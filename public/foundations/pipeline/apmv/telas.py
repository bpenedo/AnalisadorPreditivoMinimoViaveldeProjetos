# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Telas PNG do GPS preditivo — prova visual para os READMEs (D21).

Paleta e regras: método dataviz (paleta de referência validada). Categórica em ordem
fixa; sequencial em uma só matiz (azul); divergente azul↔vermelho com meio cinza;
cores de status reservadas ao semáforo e sempre acompanhadas de rótulo. Um eixo por
gráfico, marcas finas, grade recessiva, texto sempre em tinta neutra.
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .indicadores import DIMENSOES  # noqa: E402
from .mcdm import METODOS  # noqa: E402
from .tokens import FASES, PRECOS, formatar_tokens  # noqa: E402

SUPERFICIE, PLANO = "#fcfcfb", "#f9f9f7"
TINTA, TINTA2, MUDO = "#0b0b0b", "#52514e", "#898781"
GRADE, EIXO = "#e1e0d9", "#c3c2b7"
SERIE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
DIV_POS, DIV_NEG, DIV_MEIO = "#2a78d6", "#e34948", "#f0efec"
STATUS = {"VERDE": "#0ca30c", "VERDE-MVP": "#0ca30c", "AMARELO": "#fab219", "VERMELHO": "#d03b3b"}
ROTULO_STATUS = {"VERDE": "INVISTA", "VERDE-MVP": "INVISTA NO MVP", "AMARELO": "TESTE ANTES", "VERMELHO": "NÃO INVISTA AGORA"}
ICONE_STATUS = {"VERDE": "✔", "VERDE-MVP": "✔", "AMARELO": "!", "VERMELHO": "✖"}
DPI = 150

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": EIXO, "axes.labelcolor": TINTA2,
    "xtick.color": MUDO, "ytick.color": MUDO, "axes.facecolor": SUPERFICIE, "figure.facecolor": PLANO,
    "axes.grid": False, "axes.spines.top": False, "axes.spines.right": False, "text.color": TINTA,
})


def _br(v: float, casas: int = 0) -> str:
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _grade(ax, eixo="x"):
    ax.grid(axis=eixo, color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)


def _assinatura(fig, titulo: str, subtitulo: str = ""):
    fig.text(0.012, 0.975, titulo, fontsize=14, fontweight="bold", color=TINTA, va="top")
    if subtitulo:
        fig.text(0.012, 0.925, subtitulo, fontsize=9.5, color=TINTA2, va="top")
    fig.text(0.988, 0.012, "Analisador Preditivo Mínimo Viável de Projetos · ProfBru © 2026",
             fontsize=7.5, color=MUDO, ha="right")


def _salvar(fig, destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=DPI, facecolor=PLANO)
    plt.close(fig)
    return destino


