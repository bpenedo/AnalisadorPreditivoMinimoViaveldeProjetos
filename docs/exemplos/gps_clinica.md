<!--
AnalisadorPreditivoMinimoViaveldeProjetos
Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
E-mail: profbruanbima@gmail.com
-->

# 🟡 GPS preditivo — TESTE ANTES

> **Ideia:** Sistema para clínicas odontológicas que perdem pacientes por falta de lembrete; envia lembretes diários pelo WhatsApp e cobra assinatura mensal; já tenho 3 clínicas interessadas, sou dentista

**Ainda não gaste tokens de código: rode o experimento mínimo e volte com a evidência.**

| Indicador-síntese | Valor |
|---|---|
| Rota recomendada (consenso das 9 escolas) | **A1 — Experimento mínimo (≤ 5 dias) antes de qualquer token de código** |
| Robustez da rota (2.000 universos de pesos) | **PROVÁVEL** — vence em 82,9% dos universos |
| Probabilidade de viabilidade | **50%** (IC80 35%–65%; prior da classe 22%) |
| Probabilidade necessária para empatar (p*) | 22% → margem de segurança 2,22× |
| Tokens para estruturar + planejar + codificar | P50 **13,7 M** · P90 40,1 M |
| Custo de construir (tokens + horas) | P50 R$ 1.954 · P90 R$ 5.725 |
| Classe de referência | SaaS B2B / ferramenta para empresas |
| Completude da descrição | 88% |

_A escolha se sustenta na maioria dos cenários, mas o vice é competitivo — compare os dois._

## 1. Quantos tokens custa — por fase

| Fase | P10 | P50 | P90 |
|---|---:|---:|---:|
| 1 · Estruturar (pesquisa, KB, refinamento) | 483 mil | 948 mil | 1,9 M |
| 2 · Planejar (arquitetura, tarefas, revisão) | 585 mil | 1,2 M | 2,3 M |
| 3 · Codificar (código, testes, QA, revisão) | 3,7 M | 11,3 M | 37,7 M |
| **Total** | 6,0 M | 13,7 M | 40,1 M |

Tamanho estimado: **27 arquivos**, 8 funcionalidades, 1 integração, complexidade **média**, 4 sessões de codificação, HITL nível 3/4. Entrada = 97% dos tokens (Bai et al., 2026: a entrada domina o custo).

| Modelo (todas as fases) | Custo P50 | Custo P90 |
|---|---:|---:|
| Rota recomendada (Sonnet 5.5 + Opus 5.5 no planejamento) | US$ 20.81 | US$ 63.50 |
| Fable 5.1 | US$ 92.02 | US$ 288.33 |
| Opus 5.5 | US$ 37.46 | US$ 117.35 |
| Sonnet 5.5 | US$ 19.37 | US$ 60.69 |
| Haiku 4.5 | US$ 9.69 | US$ 30.35 |

Horas humanas de supervisão (ACEM/HITL): P50 23,0 h · P90 67,2 h.

## 2. Vale mais que o CDI? — economia da ideia

| Item | Valor | Origem |
|---|---:|---|
| Construir (P50) | R$ 1.954 | tokens R$ 114 + horas R$ 1.840 |
| Operar no horizonte, se lançar | R$ 28.800 | horas do autor × R$ 80/h, 12 meses |
| Perda ao desistir (operação até perceber) | R$ 7.200 | 3 meses de operação |
| VP da margem — cenário conservador | R$ 13.998 | receita da classe × margem 80%, descontada pelo CDI 14% a.a. |
| VP da margem — cenário otimista | R$ 174.969 | idem |
| **VPL esperado do projeto completo** | **R$ 11.149** | p·(VP − operar) − (1−p)·desistir − construir |
| ROI esperado | 122% | VPL / capital em risco |
| Payback (conservador) | não paga em 60 meses | rampa de 6 meses |
| EVPI — quanto vale saber antes | R$ 4.586 | Howard (1966) |
| Custo do experimento mínimo | R$ 850 | 10 h + R$ 50 |
| Fração de Kelly | +0,35 | Kelly (1956): ≤ 0 = aposta desfavorável |
| Mesmo capital no CDI | +R$ 274 | custo de oportunidade |

