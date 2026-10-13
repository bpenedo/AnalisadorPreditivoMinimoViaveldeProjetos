#!/usr/bin/env python3
# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""CLI do Analisador Preditivo Mínimo Viável de Projetos — o GPS antes do 1º token.

Subcomandos (cada um é uma "skill" do projeto):
  ideia        GPS completo de UMA ideia (texto livre, com ou sem repositório)
  comparar     várias ideias lado a lado — qual escolher, qual renunciar
  tokens       só a estimativa de tokens/custo por fase e por modelo
  repo         só a maturidade de um repositório (GitHub ou pasta local)
  indicadores  o catálogo de indicadores, dimensões e fontes
  prompt       o prompt-mestre pronto para aprofundar a ideia num LLM

Exemplos:
  python3 analisar.py ideia "App para clínicas lembrarem pacientes pelo WhatsApp"
  python3 analisar.py ideia "Fork deste bot" --repo https://github.com/usuario/projeto
  python3 analisar.py comparar "ideia A" "ideia B" "ideia C"
  python3 analisar.py comparar --arquivo ideias.txt       # uma ideia por linha
  python3 analisar.py tokens "SaaS de agenda com Pix e painel" --json
  python3 analisar.py ideia "..." --relatorio            # .md + .html + .pdf (OCR, marca d'água) + telas
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from apmv import financeiro, gps, relatorio, repositorio, tokens
from apmv.extrator import extrair
from apmv.indicadores import CATALOGO, DIMENSOES
from config import RAIZ, ENCODING


def _premissas(a) -> financeiro.Premissas:
    return financeiro.Premissas(cambio=a.cambio, cdi_anual=a.cdi, horizonte_meses=a.horizonte,
                                valor_hora=a.valor_hora, receita_mensal_cons=a.receita,
                                receita_mensal_otim=a.receita_otimista, capital_trading=a.capital,
                                custo_operacao_mes=a.infra_mes)


def _salvar(texto: str, destino: str | None, sufixo: str) -> None:
    if not destino:
        return
    p = Path(destino)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == "":
        p = p.with_suffix(sufixo)
    p.write_text(texto, encoding=ENCODING)
    print(f"💾 salvo em {p}", file=sys.stderr)


def _base_relatorio(a, texto: str) -> Path | None:
    """--relatorio sem valor → relatorios/<slug>_<DDMM_HHMMSS>; com valor → o caminho dado."""
    if a.relatorio is None:
        return None
    if a.relatorio != "AUTO":
        return Path(a.relatorio).with_suffix("")
    import re
    import time
    from apmv.extrator import normalizar
    slug = re.sub(r"[^a-z0-9]+", "_", normalizar(texto))[:40].strip("_") or "ideia"
    return RAIZ / "relatorios" / f"{slug}_{time.strftime('%d%m_%H%M%S')}"


def _exportar(md_texto: str, base: Path, telas_png: list, titulo: str) -> None:
    from apmv import exportar
    for fmt, caminho in exportar.exportar(md_texto, base, telas_png, titulo).items():
        print(f"📄 {fmt.upper():<4} {caminho}", file=sys.stderr)


def cmd_ideia(a) -> int:
    r = gps.analisar_ideia(a.texto, repo=a.repo, premissas=_premissas(a), n_iter=a.iter,
                           destino_clone=RAIZ / "dados" / "repos")
    saida = relatorio.json_resultado(r) if a.json else relatorio.markdown(r)
    print(saida)
    _salvar(saida, a.saida, ".json" if a.json else ".md")
    base = _base_relatorio(a, a.texto)
    pasta_telas = Path(a.telas) if a.telas else (base.parent / f"{base.name}_telas" if base else None)
    gerados = []
    if pasta_telas:
        from apmv import telas
        gerados = telas.telas_ideia(r, pasta_telas)
        for f in gerados:
            print(f"🖼️  {f}", file=sys.stderr)
    if base:
        _exportar(relatorio.markdown(r), base, gerados, f"GPS preditivo — {a.texto[:60]}")
    return 0


