#!/usr/bin/env python3
# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Monta `readme.blocos.json` a partir dos arquivos de autoria `translation/blocos/<idioma>.md`.

Formato de autoria (um arquivo por idioma, legível e revisável por tradutor):

    === chave ===
    texto do bloco, quantas linhas forem necessárias (Markdown/HTML permitido)
    === outra_chave ===
    ...

Regras (falha alto, nunca em silêncio):
  • todos os idiomas precisam ter EXATAMENTE as chaves do pt (origem);
  • bloco vazio é erro;
  • bloco traduzido idêntico ao pt só é aceito se for curto (rótulo como "Autor:") ou só código/links.
"""
from __future__ import annotations

import json
import re
import sys

from config import ENCODING, FOUNDATIONS

PASTA = FOUNDATIONS / "translation" / "blocos"
SAIDA = FOUNDATIONS / "translation" / "readme.blocos.json"
IDIOMAS = ("pt", "en", "es", "fr", "de", "zh", "ko", "hi", "he", "ru", "sv", "fi")
RX = re.compile(r"^=== ([a-z0-9_]+) ===\s*$", re.M)


def ler(idioma: str) -> dict[str, str]:
    t = (PASTA / f"{idioma}.md").read_text(encoding=ENCODING)
    partes = RX.split(t)
    return {partes[i]: partes[i + 1].strip("\n") for i in range(1, len(partes), 2)}


def main() -> int:
    faltando = [i for i in IDIOMAS if not (PASTA / f"{i}.md").exists()]
    if faltando:
        print(f"❌ arquivos de autoria ausentes: {', '.join(faltando)}")
        return 1
    dados = {i: ler(i) for i in IDIOMAS}
    origem = dados["pt"]
    erros = []
    for i in IDIOMAS:
        d = dados[i]
        if set(d) != set(origem):
            erros.append(f"{i}: faltam {sorted(set(origem) - set(d))} · sobram {sorted(set(d) - set(origem))}")
        for k, v in d.items():
            if not v.strip():
                erros.append(f"{i}.{k}: vazio")
            elif i != "pt" and v == origem.get(k) and len(re.sub(r"\(.*?\)|\[.*?\]|<[^>]+>|\W", "", v)) > 30:
                erros.append(f"{i}.{k}: idêntico ao português (não traduzido?)")
    if erros:
        print("❌ blocos inconsistentes:\n   " + "\n   ".join(erros))
        return 1
    blocos = {k: {i: dados[i][k] for i in IDIOMAS} for k in origem}
    SAIDA.write_text(json.dumps(blocos, ensure_ascii=False, indent=2) + "\n", encoding=ENCODING)
    print(f"✅ {len(blocos)} blocos × {len(IDIOMAS)} idiomas → {SAIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