**Utilidade marginal do capital-token** (Gossen; R$ de valor esperado por R$ adicional, sobre a fronteira eficiente das rotas): A0→A2: 18,05. Suba de degrau só enquanto a utilidade marginal for > 1. Na régua só financeira, **A1, A3** ficam fora da fronteira eficiente — o consenso ainda prefere **A1** pelos critérios não financeiros (tempo até a evidência, probabilidade de perda, opcionalidade, reversibilidade): é o preço de comprar informação e o direito de parar.

**Testar antes compensa:** a informação vale R$ 4.586 e custa R$ 850.

## 3. As rotas de alocação do capital-token

| Rota | Compromete | Valor esperado | P(perda) | Evidência em | Prob. de vencer |
|---|---:|---:|---:|---:|---:|
| **A0** Não investir agora — capital no CDI | R$ 0 | R$ 0 | 0% | 365 dias | 0,0% |
| **A1** Experimento mínimo (≤ 5 dias) antes de qualquer token de código | R$ 850 | R$ 9.805 | 13% | 5 dias | 82,9% |
| **A2** MVP enxuto (≈35% do projeto) e decisão no meio | R$ 684 | R$ 12.345 | 29% | 21 dias | 17,1% |
| **A3** Projeto completo agora | R$ 1.954 | R$ 11.149 | 50% | 105 dias | 0,0% |

- **A0** — Rende R$ 274 certos no CDI em 12 meses; é a régua que a ideia precisa bater.
- **A1** — Compra informação barata (opção real): só se gasta o projeto se o teste der positivo.
- **A2** — Constrói o núcleo, mede uso real e decide se completa — perde no máximo o MVP.
- **A3** — Gasta tudo antes de saber; só domina quando a evidência já é forte.

**Renúncia explícita:** ao escolher **A1** você renuncia, por ora, a A2, A3 — e mantém fora de risco até R$ 4.875 (exposição P90 do projeto completo) até ter evidência.

**Sensibilidade** (meta-prompt da KB — e se os pesos mudarem?): cumulatividade 2× → **A1** · durabilidade 2× → **A2** · aversão a perda 2× → **A1**

## 4. O voto das nove escolas

| Método | A0 | A1 | A2 | A3 |
|---|---:|---:|---:|---:|
| ELECTRE I | 0,000 | 0,000 | 1,000 | -1,000 |
| ELECTRE II | -1,500 | -1,500 | -1,000 | -1,500 |
| PROMETHEE II | -0,096 | 0,188 | 0,136 | -0,228 |
| MAUT | 0,528 | 0,846 | 0,808 | 0,421 |
| MCDA-C | 16,739 | 73,657 | 70,092 | 0,156 |
| AHP-TOPSIS 2n | 0,477 | 0,684 | 0,661 | 0,474 |
| VIKOR | -0,828 | -0,000 | -0,130 | -0,706 |
| TODIM | 0,548 | 1,000 | 0,841 | 0,000 |
| SAPEVO-M | 0,496 | 0,705 | 0,647 | 0,391 |

Critérios e pesos: Valor esperado (VPL vs CDI) (22%, ↑) · Capital comprometido (10%, ↓) · Probabilidade de perda total (14%, ↓) · Tempo até a 1ª evidência (10%, ↓) · Reversibilidade / cumulatividade (12%, ↑) · Opcionalidade (direito de parar) (10%, ↑) · Exposição à cauda de tokens (P90) (10%, ↓) · Durabilidade × escalabilidade engajadas (12%, ↑)

## 5. Painel de indicadores

| Dimensão | Nota | Confiança |
|---|---:|---:|
| Problema & Demanda | 0,70 | 0,82 |
| Mercado & Diversidade | 0,49 | 0,46 |
| Viabilidade técnica | 0,65 | 0,58 |
| Viabilidade econômica | 0,69 | 0,53 |
| Durabilidade | 0,86 | 0,40 |
| Escalabilidade | 0,65 | 0,50 |
| Cumulatividade | 0,55 | 0,53 |
| Robustez & Risco | 0,71 | 0,61 |
| Alinhamento & Testabilidade | 0,77 | 0,64 |
| Informação & Incerteza | 0,76 | 0,87 |