def cmd_comparar(a) -> int:
    ideias = list(a.textos)
    if a.arquivo:
        ideias += [x.strip() for x in Path(a.arquivo).read_text(encoding=ENCODING).splitlines() if x.strip() and not x.startswith("#")]
    if len(ideias) < 2:
        print("❌ informe pelo menos 2 ideias (argumentos ou --arquivo).", file=sys.stderr)
        return 2
    res, dec = gps.comparar_ideias(ideias, premissas=_premissas(a), n_iter=a.iter, workers=a.workers)
    md = relatorio.markdown_comparacao(res, dec)
    print(md)
    _salvar(md, a.saida, ".md")
    base = _base_relatorio(a, "comparacao " + " ".join(i[:12] for i in ideias))
    pasta_telas = Path(a.telas) if a.telas else (base.parent / f"{base.name}_telas" if base else None)
    gerados = []
    if pasta_telas:
        from apmv import telas
        gerados = telas.telas_comparacao(res, dec, pasta_telas)
        for f in gerados:
            print(f"🖼️  {f}", file=sys.stderr)
    if base:
        # O relatório de comparação leva também o GPS completo de cada ideia, em seguida.
        completo = md + "\n\n" + "\n\n---\n\n".join(relatorio.markdown(r) for r in res)
        _exportar(completo, base, gerados, "GPS preditivo — comparação de ideias")
    return 0


def cmd_tokens(a) -> int:
    s = extrair(a.texto)
    info = repositorio.analisar(a.repo, RAIZ / "dados" / "repos") if a.repo else None
    e = tokens.estimar(s, info)
    if a.json:
        import json
        print(json.dumps(e.como_dict(), ensure_ascii=False, indent=2))
        return 0
    t = e.tamanho
    print(f"📐 {t.arquivos_novos} arquivos · {t.sessoes} sessão(ões) · complexidade {t.complexidade} · HITL {t.his}/4")
    for f in tokens.FASES + ("total",):
        q = e.quantis[f]
        print(f"   {f:<11} P10 {tokens.formatar_tokens(q['p10']):>9} · P50 {tokens.formatar_tokens(q['p50']):>9} · P90 {tokens.formatar_tokens(q['p90']):>9}")
    for m, c in e.custo_usd.items():
        rot = tokens.PRECOS[m]["rotulo"] if m in tokens.PRECOS else "rota recomendada"
        print(f"   💵 {rot:<17} P50 US$ {c['p50']:9.2f} · P90 US$ {c['p90']:9.2f}")
    print(f"   👤 horas humanas P50 {e.horas_humanas['p50']:.1f} h · P90 {e.horas_humanas['p90']:.1f} h")
    return 0


def cmd_repo(a) -> int:
    info = repositorio.analisar(a.alvo, RAIZ / "dados" / "repos")
    print(f"📦 {info.nome} — {info.trl} · maturidade {info.maturidade:.0%}")
    print(f"   {info.loc_total:,} linhas em {info.arquivos_fonte} arquivos-fonte · licença {info.licenca}")
    print("   " + " · ".join(f"{k} {v:,}" for k, v in list(info.loc_por_linguagem.items())[:6]))
    print(f"   testes {'✅' if info.tem_testes else '❌'} · CI {'✅' if info.tem_ci else '❌'} · README {'✅' if info.tem_readme else '❌'}"
          + (f" · último commit há {info.dias_desde_ultimo_commit:.0f} dias" if info.dias_desde_ultimo_commit is not None else ""))
    for o in info.observacoes:
        print(f"   ⚠️  {o}")
    return 0


def cmd_indicadores(a) -> int:
    if a.bibliografia:
        print(relatorio.bibliografia_md())
        return 0
    print(f"🧭 {len(CATALOGO)} indicadores em {len(DIMENSOES)} dimensões\n")
    atual = None
    for i in CATALOGO:
        if i.dimensao != atual:
            atual = i.dimensao
            print(f"\n■ {atual} — {DIMENSOES[atual]['nome']} (peso {DIMENSOES[atual]['peso']:.0%})")
        print(f"   {i.id}  {i.nome:<48} [{i.tipo}]  {i.formula}")
        print(f"          fontes: {', '.join(i.fontes)} · evidência mínima: {i.evidencia_minima}")
    return 0


