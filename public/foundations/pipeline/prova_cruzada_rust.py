#!/usr/bin/env python3
# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Prova cruzada Python × Rust (D9): os dois motores precisam concordar até 1e-9.

Exporta os insumos de cada caso, roda o binário Rust (sem dependências), e compara
VPL, p*, EVPI, Kelly, rotas A1/A2, payback e a probabilidade recalculada do log-odds.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from apmv import financeiro, gps
from config import RAIZ

CRATE = RAIZ / "public" / "foundations" / "rust" / "analisadorpreditivominimoviaveldeprojetos_core"
BINARIO = CRATE / "target" / "release" / "apmv_core"
TOL = 1e-9
CASOS = {
    "clinica": "Sistema para clínicas odontológicas que perdem pacientes; lembretes diários pelo WhatsApp, assinatura mensal; já tenho 3 clínicas interessadas, sou dentista",
    "conciliacao": "Automatizar a conciliação bancária manual que meu escritório de contabilidade faz todo dia em planilha",
    "arbitragem": "Robô de arbitragem de cripto entre Binance e Mercado Bitcoin",
    "marketplace": "Marketplace que conecta passeadores de cães a donos de pets em tempo real com app mobile",
    "vaga": "uma ideia legal",
}


def main() -> int:
    if not BINARIO.exists():
        subprocess.run(["cargo", "build", "--release", "-q"], cwd=CRATE, check=True)
    entrada, esperado = [], {}
    for nome, texto in CASOS.items():
        r = gps.analisar_ideia(texto, n_iter=200)
        f, p = r.financeiro, r.financeiro.premissas
        horas_mes, margem = financeiro.OPERACAO.get(r.sinais.classe.nome, financeiro.OPERACAO["generico"])
        rc = p.receita_mensal_cons if p.receita_mensal_cons is not None else r.sinais.classe.receita_mensal_cons
        ro = p.receita_mensal_otim if p.receita_mensal_otim is not None else r.sinais.classe.receita_mensal_otim
        campos = {"p_viavel": r.previsao.p_viavel, "custo_construir": f.custo_total["p50"], "horizonte": p.horizonte_meses,
                  "cdi": p.cdi_anual, "infra_mes": p.custo_operacao_mes, "margem_contribuicao": margem,
                  "horas_mes": horas_mes, "valor_hora": p.valor_hora, "receita_cons": rc, "receita_otim": ro,
                  "custo_experimento": f.custo_experimento, "prior": r.previsao.prior,
                  **{f"contrib_{k}": v for k, v in r.previsao.contribuicoes.items()}}
        entrada.append(f"caso {nome}")
        entrada += [f"{k} = {v!r}" for k, v in campos.items()]
        rotas = {x.codigo: x.valor_esperado for x in f.rotas}
        esperado[nome] = {"vp_receita_cons": f.vp_receita_cons, "vp_receita_otim": f.vp_receita_otim,
                          "vpl_esperado": f.vpl_esperado, "p_breakeven": f.p_breakeven, "evpi": f.evpi,
                          "kelly": f.kelly, "rota_a1": rotas["A1"], "rota_a2": rotas["A2"],
                          "payback": f.payback_meses if f.payback_meses is not None else -1.0,
                          "p_viavel_recalculada": r.previsao.p_viavel}
    saida = subprocess.run([str(BINARIO)], input="\n".join(entrada), capture_output=True, text=True, check=True).stdout
    rust, atual = {}, None
    for ln in saida.splitlines():
        if ln.startswith("caso "):
            atual = ln[5:]
            rust[atual] = {}
        elif "=" in ln:
            k, v = ln.split("=")
            rust[atual][k.strip()] = float(v)
    falhas = 0
    for nome, exp in esperado.items():
        deltas = {k: abs(exp[k] - rust[nome][k]) / max(1.0, abs(exp[k])) for k in exp}
        pior = max(deltas.values())
        ok = pior <= TOL
        falhas += not ok
        print(f"{'✅' if ok else '❌'} {nome:<12} {len(deltas)} grandezas idênticas · Δ relativo máx {pior:.1e}"
              + ("" if ok else f" · divergem: {[k for k, d in deltas.items() if d > TOL]}"))
    print(f"\n{'✅ Python e Rust concordam' if not falhas else '❌ motores divergem'} ({len(esperado)} casos, tolerância {TOL:g})")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