<details><summary><b>Todos os indicadores, com evidência e fonte</b></summary>

| ID | Indicador | Nota | Conf. | Evidência | Fonte |
|---|---|---:|---:|---|---|
| ALI-01 | Vantagem do autor (founder-fit) | 0,85 | 0,80 | “sou dentista” | JAFARI-2025-META, VCBENCH-2025 |
| ALI-02 | Testabilidade (experimento ≤ 5 dias) | 0,80 | 0,60 | experimento mínimo formulável | CAMUFFO-2020, CAMUFFO-2024-SMJ |
| ALI-03 | Tempo até a 1ª evidência | 0,80 | 0,80 | “interessadas” | KERR-NANDA-RK-2014 |
| ALI-04 | Operação de custo zero (client-side/Colab) | 0,50 | 0,35 | sem menção no texto | TOKENCOST |
| CUM-01 | Ativos reutilizáveis (código, componentes) | 0,50 | 0,80 | sem menção no texto | KB-METAPROMPT, DIXIT-PINDYCK-1994 |
| CUM-02 | Fosso de dados | 0,30 | 0,35 | sem menção no texto | IDEA-EVALUATOR |
| CUM-03 | Reversibilidade — o que sobra se falhar | 0,65 | 0,50 | código/skills reaproveitáveis + aprendizado do domínio | KB-METAPROMPT, KERR-NANDA-RK-2014 |
| CUM-04 | Opcionalidade (pivôs possíveis) | 0,70 | 0,45 | 1 segmento(s) de uso detectado(s) | DIXIT-PINDYCK-1994 |
| DEM-01 | Severidade da dor | 0,62 | 0,80 | “perdem” | CBINSIGHTS-FAIL, KB-METAPROMPT |
| DEM-02 | Frequência da dor | 0,72 | 0,80 | “diarios, mensal” | CBINSIGHTS-FAIL |
| DEM-03 | Disposição a pagar | 0,70 | 0,80 | “assinatura” | IDEA-EVALUATOR, CBINSIGHTS-FAIL |
| DEM-04 | Evidência de demanda (validação) | 0,60 | 0,90 | “interessadas” | CAMUFFO-2020, RIES-2011 |
| DEM-05 | Clareza do cliente-alvo | 0,90 | 0,80 | “clinicas” | JAFARI-2025-SAISE |
| DUR-01 | Durabilidade da classe de referência | 0,70 | 0,50 | perfil da classe “SaaS B2B / ferramenta para empresas” | FLYVBJERG-GARDNER-2023, KAHNEMAN-LOVALLO-1993 |
| DUR-02 | Imunidade a modismo | 0,98 | 0,35 | sem menção no texto | KB-METAPROMPT |
| DUR-03 | Independência de plataforma única | 0,98 | 0,35 | sem menção no texto | KB-METAPROMPT |
| ECO-01 | Custo P50 (tokens + horas) | 0,51 | 0,60 | R$ 1.954 (tokens R$ 114 + horas R$ 1.840) | BAI-2026-TOKENS, TOKENCAST, PRECOS-CLAUDE-2026 |
| ECO-02 | Cauda de tokens (P90/P50) | 0,34 | 0,70 | P90/P50 = 2,9× | BAI-2026-TOKENS, FLYVBJERG-BUDZIER-2011 |
| ECO-03 | Margem de segurança p/p* | 0,98 | 0,45 | p necessária 22% · margem 2,22× | KAHNEMAN-LOVALLO-1993 |
| ECO-04 | VPL esperado vs CDI | 0,98 | 0,45 | VPL esperado R$ 11.149 | DIXIT-PINDYCK-1994 |
| ECO-05 | Payback | 0,02 | 0,40 | sem payback em 60 meses (cenário conservador) | KB-SHANNON |
| ECO-06 | Receita recorrente | 0,90 | 0,80 | “assinatura, mensal” | IDEA-EVALUATOR |
| ECO-07 | Fração de Kelly | 0,85 | 0,40 | f* = +0,35 | KELLY-1956 |
| ECO-08 | Utilidade marginal do capital-token (Gossen) | 0,95 | 0,45 | A0→A2: R$ 18,05 de valor esperado por R$ adicional | GOSSEN-1854, KB-SHANNON, DIXIT-PINDYCK-1994 |
| ESC-01 | Custo marginal próximo de zero | 0,80 | 0,80 | “sistema” | KB-METAPROMPT |
| ESC-02 | Efeito de rede | 0,40 | 0,35 | sem menção no texto | KB-METAPROMPT |
| ESC-03 | Automação do processo | 0,40 | 0,35 | sem menção no texto | KB-METAPROMPT |
| ESC-04 | Escalabilidade da classe | 0,75 | 0,50 | perfil da classe “SaaS B2B / ferramenta para empresas” | FLYVBJERG-GARDNER-2023 |
| INF-01 | Completude da descrição | 0,88 | 1,00 | 7/8 perguntas essenciais respondidas | JAFARI-2025-SAISE, SHANNON-1948 |
| INF-02 | Confiança da classe de referência | 0,50 | 1,00 | saas_b2b 50%, saude_regulado 30%, ferramenta_dev 10% | KAHNEMAN-LOVALLO-1993, KNN-ICL-2026 |
| INF-03 | Valor da informação (EVPI / custo do teste) | 1,00 | 0,60 | EVPI R$ 4.586 vs experimento R$ 850 | HOWARD-1966-VOI |
| MER-01 | Alcance de mercado | 0,60 | 0,80 | sem menção no texto | IDEA-EVALUATOR |
| MER-02 | Diversidade de usos — entropia de Shannon | 0,40 | 0,40 | H = 0,00 (saude=4) | KB-SHANNON, SHANNON-1948 |
| MER-03 | Concentração de usos — HHI | 0,40 | 0,40 | HHI = 1,00 | KB-SHANNON, HHI |
| MER-04 | Índice de Simpson | 0,40 | 0,40 | Simpson D = 0,00 | KB-SHANNON |
| MER-05 | Pressão competitiva | 0,55 | 0,35 | sem menção no texto | IDEA-EVALUATOR |
| MER-06 | Índice de Versatilidade (VI) | 0,50 | 0,40 | VI = 25% (1 segmento(s) viável(is)) | KB-SHANNON |
| ROB-01 | Risco regulatório | 0,60 | 0,80 | “pacientes” | KB-METAPROMPT |
| ROB-02 | Dependência de fatores externos | 0,90 | 0,55 | 1 integração externa | KB-METAPROMPT |
| ROB-03 | Risco de execução solo (HITL) | 0,70 | 0,60 | HITL Intensity Score 3/4 | ELRAMLY-2026-ACEM |
| ROB-04 | Perda máxima relativa (aversão à perda) | 0,71 | 0,50 | perda máxima P90 R$ 5.725 | KAHNEMAN-TVERSKY-1979, GOMES-LIMA-1992 |
| TEC-01 | Tamanho funcional (pontos de função) | 0,73 | 0,55 | 27 arquivos estimados (8 funcionalidades) | ALBRECHT-1979-FP, BOEHM-2000-COCOMO |
| TEC-02 | Dependência de integrações externas | 0,88 | 0,60 | “whatsapp” | ELRAMLY-2026-ACEM |
| TEC-03 | Exigência de tempo real / hardware | 0,98 | 0,35 | sem menção no texto | BOEHM-2000-COCOMO |
| TEC-04 | Maturidade de código existente (TRL-software) | 0,30 | 0,90 | nenhum código existente informado — parte do zero | GITHUB-FUNDING-2023 |
| TEC-05 | Resiliência à comoditização por IA | 0,70 | 0,50 | classe “SaaS B2B / ferramenta para empresas”, risco de comoditização 40% | IDEA-EVALUATOR, VCBENCH-2025 |