def cmd_prompt(a) -> int:
    r = gps.analisar_ideia(a.texto, n_iter=400)
    rota = next(x for x in r.financeiro.rotas if x.codigo == r.rota_recomendada)
    print(relatorio.PROMPT_MESTRE.format(
        ideia=r.texto, classe=r.sinais.classe.rotulo, p=r.previsao.p_viavel, ic0=r.previsao.ic80[0],
        ic1=r.previsao.ic80[1], t50=tokens.formatar_tokens(r.tokens.quantis["total"]["p50"]),
        t90=tokens.formatar_tokens(r.tokens.quantis["total"]["p90"]), rota=rota.nome))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="analisar.py", description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def premissas(p):
        g = p.add_argument_group("premissas financeiras")
        g.add_argument("--cambio", type=float, default=financeiro.CAMBIO_BRL, help="R$/US$ (padrão %(default)s)")
        g.add_argument("--cdi", type=float, default=financeiro.CDI_ANUAL, help="CDI a.a. em fração (padrão %(default)s)")
        g.add_argument("--horizonte", type=int, default=financeiro.HORIZONTE_MESES, help="meses (padrão %(default)s)")
        g.add_argument("--valor-hora", type=float, default=financeiro.VALOR_HORA, help="R$/h do autor (padrão %(default)s)")
        g.add_argument("--receita", type=float, default=None, help="receita mensal conservadora em R$, se souber")
        g.add_argument("--receita-otimista", type=float, default=None, help="receita mensal otimista em R$")
        g.add_argument("--capital", type=float, default=None, help="capital alocado (ideias de trading/arbitragem)")
        g.add_argument("--infra-mes", type=float, default=0.0, help="custo mensal de infraestrutura (padrão 0 — zero-cost)")
        p.add_argument("--iter", type=int, default=2000, help="universos de pesos na robustez (padrão %(default)s)")
        p.add_argument("--saida", help="arquivo para salvar o relatório")
        p.add_argument("--telas", help="diretório para salvar as telas PNG")
        p.add_argument("--relatorio", nargs="?", const="AUTO", default=None, metavar="BASE",
                       help="gera BASE.md, BASE.html e BASE.pdf (PDF em formato OCR com marca d'água); "
                            "sem valor: relatorios/<ideia>_<DDMM_HHMMSS>")

    p = sub.add_parser("ideia", help="GPS completo de uma ideia")
    p.add_argument("texto")
    p.add_argument("--repo", help="URL do GitHub ou pasta local com código existente")
    p.add_argument("--json", action="store_true")
    premissas(p)
    p.set_defaults(f=cmd_ideia)

    p = sub.add_parser("comparar", help="compara várias ideias (escolher e renunciar)")
    p.add_argument("textos", nargs="*")
    p.add_argument("--arquivo", help="arquivo com uma ideia por linha")
    p.add_argument("--workers", type=int, default=None, help="processos (padrão: nº de CPUs)")
    premissas(p)
    p.set_defaults(f=cmd_comparar)

    p = sub.add_parser("tokens", help="estimativa de tokens/custo por fase")
    p.add_argument("texto")
    p.add_argument("--repo")
    p.add_argument("--json", action="store_true")
    p.set_defaults(f=cmd_tokens)

    p = sub.add_parser("repo", help="maturidade de um repositório")
    p.add_argument("alvo")
    p.set_defaults(f=cmd_repo)

    p = sub.add_parser("indicadores", help="catálogo de indicadores e fontes")
    p.add_argument("--bibliografia", action="store_true", help="imprime a bibliografia em Markdown")
    p.set_defaults(f=cmd_indicadores)

    p = sub.add_parser("prompt", help="prompt-mestre para aprofundar num LLM")
    p.add_argument("texto")
    p.set_defaults(f=cmd_prompt)

    a = ap.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
