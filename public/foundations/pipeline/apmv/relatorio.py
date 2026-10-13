# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Relatório do GPS preditivo em Markdown (para ler) e JSON (para máquinas).

Regra de redação: todo número vem com a sua origem (fórmula, premissa ou fonte) e
toda nota com a sua evidência. Premissa aparece como premissa — nunca como fato.
"""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass

from .decisao import CRITERIOS_ROTA
from .gps import MENSAGENS
from .indicadores import CATALOGO_POR_ID, DIMENSOES
from .mcdm import METODOS
from .mcdm.robustez import DESCRICAO_VEREDITO
from .referencias import REFERENCIAS
from .tokens import FASES, PRECOS, formatar_tokens

ROTULO_FASE = {"estruturar": "1 · Estruturar (pesquisa, KB, refinamento)",
               "planejar": "2 · Planejar (arquitetura, tarefas, revisão)",
               "codificar": "3 · Codificar (código, testes, QA, revisão)",
               "total": "**Total**"}

PROMPT_MESTRE = """Você é um arquiteto de decisão multicritério e um investidor cético que já viu 500 pitches.
Contexto: tenho esta ideia e preciso decidir se invisto tokens/tempo nos próximos 90 dias.

IDEIA: {ideia}

O analisador quantitativo já estimou: classe de referência "{classe}", p(viável) = {p:.0%}
(IC80 {ic0:.0%}–{ic1:.0%}), tokens P50 {t50} / P90 {t90}, rota recomendada "{rota}".

1. Faça 3 perguntas que eu provavelmente estou evitando. Não seja educado.
2. Teste de reversibilidade: se eu investir 3 meses e falhar, o que sobra? (alta/média/baixa + 1 frase)
3. Proponha o menor experimento (≤ 5 dias, custo ~0) que MATARIA a ideia se desse negativo.
   Se não for possível, diga "essa ideia ainda está abstrata demais para testar".
