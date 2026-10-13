#!/usr/bin/env python3
# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Testes do analisador (Passada 1 da tripla-checagem).

Três famílias:
  • INVARIANTES — o que precisa ser verdade para qualquer ideia (EVPI ≥ 0, p ∈ (0,1),
    custo P10 ≤ P50 ≤ P90, determinismo, serial = paralelo);
  • FUNDAMENTAÇÃO — todo indicador cita fonte existente na bibliografia (diretriz
    "fronteira da ciência": indicador sem fonte não entra);
  • REGRESSÃO — um teste por bug do bugs.md, para que ele não volte.
Roda sem pytest: `python3 testes_apmv.py` (código de saída ≠ 0 se algo falhar).
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

from apmv import gps, indicadores, referencias, tokens
from apmv.extrator import extrair
from apmv.preditivo import prever

CLINICA = ("Sistema para clínicas odontológicas que perdem pacientes por falta de lembrete; envia lembretes diários "
           "pelo WhatsApp e cobra assinatura mensal; já tenho 3 clínicas interessadas, sou dentista")
TESTES = []


def teste(f):
    TESTES.append(f)
    return f


# ── Fundamentação ────────────────────────────────────────────────────────────
@teste
def todo_indicador_tem_fonte_valida():
    for i in indicadores.CATALOGO:
        assert i.fontes, f"{i.id} sem fonte"
        faltam = referencias.validar(list(i.fontes))
        assert not faltam, f"{i.id} cita fontes inexistentes: {faltam}"


@teste
def literatura_recente_presente():
    anos = [r["cit"] for r in referencias.REFERENCIAS.values()]
    recentes = sum(any(a in c for a in ("2024", "2025", "2026")) for c in anos)
    assert recentes >= 12, f"só {recentes} referências de 2024–2026 — a fronteira precisa estar representada"


@teste
def ids_de_indicador_unicos_e_dimensoes_validas():
    ids = [i.id for i in indicadores.CATALOGO]
    assert len(ids) == len(set(ids))
    assert all(i.dimensao in indicadores.DIMENSOES for i in indicadores.CATALOGO)


# ── Invariantes ──────────────────────────────────────────────────────────────
@teste
def quantis_ordenados_e_custos_positivos():
    e = tokens.estimar(extrair(CLINICA), n=20_000)
    for f in tokens.FASES + ("total",):
        q = e.quantis[f]
        assert 0 < q["p10"] <= q["p50"] <= q["p90"], f
    for m, c in e.custo_usd.items():
        assert 0 < c["p10"] <= c["p50"] <= c["p90"], m
    # preço: Fable 5.1 > Opus 5.5 > Sonnet 5.5 > Haiku 4.5 para o mesmo volume
    c = [e.custo_usd[m]["p50"] for m in ("claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-4-5")]
    assert c == sorted(c, reverse=True)


@teste
def entrada_domina_o_custo():
    """Bai et al. (2026): em tarefas agênticas, tokens de entrada dominam."""
    e = tokens.estimar(extrair(CLINICA), n=5_000)
    assert e.fracao_entrada > 0.85


@teste
def determinismo():
    a = gps.analisar_ideia(CLINICA, n_iter=300)
    b = gps.analisar_ideia(CLINICA, n_iter=300)
    assert a.previsao.p_viavel == b.previsao.p_viavel
    assert a.tokens.quantis == b.tokens.quantis
    assert a.decisao.prob_vitoria == b.decisao.prob_vitoria


@teste
def evpi_nao_negativo_e_probabilidades_validas():
    for t in (CLINICA, "uma ideia legal", "Robô de arbitragem de cripto", "Marketplace de passeadores de cães"):
        r = gps.analisar_ideia(t, n_iter=200)
        assert r.financeiro.evpi >= -1e-9, t
        assert 0 < r.previsao.p_viavel < 1
        assert r.previsao.ic80[0] <= r.previsao.p_viavel <= r.previsao.ic80[1] + 0.05
        assert 0 <= r.financeiro.p_breakeven <= 1


@teste
def validacao_aumenta_probabilidade():
    """Monotonicidade: acrescentar evidência de demanda não pode REDUZIR p."""
    base = "App para clínicas agendarem consultas"
    s0, s1 = extrair(base), extrair(base + "; já tenho clientes pagantes em piloto")
    e0, e1 = tokens.estimar(s0, n=2000), tokens.estimar(s1, n=2000)
    p0 = prever(indicadores.medir_qualitativos(s0, e0.tamanho), s0).p_viavel
    p1 = prever(indicadores.medir_qualitativos(s1, e1.tamanho), s1).p_viavel
    assert p1 > p0, (p0, p1)


@teste
def ideia_vaga_nunca_recebe_verde():
    r = gps.analisar_ideia("uma ideia legal", n_iter=300)
    assert not r.semaforo.startswith("VERDE"), r.semaforo


@teste
def serial_igual_paralelo():
    ideias = ["Automatizar conciliação bancária do escritório", "Curso online de Excel com assinatura mensal",
              "Marketplace de passeadores de cães"]
    a, da = gps.comparar_ideias(ideias, n_iter=200, workers=1)
    b, db = gps.comparar_ideias(ideias, n_iter=200, workers=3)
    assert [x.previsao.p_viavel for x in a] == [x.previsao.p_viavel for x in b]
    assert da.prob_vitoria == db.prob_vitoria and da.prob_vitoria_notas == db.prob_vitoria_notas


