# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Quantos tokens custa ESTRUTURAR, PLANEJAR e CODIFICAR a ideia — com intervalo.

Por que não um número só
------------------------
Bai et al. (2026, arXiv:2604.22750) mediram 8 LLMs de fronteira no SWE-bench
Verified: a MESMA tarefa varia até 30× em tokens entre execuções, a entrada (não a
saída) domina o custo, e os modelos não preveem o próprio consumo (r ≤ 0,39).
Flyvbjerg & Budzier (2011, HBR; 1.471 projetos de TI) acharam que 1 em cada 6
projetos é "cisne negro", com sobrecusto médio de 200%. Logo, um estimador honesto
devolve uma DISTRIBUIÇÃO: P10 / P50 / P90, e diz qual cauda está pagando.

Modelo
------
1. Tamanho funcional (Albrecht, 1979) a partir do texto: funcionalidades citadas,
   integrações, interface, tempo real, IA, hardware → nº de arquivos N.
2. Tokens por atividade (tabela do tokencast, MIT): ler/escrever/editar arquivo,
   teste, revisão, pesquisa, planejamento, turno de conversa.
3. Acúmulo de contexto por sessão: entrada × (K+1)/2, K = atividades da sessão
   (crescimento triangular do contexto — tokencast).
4. Fatores do ACEM (El-Ramly, 2026): Revision Factor (retrabalho por complexidade)
   e HITL Intensity Score (horas de supervisão humana).
5. Monte Carlo (numba): por fase, lognormal com mediana = estimativa determinística
   e σ crescente com a ignorância (completude baixa ⇒ σ maior); na fase de código,
   evento de cauda com p = 1/6 e multiplicador 1 + Pareto(α=2) (média 3×).

Todo parâmetro está nomeado aqui, com a fonte — calibrar é editar ESTE arquivo.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

try:
    from numba import njit
    NUMBA_ATIVO = True
except ImportError:  # pragma: no cover — degradação graciosa (D13)
    NUMBA_ATIVO = False

    def njit(*a, **k):
        return (lambda f: f) if not (a and callable(a[0])) else a[0]

# ── Tokens por atividade (entrada, saída) — tokencast/references/heuristics.md ──
ATIVIDADE = {
    "ler_arquivo":     (10_000, 200),
    "escrever_novo":   (1_500, 4_000),
    "editar":          (2_500, 1_500),
    "escrever_teste":  (2_000, 5_000),
    "revisao":         (8_000, 3_000),
    "pesquisa":        (5_000, 2_000),
    "planejamento":    (3_000, 4_000),
    "busca":           (500, 500),
    "shell":           (300, 500),
    "turno":           (5_000, 1_500),
}
TOKENS_POR_LINHA = 10            # ~10 tokens por linha de código (leitura de repositório)
ARQUIVOS_POR_SESSAO = 8          # sessão de codificação típica antes de compactar/reiniciar
CICLOS_REVISAO = 2               # tokencast: 2 ciclos, decaimento geométrico 0,6
DECAIMENTO_REVISAO = 0.6
TAXA_CACHE = 0.50                # tokencast: faixa esperada (otimista 0,6 · pessimista 0,3)
FRACAO_ESCRITA_CACHE = 0.10      # parcela da entrada cobrada como escrita de cache (1,25×)

# Revision Factor por nível de complexidade (ACEM) — retrabalho por rejeição/novas tentativas.
REVISION_FACTOR = {"baixa": 1.10, "media": 1.30, "alta": 1.60}
# HITL Intensity Score (ACEM, 4 níveis) → horas humanas por sessão de codificação.
HORAS_POR_SESSAO_HIS = {1: 1.5, 2: 3.0, 3: 4.5, 4: 6.0}   # revisar, testar, corrigir, integrar (BUG-008)
HORAS_ESTRUTURAR, HORAS_PLANEJAR = 2.0, 3.0

# Incerteza (σ do log) por fase; somam-se +0,6·(1 − completude).
SIGMA_FASE = {"estruturar": 0.45, "planejar": 0.45, "codificar": 0.75}
P_CAUDA = 1 / 6                  # Flyvbjerg & Budzier (2011): 1 em 6 projetos de TI é cisne negro
PARETO_ALFA = 2.0                # multiplicador de cauda 1 + Pareto(α=2, xm=1) ⇒ média 3× (sobrecusto 200%)
N_AMOSTRAS = 200_000

# Preços por milhão de tokens (US$) — tabela oficial de preços Claude, cache de 25/09/2026.
PRECOS = {
    "claude-fable-5-1":  {"rotulo": "Fable 5.1",  "in": 10.0, "out": 50.0, "cache": 0.25},
    "claude-opus-5-5":   {"rotulo": "Opus 5.5",   "in": 4.0,  "out": 20.0, "cache": 0.20},
    "claude-sonnet-5-5": {"rotulo": "Sonnet 5.5", "in": 2.0,  "out": 10.0, "cache": 0.20},
    "claude-haiku-4-5":  {"rotulo": "Haiku 4.5",  "in": 1.0,  "out": 5.0,  "cache": 0.10},
}
# Roteamento padrão: pesquisa e código no modelo de custo médio, arquitetura no mais capaz.
ROTA_MODELOS = {"estruturar": "claude-sonnet-5-5", "planejar": "claude-opus-5-5",
                "codificar": "claude-sonnet-5-5"}