# ── Telas do subcomando `ideia` ──────────────────────────────────────────────
def tela_gps(r, destino: Path) -> Path:
    """Painel-síntese: semáforo + 5 números-herói (stat tiles, não gráfico)."""
    f = r.financeiro
    fig = plt.figure(figsize=(11, 4.2))
    _assinatura(fig, "GPS preditivo — antes do 1º token", f"Ideia: {r.texto[:110]}{'…' if len(r.texto) > 110 else ''}")
    cor = STATUS[r.semaforo]
    ax = fig.add_axes([0.012, 0.10, 0.27, 0.72])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=SUPERFICIE, ec=GRADE, lw=1, transform=ax.transAxes))
    ax.add_patch(plt.Circle((0.17, 0.62), 0.11, color=cor, transform=ax.transAxes))
    ax.text(0.17, 0.62, ICONE_STATUS[r.semaforo], color="white", fontsize=22, ha="center", va="center",
            fontweight="bold", transform=ax.transAxes)
    ax.text(0.34, 0.66, ROTULO_STATUS[r.semaforo], fontsize=15, fontweight="bold", va="center", transform=ax.transAxes)
    ax.text(0.34, 0.52, f"rota {r.rota_recomendada} · {r.decisao.veredito_robustez}", fontsize=10, color=TINTA2,
            va="center", transform=ax.transAxes)
    rota = next(x for x in f.rotas if x.codigo == r.rota_recomendada)
    ax.text(0.06, 0.30, textwrap.fill(rota.nome, 46), fontsize=8.6, color=TINTA2, va="top", transform=ax.transAxes)
    tiles = [
        ("p(viável)", f"{r.previsao.p_viavel:.0%}", f"IC80 {r.previsao.ic80[0]:.0%}–{r.previsao.ic80[1]:.0%}\nprior {r.previsao.prior:.0%}"),
        ("Tokens P50 / P90", f"{formatar_tokens(r.tokens.quantis['total']['p50'])}", f"P90 {formatar_tokens(r.tokens.quantis['total']['p90'])} · 3 fases"),
        ("Construir P50", f"R$ {_br(f.custo_total['p50'])}", f"P90 R$ {_br(f.custo_total['p90'])}"),
        ("VPL esperado", f"R$ {_br(f.vpl_esperado)}", f"p* {f.p_breakeven:.0%}\nmargem {_br(f.margem_seguranca, 2)}×"),
        ("EVPI (testar antes)", f"R$ {_br(f.evpi)}", f"teste custa R$ {_br(f.custo_experimento)}"),
    ]
    for i, (rot, val, sub) in enumerate(tiles):
        x0 = 0.30 + i * 0.138
        a = fig.add_axes([x0, 0.10, 0.128, 0.72])
        a.axis("off")
        a.add_patch(plt.Rectangle((0, 0), 1, 1, color=SUPERFICIE, ec=GRADE, lw=1, transform=a.transAxes))
        a.text(0.08, 0.86, rot, fontsize=8.6, color=TINTA2, transform=a.transAxes)
        a.text(0.08, 0.52, val, fontsize=17 if len(val) < 9 else 13.5, fontweight="bold", transform=a.transAxes)
        a.text(0.08, 0.18, sub, fontsize=7.4, color=MUDO, transform=a.transAxes, wrap=True)
    return _salvar(fig, destino)


def tela_tokens(r, destino: Path) -> Path:
    """Intervalo P10–P90 por fase (escala log) + custo por modelo."""
    e = r.tokens
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(top=0.78, bottom=0.21, left=0.13, right=0.97, wspace=0.42)
    _assinatura(fig, "Quantos tokens custa estruturar, planejar e codificar",
                "Faixa P10–P90 (Monte Carlo, 200 mil amostras) e mediana P50 · custo por modelo Claude")
    nomes = list(FASES) + ["total"]
    rot = ["Estruturar", "Planejar", "Codificar", "Total"]
    for i, fz in enumerate(nomes):
        q = e.quantis[fz]
        cor = SEQ[5] if fz == "total" else SERIE[0]
        a1.plot([q["p10"], q["p90"]], [i, i], color=cor, lw=6, solid_capstyle="round", alpha=0.35)
        a1.plot(q["p50"], i, "o", color=cor, ms=9, mec=SUPERFICIE, mew=2)
        a1.text(q["p90"] * 1.15, i, f"P50 {formatar_tokens(q['p50'])} · P90 {formatar_tokens(q['p90'])}", va="center",
                fontsize=8.4, color=TINTA2)
    a1.set_xscale("log")
    a1.set_yticks(range(len(rot)), rot)
    a1.invert_yaxis()
    a1.set_xlim(min(e.quantis[f]["p10"] for f in nomes) * 0.6, e.quantis["total"]["p90"] * 9)
    a1.set_xlabel("tokens (escala log)")
    _grade(a1)
    modelos = list(PRECOS)
    p50 = [e.custo_usd[m]["p50"] for m in modelos]
    p90 = [e.custo_usd[m]["p90"] for m in modelos]
    y = np.arange(len(modelos))
    a2.barh(y, p50, color=SERIE[0], height=0.55)
    a2.errorbar(p50, y, xerr=[np.zeros(len(y)), np.array(p90) - np.array(p50)], fmt="none", ecolor=MUDO, capsize=3, lw=1)
    for yi, v, w in zip(y, p50, p90):
        a2.text(w * 1.04, yi, f"US$ {_br(v, 2)} (P90 {_br(w, 0)})", va="center", fontsize=8.2, color=TINTA2)
    a2.set_yticks(y, [PRECOS[m]["rotulo"] for m in modelos])
    a2.invert_yaxis()
    a2.set_xlim(0, max(p90) * 1.75)
    a2.set_xlabel("US$ — todas as fases no mesmo modelo")
    _grade(a2)
    return _salvar(fig, destino)