</details>

**Como cada dimensão moveu a probabilidade** (Δ log-odds sobre o prior da classe): DEM +0,44 · DUR +0,21 · ROB +0,18 · ALI +0,18 · TEC +0,13 · ESC +0,10 · CUM +0,04 · MER -0,00

## 6. O que a planilha não diz

**Perguntas que você provavelmente está evitando:**

1. Que dado proprietário fica mais valioso a cada uso?
1. Se o primeiro segmento não comprar, qual é o segundo? Existe?
1. Por que o cliente trocaria a solução atual (incluindo planilha e WhatsApp) pela sua?

**Teste de reversibilidade:** ALTA — o que se constrói (código, dados, aprendizado do domínio) serve a outros projetos.

**Experimento mínimo (≤ 5 dias) que mataria a ideia:** Landing page + 15 mensagens diretas para o público-alvo pedindo uma call ou pré-venda; menos de 3 respostas qualificadas em 5 dias = sem dor suficiente.

**Mapa de dependências:**

| Depende só de você | Depende do mundo |
|---|---|
| escrever e testar o código | APIs de terceiros: whatsapp |
| definir o escopo mínimo | regulação/licenciamento do setor |
| aplicar a sua experiência no domínio |  |

**Lacunas — o que descobrir antes (em vez de chutar):**