FASES = ("estruturar", "planejar", "codificar")


@dataclass
class Tamanho:
    funcionalidades: int
    integracoes: int
    arquivos_novos: int
    complexidade: str
    his: int
    sessoes: int
    loc_existente: int
    maturidade_repo: float


@dataclass
class EstimativaTokens:
    tamanho: Tamanho
    deterministico: dict          # fase -> {"in":…, "out":…}
    quantis: dict                 # fase/total -> {"p10","p50","p90","media"} (tokens totais)
    custo_usd: dict               # rota/modelo -> {"p10","p50","p90"}
    horas_humanas: dict           # {"p50","p90"}
    fracao_entrada: float
    cauda_p90_sobre_p50: float

    def como_dict(self) -> dict:
        d = asdict(self)
        d["tamanho"] = asdict(self.tamanho)
        return d


def dimensionar(sinais, repo=None) -> Tamanho:
    """Tamanho funcional e complexidade a partir dos sinais (e do repositório, se houver)."""
    c = sinais.contagens
    f = max(sinais.classe.funcionalidades_base, sinais.n_funcionalidades)
    integ = min(c.get("integracao", 0), 6)
    n = 3 + 2 * f + 2 * integ
    n += 6 if (c.get("ui", 0) or c.get("b2c", 0)) else 0
    n += 4 if c.get("tempo_real", 0) else 0
    n += 3 if c.get("ia", 0) else 0
    n += 4 if c.get("hardware", 0) else 0
    n += 3 if c.get("arbitragem", 0) else 0          # backtest + execução + gestão de risco
    pontos = sum(bool(c.get(s, 0)) for s in ("tempo_real", "regulado", "rede", "hardware", "arbitragem")) \
        + (integ >= 3) + (f >= 10)
    complexidade = "baixa" if pontos == 0 and f <= 5 else ("alta" if pontos >= 3 else "media")
    his = 1 + (complexidade != "baixa") + (complexidade == "alta") + bool(c.get("regulado", 0) or c.get("arbitragem", 0))
    his = min(his, 4)
    loc, mat = 0, 0.0
    if repo is not None:
        loc, mat = repo.loc_total, repo.maturidade
        n = max(2, int(round(n * (1 - mat))))         # o que já existe não precisa ser escrito
    sessoes = max(1, -(-n // ARQUIVOS_POR_SESSAO))
    return Tamanho(f, integ, n, complexidade, his, sessoes, loc, mat)


def _somar(atividades: dict[str, float]) -> tuple[float, float]:
    ent = sum(ATIVIDADE[a][0] * q for a, q in atividades.items())
    sai = sum(ATIVIDADE[a][1] * q for a, q in atividades.items())
    return ent, sai


def _sessao(atividades: dict[str, float]) -> tuple[float, float]:
    """Uma sessão com acúmulo de contexto triangular: entrada × (K+1)/2."""
    ent, sai = _somar(atividades)
    k = sum(atividades.values())
    return ent * (k + 1) / 2, sai


def deterministico(t: Tamanho, sinais) -> dict:
    """Estimativa central (mediana) de entrada/saída por fase."""
    rf = REVISION_FACTOR[t.complexidade]
    leitura_repo = min(t.loc_existente * TOKENS_POR_LINHA, 400_000)
    # 1 · ESTRUTURAR — pesquisa de mercado, KB, refinamento da ideia, benchmark.
    e_in, e_out = _sessao({"pesquisa": 6 + 2 * (1 - sinais.completude) * 3, "busca": 8,
                           "planejamento": 1, "turno": 4, "ler_arquivo": 2})
    e_in += leitura_repo
    # 2 · PLANEJAR — arquitetura, decomposição em tarefas, revisão do plano.
    p_in, p_out = _sessao({"planejamento": 3, "revisao": 2, "turno": 4,
                           "ler_arquivo": 4 + min(t.funcionalidades, 10) / 2})
    p_in += leitura_repo * 0.5
    # 3 · CODIFICAR — sessões de ~8 arquivos: escrever, reler, editar ×RF, testar, QA.
    c_in = c_out = 0.0
    restantes = t.arquivos_novos
    for _ in range(t.sessoes):
        n = min(ARQUIVOS_POR_SESSAO, restantes)
        restantes -= n
        i, o = _sessao({"escrever_novo": n, "ler_arquivo": 0.5 * n, "editar": 1.5 * n * rf,
                        "escrever_teste": 0.5 * n, "shell": 3 + n, "turno": 4})
        c_in += i
        c_out += o
    # Revisão de PR com decaimento geométrico (tokencast).
    r_in, r_out = _somar({"revisao": 1, "planejamento": 1})
    fator = (1 - DECAIMENTO_REVISAO ** CICLOS_REVISAO) / (1 - DECAIMENTO_REVISAO) * t.sessoes
    c_in += r_in * fator
    c_out += r_out * fator
    return {"estruturar": {"in": e_in, "out": e_out},
            "planejar": {"in": p_in, "out": p_out},
            "codificar": {"in": c_in, "out": c_out}}


@njit(cache=True)
def _monte_carlo(medianas, sigmas, idx_codigo, p_cauda, alfa, n, semente):
    """Amostras de tokens por fase (n × fases) + total. Kernel numba (D13)."""
    np.random.seed(semente)
    nf = medianas.shape[0]
    saida = np.empty((n, nf + 1))
    for i in range(n):
        tot = 0.0
        for f in range(nf):
            v = medianas[f] * np.exp(sigmas[f] * np.random.standard_normal())
            if f == idx_codigo and np.random.random() < p_cauda:
                # Pareto(α, xm=1) por inversão: (1 − U)^(−1/α)
                v *= 1.0 + (1.0 - np.random.random()) ** (-1.0 / alfa)
            saida[i, f] = v
            tot += v
        saida[i, nf] = tot
    return saida


def _custo(ent, sai, modelo, taxa_cache=TAXA_CACHE) -> float:
    p = PRECOS[modelo]
    em_cache = ent * taxa_cache
    escrita = ent * FRACAO_ESCRITA_CACHE
    normal = max(ent - em_cache - escrita, 0.0)
    return (normal * p["in"] + em_cache * p["cache"] + escrita * p["in"] * 1.25 + sai * p["out"]) / 1e6


def estimar(sinais, repo=None, semente: int = 42, n: int = N_AMOSTRAS) -> EstimativaTokens:
    t = dimensionar(sinais, repo)
    det = deterministico(t, sinais)
    extra = 0.6 * (1 - sinais.completude)
    med = np.array([det[f]["in"] + det[f]["out"] for f in FASES])
    sig = np.array([SIGMA_FASE[f] + extra for f in FASES])
    am = _monte_carlo(med, sig, FASES.index("codificar"), P_CAUDA, PARETO_ALFA, n, semente)
    quantis = {}
    for j, nome in enumerate(FASES + ("total",)):
        col = am[:, j]
        quantis[nome] = {"p10": float(np.percentile(col, 10)), "p50": float(np.percentile(col, 50)),
                         "p90": float(np.percentile(col, 90)), "media": float(col.mean())}
    ent_tot = sum(det[f]["in"] for f in FASES)
    sai_tot = sum(det[f]["out"] for f in FASES)
    frac_in = ent_tot / (ent_tot + sai_tot)

    def custo_rota(q: str, modelo_unico: str | None = None) -> float:
        total = 0.0
        for f in FASES:
            escala = quantis[f][q] / (det[f]["in"] + det[f]["out"])
            m = modelo_unico or ROTA_MODELOS[f]
            total += _custo(det[f]["in"] * escala, det[f]["out"] * escala, m)
        return total

    custos = {"rota_recomendada": {q: custo_rota(q) for q in ("p10", "p50", "p90")}}
    for m in PRECOS:
        custos[m] = {q: custo_rota(q, m) for q in ("p10", "p50", "p90")}
    h_base = HORAS_ESTRUTURAR + HORAS_PLANEJAR + HORAS_POR_SESSAO_HIS[t.his] * t.sessoes
    razao = quantis["total"]["p90"] / quantis["total"]["p50"]
    return EstimativaTokens(t, det, quantis, custos,
                            {"p50": h_base, "p90": h_base * razao},
                            frac_in, razao)


def formatar_tokens(v: float) -> str:
    if v >= 1e6:
        return f"{v / 1e6:.1f} M".replace(".", ",")      # decimal PT-BR (BUG-009)
    if v >= 1e3:
        return f"{v / 1e3:.0f} mil"
    return f"{v:.0f}"


if __name__ == "__main__":
    import sys
    import time

    from .extrator import extrair
    s = extrair(" ".join(sys.argv[1:]) or "SaaS para clínicas com agenda, lembretes por WhatsApp, cobrança por Pix e painel")
    t0 = time.perf_counter()
    e = estimar(s)
    dt = time.perf_counter() - t0
    print(f"📐 {e.tamanho.arquivos_novos} arquivos · {e.tamanho.sessoes} sessões · complexidade {e.tamanho.complexidade} · HIS {e.tamanho.his}")
    for f in FASES + ("total",):
        q = e.quantis[f]
        print(f"   {f:<11} P10 {formatar_tokens(q['p10']):>9} · P50 {formatar_tokens(q['p50']):>9} · P90 {formatar_tokens(q['p90']):>9}")
    for m, c in e.custo_usd.items():
        print(f"   💵 {PRECOS.get(m, {}).get('rotulo', m):<17} P50 US$ {c['p50']:8.2f} · P90 US$ {c['p90']:8.2f}")
    print(f"   👤 horas humanas P50 {e.horas_humanas['p50']:.1f} h · P90 {e.horas_humanas['p90']:.1f} h · entrada = {e.fracao_entrada:.0%} dos tokens")
    print(f"   ⏱️  {dt:.2f}s ({N_AMOSTRAS:,} amostras, numba {'ATIVO' if NUMBA_ATIVO else 'inativo'})")