def tela_rotas(r, destino: Path) -> Path:
    """Valor esperado por rota (divergente em torno de zero) + robustez do consenso."""
    f, d = r.financeiro, r.decisao
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
    fig.subplots_adjust(top=0.78, bottom=0.21, left=0.24, right=0.97, wspace=0.55)
    _assinatura(fig, "Escolher e renunciar: as rotas de alocação do capital-token",
                "Valor esperado em R$ (VPL já descontado pelo CDI) · % de " + _br(d.n_iter) + " universos de pesos em que a rota vence")
    cod = [x.codigo for x in f.rotas]
    ev = [x.valor_esperado for x in f.rotas]
    nomes = [f"{x.codigo} · {x.nome[:26]}{'…' if len(x.nome) > 26 else ''}" for x in f.rotas]
    y = np.arange(len(cod))
    a1.barh(y, ev, color=[DIV_POS if v >= 0 else DIV_NEG for v in ev], height=0.55)
    a1.axvline(0, color=EIXO, lw=1)
    for yi, v in zip(y, ev):
        a1.text(v + (max(map(abs, ev)) * 0.03 * (1 if v >= 0 else -1)), yi, f"R$ {_br(v)}", va="center",
                ha="left" if v >= 0 else "right", fontsize=8.4, color=TINTA2)
    a1.set_yticks(y, nomes, fontsize=8.6)
    a1.invert_yaxis()
    lim = max(map(abs, ev)) * 1.45 or 1
    a1.set_xlim(-lim if min(ev) < 0 else -lim * 0.15, lim)
    a1.set_xlabel("valor esperado (R$)")
    _grade(a1)
    pv = [d.prob_vitoria.get(c, 0) for c in cod]
    a2.barh(y, pv, color=[SERIE[0] if c == r.rota_recomendada else SEQ[1] for c in cod], height=0.55)
    for yi, v in zip(y, pv):
        a2.text(v + 2, yi, f"{_br(v, 1)}%", va="center", fontsize=8.4, color=TINTA2)
    a2.set_yticks(y, cod)
    a2.invert_yaxis()
    a2.set_xlim(0, 115)
    a2.set_xlabel(f"vence em % dos universos · veredito {d.veredito_robustez}")
    _grade(a2)
    return _salvar(fig, destino)


