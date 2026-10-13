# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""A decisão: nove escolas multicritério votam na ROTA de investimento de tokens.

Uma ideia isolada não tem "concorrentes" para ranquear — mas a DECISÃO tem
alternativas: não investir (CDI), testar antes, MVP enxuto, projeto completo ou
reaproveitar código. Cada rota é avaliada em 8 critérios e as 9 escolas do
MCDM Studio (ELECTRE I/II, PROMETHEE II, MAUT, MCDA-C, AHP-TOPSIS 2n, VIKOR,
TODIM, SAPEVO-M) votam; o consenso de Borda escolhe; 2.000 universos de pesos
(Dirichlet) dizem se a escolha é ROBUSTA, PROVÁVEL ou FRÁGIL.

Por que várias escolas (KB-OUTRANK): MAUT compensa tudo; ELECTRE veta o desastre;
TODIM pesa a perda mais que o ganho (Kahneman & Tversky); VIKOR recusa compensar o
pior critério. Para quem vai gastar dinheiro numa ideia não validada, a
concordância entre teorias independentes é a evidência mais forte disponível.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .mcdm import CONSENSO, METODOS, classificar, preparar, resumir, simular
from .mcdm.nucleo import borda, ranks

CRITERIOS_ROTA = (
    # (nome, direção, peso)
    ("Valor esperado (VPL vs CDI)", "benefit", 0.22),
    ("Capital comprometido", "cost", 0.10),
    ("Probabilidade de perda total", "cost", 0.14),
    ("Tempo até a 1ª evidência", "cost", 0.10),
    ("Reversibilidade / cumulatividade", "benefit", 0.12),
    ("Opcionalidade (direito de parar)", "benefit", 0.10),
    ("Exposição à cauda de tokens (P90)", "cost", 0.10),
    ("Durabilidade × escalabilidade engajadas", "benefit", 0.12),
)
OPCIONALIDADE = {"A0": 0.5, "A1": 1.0, "A2": 0.8, "A3": 0.1, "A4": 0.6}
ENGAJAMENTO = {"A0": 0.0, "A1": 0.3, "A2": 0.7, "A3": 1.0, "A4": 0.9}
EXPOSICAO = {"A0": 0.0, "A1": 0.0, "A2": 0.35, "A3": 1.0}


@dataclass
class ResultadoDecisao:
    alternativas: list[str]
    criterios: list[str]
    matriz: np.ndarray
    pesos: np.ndarray
    scores: dict[str, list[float]]      # método -> score por alternativa
    ranking_consenso: list[str]
    lider: str
    prob_lider: float
    veredito_robustez: str
    prob_vitoria: dict[str, float]      # alternativa -> % de universos em que vence (consenso)
    sensibilidade: dict[str, str]       # cenário -> líder
    prob_vitoria_notas: dict[str, float] | None = None   # robustez à INCERTEZA DAS NOTAS
    n_iter: int = 2000                                   # universos de pesos simulados


def _rodar(X, direcoes, w, alternativas, n_iter, semente) -> tuple[dict, list[str], dict[str, float]]:
    prep = preparar(X, direcoes)
    sc = {k: np.asarray(v, dtype=float) for k, v in prep.pontuar(w).items()}
    mr = np.vstack([ranks(sc[m]) for m in METODOS])
    cons = borda(mr, len(alternativas))
    ordem = [alternativas[i] for i in np.argsort(-cons, kind="stable")]
    pos = simular(X, direcoes, w, n_iter=n_iter, semente=semente)
    pv = {r["alternativa"]: r["prob_vitoria"] for r in resumir(pos, alternativas) if r["metodo"] == CONSENSO}
    return {k: v.tolist() for k, v in sc.items()}, ordem, pv