@teste
def motor_mcdm_vendorizado_fiel():
    """O núcleo das 9 escolas é cópia fiel do MCDM Studio (só imports relativos mudam)."""
    origem = Path("/home/c7g/devparetoprojects/multicriteriadecisionmodels/public/foundations/pipeline")
    if not origem.exists():
        return
    for nome in ("nucleo.py", "metodos_br.py", "robustez.py"):
        a = (origem / nome).read_text(encoding="utf-8").replace("from config import", "from .config_mcdm import")
        a = a.replace("from nucleo import", "from .nucleo import").replace("from metodos_br import", "from .metodos_br import")
        b = (Path(__file__).parent / "apmv" / "mcdm" / nome).read_text(encoding="utf-8")
        assert a == b, f"{nome} divergiu da fonte — ressincronize"


# ── Regressões (bugs.md) ─────────────────────────────────────────────────────
@teste
def bug_001_validacao_e_competencia_reconhecidas():
    s = extrair("já tenho 3 clínicas interessadas, sou dentista")
    assert s.tem("validacao") and s.tem("competencia")


@teste
def bug_002_evidencia_sem_pontuacao():
    s = extrair("cobra assinatura mensal; todo dia")
    assert all(not x.endswith((";", ",", ".")) for v in s.evidencias.values() for x in v)


@teste
def bug_003_assinatura_nao_e_funcionalidade():
    assert "assinatura" not in extrair("cobra assinatura mensal").funcionalidades


@teste
def bug_004_arbitragem_responde_como_ganha_dinheiro():
    assert "como se ganha dinheiro" not in extrair("Robô de arbitragem de cripto").lacunas


@teste
def bug_005_flexao_nao_duplica_funcionalidade():
    assert extrair("envia lembrete e lembretes").n_funcionalidades == 2


@teste
def bug_006_custo_de_operar_entra_no_break_even():
    r = gps.analisar_ideia("Marketplace que conecta passeadores de cães a donos de pets", n_iter=200)
    assert r.financeiro.custo_operar > 0
    assert r.financeiro.p_breakeven > 0.2      # antes do conserto ficava ~1%


@teste
def bug_009_decimal_ptbr_no_relatorio():
    from apmv import relatorio
    md = relatorio.markdown(gps.analisar_ideia(CLINICA, n_iter=200))
    assert "vence em" in md and not any(f"{d}.{e}%" in md for d in range(10) for e in range(10))


@teste
def bug_009b_evidencias_economicas_em_ptbr():
    import re
    r = gps.analisar_ideia(CLINICA, n_iter=200)
    for k in ("ECO-01", "ECO-02", "ECO-03", "ECO-04", "ECO-07", "ROB-04", "INF-03"):
        ev = r.medidas[k].evidencia
        # ponto seguido de 1–2 dígitos = decimal no formato inglês (milhar tem 3 dígitos)
        assert not re.search(r"\d\.\d{1,2}(?!\d)", ev), (k, ev)


@teste
def bug_010_evidencia_multipalavra():
    assert "sou dentista" in extrair("sou dentista").evidencias["competencia"]


@teste
def bug_011_comparacao_sem_dupla_contagem():
    from apmv import decisao
    import inspect
    src = inspect.getsource(decisao.decidir_ideias)
    assert "p_viavel" not in src.split("linhas.append")[1].split(")")[0]


@teste
def bug_012_terminal_sem_emoji():
    from apmv.telas import _sem_emoji
    assert _sem_emoji("💵 US$ ✅ ok 🧭").strip() == "$ US$ [ok] ok >"


@teste
def bug_014_rotulo_de_universos_reflete_iter():
    from apmv import relatorio
    md = relatorio.markdown(gps.analisar_ideia("uma ideia legal", n_iter=300))
    assert "(300 universos de pesos)" in md


@teste
def utilidade_marginal_decrescente_na_fronteira():
    """Gossen: na fronteira eficiente a utilidade marginal nunca cresce."""
    for t in (CLINICA, "Automatizar a conciliação bancária do escritório", "Marketplace de passeadores de cães"):
        um = list(gps.analisar_ideia(t, n_iter=200).financeiro.utilidade_marginal.values())
        assert all(a >= b - 1e-9 for a, b in zip(um, um[1:])), (t, um)


@teste
def kb_shannon_e_utilidade_marginal_no_catalogo():
    ids = {i.id for i in indicadores.CATALOGO}
    assert {"MER-02", "MER-03", "MER-04", "MER-06", "ECO-08"} <= ids


def main() -> int:
    falhas = 0
    for t in TESTES:
        try:
            t()
            print(f"  ✅ {t.__name__}")
        except Exception:  # noqa: BLE001
            falhas += 1
            print(f"  ❌ {t.__name__}")
            traceback.print_exc()
    print(f"\n{'✅' if not falhas else '❌'} {len(TESTES) - falhas}/{len(TESTES)} testes passaram")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
