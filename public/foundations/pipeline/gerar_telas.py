#!/usr/bin/env python3
# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Gera as telas de exemplo de CADA skill/sub-skill (D21).

Grava em `_private/foundations/telas/<caso>/` (acervo) e copia para `docs/telas/<caso>/`
(caminho público que o README referencia — `_private/` não vai para o GitHub).
Os casos são fixos e a semente também: as telas são reprodutíveis bit a bit.
"""
from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path

from apmv import gps, telas
from config import RAIZ, TELAS_PRIVADAS, TELAS_PUBLICAS

CASOS_IDEIA = {
    "ideia_clinica": "Sistema para clínicas odontológicas que perdem pacientes por falta de lembrete; envia lembretes "
                     "diários pelo WhatsApp e cobra assinatura mensal; já tenho 3 clínicas interessadas, sou dentista",
    "ideia_conciliacao": "Automatizar a conciliação bancária manual que meu escritório de contabilidade faz todo dia em planilha",
    "ideia_arbitragem": "Robô de arbitragem de cripto entre Binance e Mercado Bitcoin",
    "ideia_vaga": "uma ideia legal",
}
COMPARAR = [
    "Automatizar a conciliação bancária manual do meu escritório de contabilidade",
    "Marketplace que conecta passeadores de cães a donos de pets",
    "Robô de arbitragem de cripto entre Binance e Mercado Bitcoin com backtest",
    "Curso online de Excel para contadores com assinatura mensal",
]
REPO_LOCAL = RAIZ / "_private" / "kb" / "github" / "idea-evaluator"


def _cli(*args) -> str:
    import analisar
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        analisar.main(list(args))
    return buf.getvalue()


def main() -> int:
    gerados = []
    for caso, texto in CASOS_IDEIA.items():
        r = gps.analisar_ideia(texto)
        if caso == "ideia_clinica":
            gerados += telas.telas_ideia(r, TELAS_PRIVADAS / caso)
        else:
            gerados += [telas.tela_gps(r, TELAS_PRIVADAS / caso / "tela1.png"),
                        telas.tela_rotas(r, TELAS_PRIVADAS / caso / "tela3.png")]
    res, dec = gps.comparar_ideias(COMPARAR)
    gerados += telas.telas_comparacao(res, dec, TELAS_PRIVADAS / "comparar")
    if REPO_LOCAL.exists():
        from apmv import repositorio
        info = repositorio.analisar(REPO_LOCAL)
        gerados.append(telas.tela_repo(info, TELAS_PRIVADAS / "repo" / "tela1.png"))
        r = gps.analisar_ideia("Avaliador de ideias de negócio com RICE e valuation, reaproveitando este código",
                               repo=str(REPO_LOCAL))
        gerados.append(telas.tela_rotas(r, TELAS_PRIVADAS / "repo" / "tela2.png"))
    gerados.append(telas.tela_terminal(_cli("tokens", "SaaS de agenda para salões com Pix, WhatsApp e painel"),
                                       "python3 analisar.py tokens \"SaaS de agenda para salões com Pix, WhatsApp e painel\"",
                                       TELAS_PRIVADAS / "tokens" / "tela1.png"))
    gerados.append(telas.tela_terminal(_cli("indicadores"), "python3 analisar.py indicadores",
                                       TELAS_PRIVADAS / "indicadores" / "tela1.png", max_linhas=40))
    gerados.append(telas.tela_terminal(_cli("prompt", CASOS_IDEIA["ideia_conciliacao"]),
                                       "python3 analisar.py prompt \"Automatizar a conciliação bancária…\"",
                                       TELAS_PRIVADAS / "prompt" / "tela1.png"))
    # Relatório-exemplo em MD + HTML + PDF (formato OCR, marca d'água) e a "tela" da página 1 do PDF.
    from apmv import exportar, relatorio
    import fitz
    r = gps.analisar_ideia(CASOS_IDEIA["ideia_clinica"])
    exemplos = RAIZ / "docs" / "exemplos"
    tl = sorted((TELAS_PRIVADAS / "ideia_clinica").glob("tela*.png"))
    saidas = exportar.exportar(relatorio.markdown(r), exemplos / "gps_clinica", tl, "GPS preditivo — clínicas odontológicas")
    pdf = fitz.open(saidas["pdf"])
    (TELAS_PRIVADAS / "relatorio").mkdir(parents=True, exist_ok=True)
    for i in (0, 2):
        destino = TELAS_PRIVADAS / "relatorio" / f"pagina{i + 1}.png"
        pdf[i].get_pixmap(dpi=90).save(destino)
        gerados.append(destino)
    gerados += list(saidas.values())

    # Publica: _private/foundations/telas → docs/telas (o README só enxerga docs/)
    if TELAS_PUBLICAS.exists():
        shutil.rmtree(TELAS_PUBLICAS)
    shutil.copytree(TELAS_PRIVADAS, TELAS_PUBLICAS, ignore=shutil.ignore_patterns(".gitkeep"))
    for g in gerados:
        print(f"🖼️  {Path(g).relative_to(RAIZ)}")
    print(f"✅ {len(gerados)} telas geradas e copiadas para {TELAS_PUBLICAS.relative_to(RAIZ)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