def decidir_rotas(fin, est, dims: dict, n_iter: int = 2000, semente: int = 42) -> ResultadoDecisao:
    """Monta a matriz rotas × critérios e roda as 9 escolas + robustez."""
    p90 = fin.custo_total["p90"]
    duresc = np.mean([dims[d]["nota"] for d in ("DUR", "ESC", "CUM") if d in dims])
    linhas, nomes = [], []
    for r in fin.rotas:
        # A4 expõe à cauda na proporção do que ainda precisa ser escrito.
        exp = EXPOSICAO[r.codigo] if r.codigo in EXPOSICAO else r.custo / max(fin.custo_total["p50"], 1)
        linhas.append([
            r.valor_esperado,
            r.custo,
            r.p_perda_total,
            r.tempo_ate_evidencia_dias,
            r.reversibilidade,
            OPCIONALIDADE[r.codigo],
            exp * p90,
            duresc * ENGAJAMENTO[r.codigo],
        ])
        nomes.append(r.codigo)
    X = np.asarray(linhas, dtype=float)
    # Desempate mínimo: colunas constantes quebram normalizações min-max.
    X += np.arange(X.shape[0])[:, None] * 1e-9
    direcoes = [c[1] for c in CRITERIOS_ROTA]
    w = np.array([c[2] for c in CRITERIOS_ROTA])
    w = w / w.sum()
    scores, ordem, pv = _rodar(X, direcoes, w, nomes, n_iter, semente)
    lider = ordem[0]
    # Sensibilidade pedida no meta-prompt da KB: durabilidade/cumulatividade 2× mais importantes.
    sens = {}
    for rot, idx in (("cumulatividade 2×", [4]), ("durabilidade 2×", [7]), ("aversão a perda 2×", [2, 6])):
        w2 = w.copy()
        w2[idx] *= 2
        w2 /= w2.sum()
        prep = preparar(X, direcoes)
        mr = np.vstack([ranks(np.asarray(v, float)) for v in prep.pontuar(w2).values()])
        sens[rot] = nomes[int(np.argmax(borda(mr, len(nomes))))]
    return ResultadoDecisao(nomes, [c[0] for c in CRITERIOS_ROTA], X, w, scores, ordem, lider,
                            pv.get(lider, 0.0), classificar(pv.get(lider, 0.0)), pv, sens, None, n_iter)


def decidir_ideias(resultados: list, n_iter: int = 2000, semente: int = 42) -> ResultadoDecisao:
    """Modo comparação: as IDEIAS são as alternativas; critérios = dimensões + economia."""
    # Critérios SEM sobreposição (BUG-011): p_viável é função das dimensões — usar as
    # duas contaria a mesma evidência duas vezes. Entram as dimensões (com os pesos do
    # catálogo), o prior da classe (outside view, informação que as dimensões não têm)
    # e o custo P90 (cauda de capital em risco).
    from .indicadores import DIMENSOES
    dims_usadas = ["DEM", "MER", "TEC", "ECO", "DUR", "ESC", "CUM", "ROB", "ALI"]
    crit = [(d, "benefit", DIMENSOES[d]["peso"]) for d in dims_usadas] + [
        ("Prior da classe de referência", "benefit", 0.10), ("Custo P90 de construir", "cost", 0.08)]
    nomes, linhas = [], []
    for i, r in enumerate(resultados):
        nomes.append(f"I{i + 1}")
        linhas.append([r.dimensoes[d]["nota"] for d in dims_usadas] +
                      [r.previsao.prior, r.financeiro.custo_total["p90"]])
    X = np.asarray(linhas, float) + np.arange(len(linhas))[:, None] * 1e-9
    direcoes = [c[1] for c in crit]
    w = np.array([c[2] for c in crit], float)
    w /= w.sum()
    scores, ordem, pv = _rodar(X, direcoes, w, nomes, n_iter, semente)
    # Segunda camada de robustez (SMAA — Lahdelma et al., 1998): as NOTAS também são incertas. Cada nota de dimensão
    # recebe ruído normal com σ = 0,15·(1 − confiança), e o prior σ = 0,25·prior.
    # Robustez só aos pesos (Dirichlet) mede a calibração do decisor; esta mede a
    # ignorância sobre a ideia — e é a que costuma derrubar "vencedores" de texto curto.
    rng = np.random.default_rng(semente)
    sig = np.array([[0.15 * (1 - r.dimensoes[d]["confianca"]) for d in dims_usadas] +
                    [0.25 * r.previsao.prior, 0.0] for r in resultados])
    vitorias = np.zeros(len(nomes))
    n_notas = max(200, n_iter // 5)
    for _ in range(n_notas):
        Xp = X + rng.standard_normal(X.shape) * sig
        Xp[:, :-1] = np.clip(Xp[:, :-1], 0.0, 1.0)
        prep = preparar(Xp, direcoes)
        mr = np.vstack([ranks(np.asarray(v, float)) for v in prep.pontuar(w).values()])
        vitorias[int(np.argmax(borda(mr, len(nomes))))] += 1
    pvn = {n: float(v / n_notas * 100) for n, v in zip(nomes, vitorias)}
    return ResultadoDecisao(nomes, [c[0] for c in crit], X, w, scores, ordem, ordem[0],
                            pv.get(ordem[0], 0.0), classificar(min(pv.get(ordem[0], 0.0), pvn.get(ordem[0], 0.0))),
                            pv, {}, pvn, n_iter)
