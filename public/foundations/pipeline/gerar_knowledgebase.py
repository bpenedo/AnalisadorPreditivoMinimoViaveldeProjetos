#!/usr/bin/env python3
# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Preenche as seções geradas da knowledgebase a partir do código (catálogo e bibliografia).

Idempotente: substitui o conteúdo entre os marcadores `<!-- GERADO:X -->` e o próximo `## `.
Assim o documento de fundamentação nunca descreve um indicador que não existe no código.
"""
from __future__ import annotations

import re
import sys

from apmv.indicadores import CATALOGO, DIMENSOES
from apmv.relatorio import bibliografia_md
from config import ENCODING, RAIZ

KB = RAIZ / "_private" / "kb" / "knowledgebase.md"


def catalogo_md() -> str:
    L = [f"**{len(CATALOGO)} indicadores em {len(DIMENSOES)} dimensões.** Nota sempre orientada para "
         "viabilidade (1 = favorável); sem evidência, nota 0,5 com confiança baixa.", ""]
    atual = None
    for i in CATALOGO:
        if i.dimensao != atual:
            atual = i.dimensao
            d = DIMENSOES[atual]
            L += ["", f"### {atual} — {d['nome']} (peso {d['peso']:.0%})".replace(".", ","), "",
                  "| ID | Indicador | Tipo | Fórmula | Fontes | Evidência mínima |", "|---|---|---|---|---|---|"]
        L.append(f"| {i.id} | {i.nome} | {i.tipo} | {i.formula} | {', '.join(i.fontes)} | {i.evidencia_minima} |")
    return "\n".join(L) + "\n"


def preencher(texto: str, marcador: str, conteudo: str) -> str:
    padrao = re.compile(rf"(<!-- GERADO:{marcador} -->\n)(.*?)(?=\n## )", re.S)
    if not padrao.search(texto):
        raise SystemExit(f"❌ marcador GERADO:{marcador} ausente em {KB}")
    return padrao.sub(lambda m: m.group(1) + "\n" + conteudo, texto, count=1)


def main() -> int:
    t = KB.read_text(encoding=ENCODING)
    t = preencher(t, "CATALOGO", catalogo_md())
    t = preencher(t, "BIBLIOGRAFIA", bibliografia_md())
    KB.write_text(t, encoding=ENCODING)
    print(f"✅ knowledgebase atualizada: {len(CATALOGO)} indicadores · bibliografia completa → {KB.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