def tela_escolas(r, destino: Path) -> Path:
    """Heatmap das posições (1 = melhor) de cada rota em cada uma das 9 escolas."""
    d = r.decisao
    M = np.array([[sorted(d.scores[m], reverse=True).index(v) + 1 for v in d.scores[m]] for m in METODOS])
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    fig.subplots_adjust(top=0.80, bottom=0.08, left=0.2, right=0.97)
    _assinatura(fig, "O voto das nove escolas multicritério", "Posição de cada rota (1 = melhor) · cor mais escura = melhor posição")
    n = len(d.alternativas)
    cores = [SEQ[min(6, int(round((n - v) / max(n - 1, 1) * 6)))] for v in M.ravel()]
    for (i, j), cor in zip(np.ndindex(M.shape), cores):
        ax.add_patch(plt.Rectangle((j, i), 0.94, 0.9, color=cor))
        ax.text(j + 0.47, i + 0.45, f"{M[i, j]}º", ha="center", va="center", fontsize=10,
                color="white" if M[i, j] <= max(1, n // 2) else TINTA)
    ax.set_xlim(0, n)
    ax.set_ylim(len(METODOS), 0)
    ax.set_xticks(np.arange(n) + 0.47, d.alternativas)
    ax.set_yticks(np.arange(len(METODOS)) + 0.45, METODOS)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    return _salvar(fig, destino)


def tela_dimensoes(r, destino: Path) -> Path:
    """Notas por dimensão (0–1) com a confiança anotada + contribuições ao log-odds."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1.2, 1]})
    fig.subplots_adjust(top=0.80, bottom=0.21, left=0.2, right=0.97, wspace=0.55)
    _assinatura(fig, "Painel de indicadores e o que moveu a probabilidade",
                f"Nota por dimensão (0,5 = neutro) · Δ log-odds sobre o prior da classe ({r.previsao.prior:.0%} → {r.previsao.p_viavel:.0%})")
    dims = list(r.dimensoes)
    notas = [r.dimensoes[x]["nota"] for x in dims]
    conf = [r.dimensoes[x]["confianca"] for x in dims]
    y = np.arange(len(dims))
    a1.barh(y, notas, color=SERIE[0], height=0.6)
    a1.axvline(0.5, color=MUDO, lw=1, ls="--")
    for yi, v, c in zip(y, notas, conf):
        a1.text(v + 0.015, yi, f"{_br(v, 2)}  (conf. {_br(c, 2)})", va="center", fontsize=8, color=TINTA2)
    a1.set_yticks(y, [DIMENSOES[x]["nome"] for x in dims], fontsize=8.6)
    a1.invert_yaxis()
    a1.set_xlim(0, 1.35)
    _grade(a1)
    ctr = sorted(r.previsao.contribuicoes.items(), key=lambda kv: -kv[1])
    y2 = np.arange(len(ctr))
    vals = [v for _, v in ctr]
    a2.barh(y2, vals, color=[DIV_POS if v >= 0 else DIV_NEG for v in vals], height=0.6)
    a2.axvline(0, color=EIXO, lw=1)
    for yi, v in zip(y2, vals):
        a2.text(v + (0.01 if v >= 0 else -0.01), yi, f"{'+' if v >= 0 else ''}{_br(v, 2)}", va="center",
                ha="left" if v >= 0 else "right", fontsize=8, color=TINTA2)
    a2.set_yticks(y2, [k for k, _ in ctr])
    a2.invert_yaxis()
    lim = max(map(abs, vals)) * 1.6 or 1
    a2.set_xlim(-lim, lim)
    a2.set_xlabel("Δ log-odds (azul aumenta, vermelho reduz)")
    _grade(a2)
    return _salvar(fig, destino)


def telas_ideia(r, pasta: Path) -> list[Path]:
    pasta = Path(pasta)
    return [tela_gps(r, pasta / "tela1.png"), tela_tokens(r, pasta / "tela2.png"), tela_rotas(r, pasta / "tela3.png"),
            tela_escolas(r, pasta / "tela4.png"), tela_dimensoes(r, pasta / "tela5.png")]


# ── Tela do subcomando `comparar` ────────────────────────────────────────────
def telas_comparacao(res, dec, pasta: Path) -> list[Path]:
    pasta = Path(pasta)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(top=0.78, bottom=0.21, left=0.08, right=0.97, wspace=0.3)
    _assinatura(fig, "Escolher e renunciar entre ideias",
                f"% de universos em que cada ideia vence — pesos incertos × notas incertas · veredito {dec.veredito_robustez}")
    nomes = dec.alternativas
    x = np.arange(len(nomes))
    pw = [dec.prob_vitoria.get(n, 0) for n in nomes]
    pn = [(dec.prob_vitoria_notas or {}).get(n, 0) for n in nomes]
    a1.bar(x - 0.2, pw, width=0.38, color=SERIE[0], label="pesos incertos (Dirichlet)")
    a1.bar(x + 0.2, pn, width=0.38, color=SERIE[1], label="notas incertas (σ ∝ 1 − confiança)")
    for xi, a, b in zip(x, pw, pn):
        a1.text(xi - 0.2, a + 1.5, f"{a:.0f}%", ha="center", fontsize=8, color=TINTA2)
        a1.text(xi + 0.2, b + 1.5, f"{b:.0f}%", ha="center", fontsize=8, color=TINTA2)
    a1.set_xticks(x, nomes)
    a1.set_ylim(0, 115)
    a1.legend(frameon=False, fontsize=8, loc="upper left")
    _grade(a1, "y")
    pv = [r.previsao.p_viavel for r in res]
    a2.bar(x, pv, color=[STATUS[r.semaforo] for r in res], width=0.55)
    for xi, r, v in zip(x, res, pv):
        a2.text(xi, v + 0.02, f"{v:.0%}\n{ROTULO_STATUS[r.semaforo]}", ha="center", fontsize=7.4, color=TINTA2)
    a2.set_xticks(x, nomes)
    a2.set_ylim(0, 1.0)
    a2.set_ylabel("p(viável)")
    _grade(a2, "y")
    legenda = "  ·  ".join(f"{n}: {r.texto[:38]}{'…' if len(r.texto) > 38 else ''}" for n, r in zip(nomes, res))
    fig.text(0.012, 0.075, legenda, fontsize=7.2, color=TINTA2)
    return [_salvar(fig, pasta / "tela1.png")]


# ── Tela do subcomando `repo` ────────────────────────────────────────────────
def tela_repo(info, destino: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 4.2))
    fig.subplots_adjust(top=0.76, bottom=0.21, left=0.16, right=0.97)
    _assinatura(fig, f"Código existente: {info.nome}",
                f"{info.trl} · maturidade {info.maturidade:.0%} · licença {info.licenca} · "
                f"testes {'sim' if info.tem_testes else 'não'} · CI {'sim' if info.tem_ci else 'não'}")
    itens = list(info.loc_por_linguagem.items())[:7]
    y = np.arange(len(itens))
    ax.barh(y, [v for _, v in itens], color=SERIE[0], height=0.55)
    for yi, (_, v) in zip(y, itens):
        ax.text(v * 1.01, yi, _br(v), va="center", fontsize=8.4, color=TINTA2)
    ax.set_yticks(y, [k for k, _ in itens])
    ax.invert_yaxis()
    ax.set_xlabel("linhas de código não vazias")
    _grade(ax)
    return _salvar(fig, destino)


# ── Tela de terminal (subcomandos de texto: indicadores, prompt) ────────────
_EMOJI = re.compile("[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F\u2B50\u2B55]")
_TROCA_EMOJI = {"💵": "$", "👤": "*", "📐": "#", "🧭": ">", "✅": "[ok]", "❌": "[x]", "⚠️": "[!]", "📦": "#", "■": "■"}


def _sem_emoji(t: str) -> str:
    """DejaVu Sans Mono não tem glifos de emoji: troca por marcador ASCII (BUG-012)."""
    for k, v in _TROCA_EMOJI.items():
        t = t.replace(k, v)
    return _EMOJI.sub("", t)


def tela_terminal(texto: str, titulo: str, destino: Path, max_linhas: int = 34) -> Path:
    linhas = _sem_emoji(texto).splitlines()[:max_linhas]
    alt = 0.9 + 0.205 * len(linhas)
    fig = plt.figure(figsize=(11, alt))
    fig.patch.set_facecolor("#1a1a19")
    fig.text(0.015, 1 - 0.32 / alt, "●  ●  ●   " + titulo, color="#c3c2b7", fontsize=9, family="DejaVu Sans Mono", va="top")
    for i, ln in enumerate(linhas):
        fig.text(0.015, 1 - (0.75 + 0.205 * i) / alt, ln[:150], color="#ffffff" if not ln.startswith("   ") else "#c3c2b7",
                 fontsize=7.8, family="DejaVu Sans Mono", va="top")
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=DPI, facecolor="#1a1a19")
    plt.close(fig)
    return destino