4. Separe dependências: só de mim × do mundo (mercado, timing, parceiros, regulação).
5. Se faltar dado, diga o que eu precisaria descobrir — não chute números.
Prefira ser útil a ser impressionante."""


def _brl(v: float) -> str:
    return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(v: float) -> str:
    return f"{v:.0%}"


def _d(v: float, casas: int = 1) -> str:
    """Número com vírgula decimal (PT-BR) — BUG-009."""
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _plural(n: int, sing: str, plur: str) -> str:
    return f"{n} {sing if n == 1 else plur}"


def markdown(r) -> str:
    f, d, e, s = r.financeiro, r.decisao, r.tokens, r.sinais
    emo, titulo, frase = MENSAGENS[r.semaforo]
    rota = next(x for x in f.rotas if x.codigo == r.rota_recomendada)
    L = []
    L += [f"# {emo} GPS preditivo — {titulo}", "",
          f"> **Ideia:** {r.texto}", "",
          f"**{frase}**", "",
          "| Indicador-síntese | Valor |", "|---|---|",
          f"| Rota recomendada (consenso das 9 escolas) | **{rota.codigo} — {rota.nome}** |",
          f"| Robustez da rota ({_d(d.n_iter, 0)} universos de pesos) | **{d.veredito_robustez}** — vence em {_d(d.prob_lider)}% dos universos |",
          f"| Probabilidade de viabilidade | **{_pct(r.previsao.p_viavel)}** (IC80 {_pct(r.previsao.ic80[0])}–{_pct(r.previsao.ic80[1])}; prior da classe {_pct(r.previsao.prior)}) |",
          f"| Probabilidade necessária para empatar (p*) | {_pct(f.p_breakeven)} → margem de segurança {_d(f.margem_seguranca, 2)}× |",
          f"| Tokens para estruturar + planejar + codificar | P50 **{formatar_tokens(e.quantis['total']['p50'])}** · P90 {formatar_tokens(e.quantis['total']['p90'])} |",
          f"| Custo de construir (tokens + horas) | P50 {_brl(f.custo_total['p50'])} · P90 {_brl(f.custo_total['p90'])} |",
          f"| Classe de referência | {s.classe.rotulo} |",
          f"| Completude da descrição | {_pct(s.completude)} |", ""]
    if r.avisos:
        L += ["> [!WARNING]"] + [f"> {a}  " for a in r.avisos] + [""]
    L += [f"_{DESCRICAO_VEREDITO[d.veredito_robustez].capitalize()}_", ""]

    L += ["## 1. Quantos tokens custa — por fase", "",
          "| Fase | P10 | P50 | P90 |", "|---|---:|---:|---:|"]
    for fase in FASES + ("total",):
        q = e.quantis[fase]
        L.append(f"| {ROTULO_FASE[fase]} | {formatar_tokens(q['p10'])} | {formatar_tokens(q['p50'])} | {formatar_tokens(q['p90'])} |")
    t = e.tamanho
    L += ["", f"Tamanho estimado: **{t.arquivos_novos} arquivos**, {t.funcionalidades} funcionalidades, "
          f"{_plural(t.integracoes, "integração", "integrações")}, complexidade **{ {'baixa': 'baixa', 'media': 'média', 'alta': 'alta'}[t.complexidade] }**, {_plural(t.sessoes, "sessão", "sessões")} de codificação, "
          f"HITL nível {t.his}/4. Entrada = {_pct(e.fracao_entrada)} dos tokens (Bai et al., 2026: a entrada domina o custo).", "",
          "| Modelo (todas as fases) | Custo P50 | Custo P90 |", "|---|---:|---:|",
          f"| Rota recomendada (Sonnet 5.5 + Opus 5.5 no planejamento) | US$ {e.custo_usd['rota_recomendada']['p50']:.2f} | US$ {e.custo_usd['rota_recomendada']['p90']:.2f} |"]
    for m, pr in PRECOS.items():
        L.append(f"| {pr['rotulo']} | US$ {e.custo_usd[m]['p50']:.2f} | US$ {e.custo_usd[m]['p90']:.2f} |")
    L += ["", f"Horas humanas de supervisão (ACEM/HITL): P50 {_d(e.horas_humanas['p50'])} h · P90 {_d(e.horas_humanas['p90'])} h.", ""]

    p = f.premissas
    L += ["## 2. Vale mais que o CDI? — economia da ideia", "",
          "| Item | Valor | Origem |", "|---|---:|---|",
          f"| Construir (P50) | {_brl(f.custo_total['p50'])} | tokens {_brl(f.custo_tokens_brl['p50'])} + horas {_brl(f.custo_horas_brl['p50'])} |",
          f"| Operar no horizonte, se lançar | {_brl(f.custo_operar)} | horas do autor × {_brl(p.valor_hora)}/h, {p.horizonte_meses} meses |",
          f"| Perda ao desistir (operação até perceber) | {_brl(f.custo_desistir)} | 3 meses de operação |",
          f"| VP da margem — cenário conservador | {_brl(f.vp_receita_cons)} | receita da classe × margem {_pct(f.margem_contribuicao)}, descontada pelo CDI {_pct(p.cdi_anual)} a.a. |",
          f"| VP da margem — cenário otimista | {_brl(f.vp_receita_otim)} | idem |",
          f"| **VPL esperado do projeto completo** | **{_brl(f.vpl_esperado)}** | p·(VP − operar) − (1−p)·desistir − construir |",
          f"| ROI esperado | {_pct(f.roi_esperado)} | VPL / capital em risco |",
          f"| Payback (conservador) | {'não paga em 60 meses' if f.payback_meses is None else f'{f.payback_meses:.0f} meses'} | rampa de {6} meses |",
          f"| EVPI — quanto vale saber antes | {_brl(f.evpi)} | Howard (1966) |",
          f"| Custo do experimento mínimo | {_brl(f.custo_experimento)} | 10 h + R$ 50 |",
          f"| Fração de Kelly | {_d(f.kelly, 2) if f.kelly < 0 else "+" + _d(f.kelly, 2)} | Kelly (1956): ≤ 0 = aposta desfavorável |",
          f"| Mesmo capital no CDI | +{_brl(f.custo_total['p50'] * ((1 + p.cdi_anual) ** (p.horizonte_meses / 12) - 1))} | custo de oportunidade |", ""]
    if f.utilidade_marginal or f.rotas_dominadas:
        degraus = " · ".join(f"{k}: {_d(v, 2)}" for k, v in f.utilidade_marginal.items()) or "só A0"
        L += [f"**Utilidade marginal do capital-token** (Gossen; R$ de valor esperado por R$ adicional, sobre a fronteira "
              f"eficiente das rotas): {degraus}. Suba de degrau só enquanto a utilidade marginal for > 1."
              + (f" Na régua só financeira, **{', '.join(f.rotas_dominadas)}** ficam fora da fronteira eficiente"
                 + (f" — o consenso ainda prefere **{rota.codigo}** pelos critérios não financeiros (tempo até a evidência, "
                    "probabilidade de perda, opcionalidade, reversibilidade): é o preço de comprar informação e o direito de parar."
                    if rota.codigo in f.rotas_dominadas else ".")
                 if f.rotas_dominadas else ""), ""]
    if f.evpi > f.custo_experimento:
        L += [f"**Testar antes compensa:** a informação vale {_brl(f.evpi)} e custa {_brl(f.custo_experimento)}.", ""]

    L += ["## 3. As rotas de alocação do capital-token", "",
          "| Rota | Compromete | Valor esperado | P(perda) | Evidência em | Prob. de vencer |",
          "|---|---:|---:|---:|---:|---:|"]
    for x in f.rotas:
        L.append(f"| **{x.codigo}** {x.nome} | {_brl(x.custo)} | {_brl(x.valor_esperado)} | {_pct(x.p_perda_total)} | "
                 f"{x.tempo_ate_evidencia_dias:.0f} dias | {_d(d.prob_vitoria.get(x.codigo, 0))}% |")
    L += ["", *[f"- **{x.codigo}** — {x.descricao}" for x in f.rotas], ""]
    # Renúncia explícita — escolher é também decidir o que NÃO fazer agora.
    renuncias = [x for x in f.rotas if x.codigo not in (rota.codigo, "A0")]
    if rota.codigo != "A3":
        exp = f.custo_total["p90"] - (rota.custo if rota.codigo != "A0" else 0)
        L += [f"**Renúncia explícita:** ao escolher **{rota.codigo}** você renuncia, por ora, a "
              + ", ".join(f"{x.codigo}" for x in renuncias)
              + f" — e mantém fora de risco até {_brl(max(exp, 0))} (exposição P90 do projeto completo) até ter evidência.", ""]
    else:
        L += ["**Renúncia explícita:** ao ir direto ao projeto completo, você renuncia à opção de parar barato — "
              "faça isso só porque a evidência já é forte.", ""]
    L += ["**Sensibilidade** (meta-prompt da KB — e se os pesos mudarem?): " +
          " · ".join(f"{k} → **{v}**" for k, v in d.sensibilidade.items()), ""]

    L += ["## 4. O voto das nove escolas", "",
          "| Método | " + " | ".join(d.alternativas) + " |", "|---|" + "---:|" * len(d.alternativas)]
    for m in METODOS:
        L.append(f"| {m} | " + " | ".join(_d(v, 3) for v in d.scores[m]) + " |")
    L += ["", "Critérios e pesos: " + " · ".join(f"{c[0]} ({c[2]:.0%}, {'↑' if c[1] == 'benefit' else '↓'})" for c in CRITERIOS_ROTA), ""]

    L += ["## 5. Painel de indicadores", "",
          "| Dimensão | Nota | Confiança |", "|---|---:|---:|"]
    for dim, v in r.dimensoes.items():
        L.append(f"| {DIMENSOES[dim]['nome']} | {_d(v['nota'], 2)} | {_d(v['confianca'], 2)} |")
    L += ["", "<details><summary><b>Todos os indicadores, com evidência e fonte</b></summary>", "",
          "| ID | Indicador | Nota | Conf. | Evidência | Fonte |", "|---|---|---:|---:|---|---|"]
    for mid in sorted(r.medidas):
        ind, v = CATALOGO_POR_ID[mid], r.medidas[mid]
        L.append(f"| {mid} | {ind.nome} | {_d(v.nota, 2)} | {_d(v.confianca, 2)} | {v.evidencia} | {', '.join(ind.fontes)} |")
    L += ["", "</details>", "",
          "**Como cada dimensão moveu a probabilidade** (Δ log-odds sobre o prior da classe): " +
          " · ".join(f"{k} {'+' if v >= 0 else ''}{_d(v, 2)}" for k, v in sorted(r.previsao.contribuicoes.items(), key=lambda kv: -abs(kv[1]))), ""]

    L += ["## 6. O que a planilha não diz", "",
          "**Perguntas que você provavelmente está evitando:**", "", *[f"1. {q}" for q in r.perguntas_incomodas], "",
          f"**Teste de reversibilidade:** {r.reversibilidade}", "",
          f"**Experimento mínimo (≤ 5 dias) que mataria a ideia:** {r.experimento_minimo}", "",
          "**Mapa de dependências:**", "",
          "| Depende só de você | Depende do mundo |", "|---|---|"]
    a, b = r.dependencias["so_de_voce"], r.dependencias["do_mundo"]
    for i in range(max(len(a), len(b))):
        L.append(f"| {a[i] if i < len(a) else ''} | {b[i] if i < len(b) else ''} |")
    L.append("")
    if r.lacunas:
        L += ["**Lacunas — o que descobrir antes (em vez de chutar):**", "", *[f"- {x}" for x in r.lacunas], ""]
    if f.alertas_arbitragem:
        L += ["## 7. Arbitragem financeira — alertas", "", *[f"- {x}" for x in f.alertas_arbitragem], ""]
    if r.repo is not None:
        rp = r.repo
        L += ["## 8. Código existente", "",
              f"`{rp.nome}` — {rp.loc_total:,} linhas em {rp.arquivos_fonte} arquivos · {rp.trl} · maturidade {rp.maturidade:.0%} · "
              f"licença {rp.licenca} · testes {'✅' if rp.tem_testes else '❌'} · CI {'✅' if rp.tem_ci else '❌'}", "",
              *[f"- {o}" for o in rp.observacoes], ""]
    L += ["## Premissas (edite e rode de novo)", "",
          f"Câmbio R$ {p.cambio:.2f}/US$ · CDI {_pct(p.cdi_anual)} a.a. · horizonte {p.horizonte_meses} meses · "
          f"valor-hora {_brl(p.valor_hora)} · preços Claude de 25/09/2026 · semente 42.", "",
          "## Aprofunde com um LLM (prompt pronto)", "", "```text",
          PROMPT_MESTRE.format(ideia=r.texto, classe=s.classe.rotulo, p=r.previsao.p_viavel, ic0=r.previsao.ic80[0],
                               ic1=r.previsao.ic80[1], t50=formatar_tokens(e.quantis["total"]["p50"]),
                               t90=formatar_tokens(e.quantis["total"]["p90"]), rota=rota.nome),
          "```", "",
          f"_Análise em {r.tempo_s:.1f} s · fontes: " + ", ".join(sorted({x for m in r.medidas for x in CATALOGO_POR_ID[m].fontes})) + "_"]
    return "\n".join(L) + "\n"


def markdown_comparacao(resultados, dec) -> str:
    L = ["# ⚖️ GPS preditivo — comparação de ideias", "",
         f"Consenso das 9 escolas: **{dec.lider}** vence em {_d(dec.prob_lider)}% dos universos de pesos e em "
         f"{_d((dec.prob_vitoria_notas or {}).get(dec.lider, 0))}% dos universos de notas — **{dec.veredito_robustez}** "
         "(o veredito usa a MENOR das duas robustezes).", "",
         "| # | Ideia | Semáforo | p(viável) | Tokens P50 | VPL esperado | Rota | Vence (pesos) | Vence (notas) |",
         "|---|---|---|---:|---:|---:|---|---:|---:|"]
    for i, r in enumerate(resultados):
        emo, tit, _ = MENSAGENS[r.semaforo]
        L.append(f"| I{i + 1} | {r.texto[:60]}{'…' if len(r.texto) > 60 else ''} | {emo} {tit} | {_pct(r.previsao.p_viavel)} | "
                 f"{formatar_tokens(r.tokens.quantis['total']['p50'])} | {_brl(r.financeiro.vpl_esperado)} | {r.rota_recomendada} | "
                 f"{_d(dec.prob_vitoria.get(f'I{i + 1}', 0))}% | {_d((dec.prob_vitoria_notas or {}).get(f'I{i + 1}', 0))}% |")
    pior = min(range(len(resultados)), key=lambda i: dec.prob_vitoria.get(f"I{i + 1}", 0) + resultados[i].previsao.p_viavel)
    ef = max(range(len(resultados)), key=lambda i: resultados[i].previsao.p_viavel / max(resultados[i].financeiro.custo_experimento, 1)
             * (1 + resultados[i].sinais.completude))
    pvn = dec.prob_vitoria_notas or dec.prob_vitoria
    vivas = [k for k, v in sorted(pvn.items(), key=lambda kv: -kv[1]) if v >= 5.0]
    mortas = [k for k in pvn if k not in vivas]
    if len(vivas) >= 2:
        L += ["", f"**Leitura:** {' e '.join(vivas)} estão em empate técnico diante da incerteza das notas — "
              "não escolha pelo ranking; rode o experimento mínimo das duas e deixe a evidência desempatar."]
    if mortas:
        L += [f"**Renúncia segura:** {', '.join(mortas)} não vencem em nenhum cenário plausível (< 5%) — "
              "renuncie agora e libere tempo e tokens para as demais."]
    L += ["", f"**Eliminaria primeiro:** I{pior + 1} — menor probabilidade de viabilidade combinada com a pior posição no consenso.",
          f"**Melhor relação esforço de 90 dias → evidência concreta:** I{ef + 1} — {resultados[ef].experimento_minimo}", ""]
    conflitos = []
    for i in range(len(resultados)):
        for j in range(i + 1, len(resultados)):
            a, b = resultados[i].sinais, resultados[j].sinais
            comum = set(a.segmentos) & set(b.segmentos)
            if a.classe.nome == b.classe.nome or comum:
                conflitos.append(f"I{i + 1} × I{j + 1}: disputam " + (f"o mesmo público ({', '.join(sorted(comum))})" if comum else f"a mesma classe ({a.classe.rotulo})"))
    L += ["**Conflitos reais entre as ideias:**", *([f"- {c}" for c in conflitos] or ["- nenhum detectado no texto: competem apenas pelo seu tempo."]), ""]
    return "\n".join(L) + "\n"


def _jsonavel(o):
    if is_dataclass(o):
        return {k: _jsonavel(v) for k, v in asdict(o).items()}
    if isinstance(o, dict):
        return {str(k): _jsonavel(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonavel(v) for v in o]
    if hasattr(o, "tolist"):
        return o.tolist()
    return o


def json_resultado(r) -> str:
    d = {
        "ideia": r.texto, "semaforo": r.semaforo, "rota": r.rota_recomendada,
        "robustez": r.decisao.veredito_robustez, "prob_lider": r.decisao.prob_lider,
        "p_viavel": r.previsao.p_viavel, "ic80": r.previsao.ic80, "prior": r.previsao.prior,
        "classe": r.sinais.classe.nome, "completude": r.sinais.completude, "lacunas": r.lacunas,
        "tokens": r.tokens.quantis, "custo_usd": r.tokens.custo_usd, "tamanho": _jsonavel(r.tamanho),
        "financeiro": {k: v for k, v in _jsonavel(r.financeiro).items() if k != "premissas"},
        "premissas": _jsonavel(r.financeiro.premissas),
        "dimensoes": r.dimensoes, "indicadores": {k: _jsonavel(v) for k, v in r.medidas.items()},
        "contribuicoes": r.previsao.contribuicoes, "sensibilidade": r.decisao.sensibilidade,
        "perguntas_incomodas": r.perguntas_incomodas, "reversibilidade": r.reversibilidade,
        "experimento_minimo": r.experimento_minimo, "dependencias": r.dependencias, "avisos": r.avisos,
        "repositorio": _jsonavel(r.repo) if r.repo is not None else None,
    }
    return json.dumps(d, ensure_ascii=False, indent=2)


def bibliografia_md() -> str:
    L = ["| ID | Referência | Uso no analisador |", "|---|---|---|"]
    for k, v in REFERENCIAS.items():
        cit = f"[{v['cit']}]({v['url']})" if v["url"].startswith("http") else v["cit"]
        L.append(f"| {k} | {cit} | {v['uso']} |")
    return "\n".join(L) + "\n"
