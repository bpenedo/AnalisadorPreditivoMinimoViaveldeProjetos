# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Probabilidade de viabilidade — log-odds transparentes sobre a classe de referência.

Evento previsto (definição estágio-dependente, como pede o SAISE — Jafari et al., 2025):
    "a ideia retorna MAIS do que custa (tokens + horas) dentro do horizonte".
Não é "virar unicórnio" — esse evento tem taxa-base de ~2% (VCBench, 2025) e não é
a decisão de quem vai gastar tokens numa ideia.

    logit(p) = logit(prior_da_classe) + Σ_d  w_d · K · média_i[ conf_i · (nota_i − 0,5) ]

  • prior_da_classe — outside view (Kahneman & Lovallo, 1993; Flyvbjerg, 2023);
  • cada dimensão desloca as chances proporcionalmente ao seu peso e à CONFIANÇA
    das notas — indicador sem evidência (conf baixa) quase não mexe no prior;
  • K = 12 limita o deslocamento máximo a ≈ ±3,8 logits (chances ×45): nenhum texto,
    por mais entusiasmado, transforma uma classe de 8% em certeza.

É a mesma ideia das regras probabilísticas interpretáveis do LLM-AR (2025): cada
contribuição é exibida no relatório, com sinal e tamanho.

O intervalo de credibilidade vem de uma Beta com tamanho amostral efetivo que cresce
com a completude da descrição: pouca informação ⇒ intervalo largo, e o relatório mostra.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .indicadores import CATALOGO_POR_ID, DIMENSOES, DIMENSOES_PREDITIVAS

K_DESLOCAMENTO = 12.0
N_EFETIVO_MIN, N_EFETIVO_MAX = 4.0, 20.0


@dataclass
class Previsao:
    prior: float
    p_viavel: float
    ic80: tuple[float, float]
    contribuicoes: dict[str, float]   # dimensão -> Δ logit
    n_efetivo: float


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def prever(medidas, sinais, semente: int = 42) -> Previsao:
    prior = sinais.classe.prior
    pesos = {d: DIMENSOES[d]["peso"] for d in DIMENSOES_PREDITIVAS}
    if "ARB-01" in medidas:                       # estratégia financeira: ARB ganha peso
        pesos["ARB"] = 0.12
    soma = sum(pesos.values())
    contrib = {}
    for d in DIMENSOES_PREDITIVAS:
        itens = [v for mid, v in medidas.items() if CATALOGO_POR_ID[mid].dimensao == d]
        if not itens:
            continue
        media = sum(v.confianca * (v.nota - 0.5) for v in itens) / len(itens)
        contrib[d] = pesos[d] / soma * K_DESLOCAMENTO * media
    lg = _logit(prior) + sum(contrib.values())
    p = 1 / (1 + math.exp(-lg))
    n_ef = N_EFETIVO_MIN + (N_EFETIVO_MAX - N_EFETIVO_MIN) * sinais.completude
    a, b = p * n_ef, (1 - p) * n_ef
    am = np.random.default_rng(semente).beta(a, b, 40_000)
    ic = (float(np.percentile(am, 10)), float(np.percentile(am, 90)))
    return Previsao(prior, p, ic, contrib, n_ef)