- quem já resolve isso (concorrência)

## Premissas (edite e rode de novo)

Câmbio R$ 5.50/US$ · CDI 14% a.a. · horizonte 12 meses · valor-hora R$ 80 · preços Claude de 25/09/2026 · semente 42.

## Aprofunde com um LLM (prompt pronto)

```text
Você é um arquiteto de decisão multicritério e um investidor cético que já viu 500 pitches.
Contexto: tenho esta ideia e preciso decidir se invisto tokens/tempo nos próximos 90 dias.

IDEIA: Sistema para clínicas odontológicas que perdem pacientes por falta de lembrete; envia lembretes diários pelo WhatsApp e cobra assinatura mensal; já tenho 3 clínicas interessadas, sou dentista

O analisador quantitativo já estimou: classe de referência "SaaS B2B / ferramenta para empresas", p(viável) = 50%
(IC80 35%–65%), tokens P50 13,7 M / P90 40,1 M, rota recomendada "Experimento mínimo (≤ 5 dias) antes de qualquer token de código".

1. Faça 3 perguntas que eu provavelmente estou evitando. Não seja educado.
2. Teste de reversibilidade: se eu investir 3 meses e falhar, o que sobra? (alta/média/baixa + 1 frase)
3. Proponha o menor experimento (≤ 5 dias, custo ~0) que MATARIA a ideia se desse negativo.
   Se não for possível, diga "essa ideia ainda está abstrata demais para testar".
4. Separe dependências: só de mim × do mundo (mercado, timing, parceiros, regulação).
5. Se faltar dado, diga o que eu precisaria descobrir — não chute números.
Prefira ser útil a ser impressionante.
```

_Análise em 2.2 s · fontes: ALBRECHT-1979-FP, BAI-2026-TOKENS, BOEHM-2000-COCOMO, CAMUFFO-2020, CAMUFFO-2024-SMJ, CBINSIGHTS-FAIL, DIXIT-PINDYCK-1994, ELRAMLY-2026-ACEM, FLYVBJERG-BUDZIER-2011, FLYVBJERG-GARDNER-2023, GITHUB-FUNDING-2023, GOMES-LIMA-1992, GOSSEN-1854, HHI, HOWARD-1966-VOI, IDEA-EVALUATOR, JAFARI-2025-META, JAFARI-2025-SAISE, KAHNEMAN-LOVALLO-1993, KAHNEMAN-TVERSKY-1979, KB-METAPROMPT, KB-SHANNON, KELLY-1956, KERR-NANDA-RK-2014, KNN-ICL-2026, PRECOS-CLAUDE-2026, RIES-2011, SHANNON-1948, TOKENCAST, TOKENCOST, VCBENCH-2025_
