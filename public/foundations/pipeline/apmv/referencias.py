# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Bibliografia que fundamenta cada indicador, prior e fórmula do analisador.

Regra: nenhum indicador entra no catálogo sem pelo menos UMA referência daqui.
Toda referência recente (2024–2026) foi conferida na fonte em 12/10/2026; as
clássicas são as obras seminais de cada método. O campo `uso` diz o que, no
código, depende daquela fonte — é o que permite auditar a cadeia
"número no relatório → fórmula → fonte".
"""
from __future__ import annotations

# id -> (citação curta, tipo, URL ou DOI, uso no projeto)
REFERENCIAS: dict[str, dict[str, str]] = {
    # ── Base de conhecimento do usuário (_private/kb) ───────────────────────
    "KB-SHANNON": {
        "cit": "KB do projeto — entropia de Shannon, Simpson, HHI e KPIs (ROI, payback, VI, OEE) aplicados à escolha de equipamentos",
        "tipo": "base de conhecimento", "url": "_private/kb/Além de utilidade marginal...pdf",
        "uso": "diversidade de usos/segmentos da ideia (H, Simpson, HHI); ROI, payback, índice de versatilidade",
    },
    "KB-OUTRANK": {
        "cit": "KB do projeto — outranking × utility theory em comparações sem dados",
        "tipo": "base de conhecimento", "url": "_private/kb/Diferenças entre outranking...pdf",
        "uso": "por que rodar escolas não compensatórias (ELECTRE/PROMETHEE) ao lado de MAUT",
    },
    "KB-METAPROMPT": {
        "cit": "KB do projeto — meta-prompt de durabilidade, escalabilidade e cumulatividade; TODIM fuzzy para ideias não validadas",
        "tipo": "base de conhecimento", "url": "_private/kb/Qual o MELHOR PROMPT...pdf + referencias.txt",
        "uso": "dimensões Durabilidade/Escalabilidade/Cumulatividade/Robustez/Alinhamento; teste de reversibilidade, experimento mínimo e mapa de dependências",
    },
    # ── Métodos multicritério (as 9 escolas) ────────────────────────────────
    "SAATY-1980": {"cit": "Saaty, T. L. (1980). The Analytic Hierarchy Process. McGraw-Hill.",
                   "tipo": "livro", "url": "", "uso": "AHP-TOPSIS 2n"},
    "HWANG-YOON-1981": {"cit": "Hwang, C.-L.; Yoon, K. (1981). Multiple Attribute Decision Making. Springer.",
                        "tipo": "livro", "url": "", "uso": "TOPSIS"},
    "ROY-1968": {"cit": "Roy, B. (1968). Classement et choix en présence de points de vue multiples (la méthode ELECTRE). RIRO 2(8).",
                 "tipo": "artigo", "url": "", "uso": "ELECTRE I/II — veto não compensatório"},
    "BRANS-VINCKE-1985": {"cit": "Brans, J.-P.; Vincke, Ph. (1985). A preference ranking organisation method (PROMETHEE). Management Science 31(6).",
                          "tipo": "artigo", "url": "https://doi.org/10.1287/mnsc.31.6.647", "uso": "PROMETHEE II"},
    "KEENEY-RAIFFA-1976": {"cit": "Keeney, R.; Raiffa, H. (1976). Decisions with Multiple Objectives. Wiley.",
                           "tipo": "livro", "url": "", "uso": "MAUT com aversão a risco"},
    "ENSSLIN-2001": {"cit": "Ensslin, L.; Montibeller, G.; Noronha, S. (2001). Apoio à Decisão: metodologias para estruturação de problemas. Insular.",
                     "tipo": "livro", "url": "", "uso": "MCDA-C — níveis Neutro/Bom"},
    "OPRICOVIC-TZENG-2004": {"cit": "Opricovic, S.; Tzeng, G.-H. (2004). Compromise solution by MCDM methods: VIKOR vs TOPSIS. EJOR 156(2).",
                             "tipo": "artigo", "url": "https://doi.org/10.1016/S0377-2217(03)00020-1", "uso": "VIKOR — arrependimento máximo"},
    "GOMES-LIMA-1992": {"cit": "Gomes, L. F. A. M.; Lima, M. M. P. P. (1992). TODIM: basics and application to multicriteria ranking. Found. Comput. Decision Sci. 16.",
                        "tipo": "artigo", "url": "", "uso": "TODIM — aversão à perda"},
    "KAHNEMAN-TVERSKY-1979": {"cit": "Kahneman, D.; Tversky, A. (1979). Prospect Theory. Econometrica 47(2).",
                              "tipo": "artigo", "url": "https://doi.org/10.2307/1914185", "uso": "TODIM; indicador de aversão à perda"},
    "GOMES-1997-SAPEVO": {"cit": "Gomes, L. F. A. M. et al. (1997). SAPEVO; extensão multidecisor SAPEVO-M: Teixeira, Santos & Gomes (2019).",
                          "tipo": "artigo", "url": "", "uso": "SAPEVO-M — comitê ordinal"},
    "TODIM-FUZZY-2024": {"cit": "Revisões recentes de TODIM fuzzy/linguístico para ideias sem dados (Wiley 2024, doi 10.1155/2024/3798588).",
                                "tipo": "artigo", "url": "https://onlinelibrary.wiley.com/doi/10.1155/2024/3798588", "uso": "justificativa do TODIM para ideias não validadas"},
    # ── Previsão de sucesso de startups / ideias (2023–2026) ────────────────
    "JAFARI-2025-META": {"cit": "Jafari, S. M. A.; Mobini Dehkordi, A.; Chitsaz, E.; Yaghoobzadeh, Y. (2025). What Matters Most? A Quantitative Meta-Analysis of AI-Based Predictors for Startup Success. arXiv:2507.09675.",
                         "tipo": "artigo", "url": "https://arxiv.org/abs/2507.09675",
                         "uso": "58 preditores, importância dependente de estágio — justifica pesos por estágio e a dimensão Tração Digital"},
    "JAFARI-2025-SAISE": {"cit": "Jafari, S. M. A. et al. (2025). Deconstructing the Crystal Ball: principled startup evaluation with the SAISE framework. arXiv:2508.05491.",
                          "tipo": "artigo", "url": "https://arxiv.org/abs/2508.05491",
                          "uso": "roteiro em 5 estágios: definição de sucesso por estágio, features fundamentadas em teoria, validação, interpretação ciente de risco"},
    "VCBENCH-2025": {"cit": "Chen, R. et al. (2025). VCBench: Benchmarking LLMs in Venture Capital. arXiv:2509.14448.",
                     "tipo": "artigo", "url": "https://arxiv.org/abs/2509.14448",
                     "uso": "taxa-base: precisão do índice de mercado 1,9%; YC 1,7× e fundos tier-1 2,9× o índice — mostra o teto realista de previsão"},
    "SSFF-2024": {"cit": "Universidade de Oxford & Vela Research (2024/2025). SSFF: Investigating LLM Predictive Capabilities for Startup Success through a Multi-Agent Framework. arXiv:2405.19456 (NeurIPS 2025 workshop).",
                  "tipo": "artigo", "url": "https://arxiv.org/abs/2405.19456",
                  "uso": "arquitetura previsão + análise + conhecimento externo; LLM sozinho é inferior ao híbrido ML+LLM"},
    "LLMAR-2025": {"cit": "LLM-AR: LLM-powered Automated Reasoning Framework para sucesso de startups em estágio de ideia (2025). arXiv:2510.22034.",
                   "tipo": "artigo", "url": "https://arxiv.org/abs/2510.22034",
                   "uso": "regras probabilísticas interpretáveis destiladas de LLM — inspira a agregação em log-odds explicável"},
    "VC-RAREEVENT-2025": {"cit": "From Limited Data to Rare-event Prediction: LLM-powered Feature Engineering and Multi-model Learning in Venture Capital (2025). arXiv:2509.08140.",
                          "tipo": "artigo", "url": "https://arxiv.org/abs/2509.08140",
                          "uso": "sucesso é evento raro: priors baixos e precisão relativa ao acaso como métrica honesta"},
    "KNN-ICL-2026": {"cit": "Predicting Startup Success Using Large Language Models: A Novel In-Context Learning Approach (2026). arXiv:2601.16568.",
                     "tipo": "artigo", "url": "https://arxiv.org/abs/2601.16568",
                     "uso": "previsão em cenário de poucos dados (few-shot) — base do modo 'classe de referência' sem dataset"},
    "SUST-2025-ML-IDEA": {"cit": "Conceptual Framework for a Machine Learning-Based Algorithmic Model for Early-Stage Business Idea Evaluation (2025). Sustainability 17(22):10124.",
                          "tipo": "artigo", "url": "https://doi.org/10.3390/su172210124",
                          "uso": "avaliação algorítmica de ideia em estágio inicial — enquadramento do problema"},
    "IDEA-SCREEN-LLM": {"cit": "Estudos de triagem de ideias em concursos de inovação com ML/LLM (74.436 ideias, 153 concursos; esforço de avaliação −28,4%).",
                        "tipo": "artigo", "url": "https://repositorio.uandes.cl/items/8cf83d8c-676a-4aa4-9522-d3fd63eff614",
                        "uso": "triagem automática de ideias é viável e reduz esforço de especialistas"},
    "EXPERT-DISAGREE-2026": {"cit": "Aggregate vs. Personalized Judges in Business Idea Evaluation: Evidence from Expert Disagreement (2026). arXiv:2604.22517.",
                             "tipo": "artigo", "url": "https://arxiv.org/abs/2604.22517",
                             "uso": "especialistas discordam — por isso o veredito traz probabilidade e robustez, não um número único"},
    # ── Experimentação, método científico e opções reais ───────────────────
    "KERR-NANDA-RK-2014": {"cit": "Kerr, W. R.; Nanda, R.; Rhodes-Kropf, M. (2014). Entrepreneurship as Experimentation. Journal of Economic Perspectives 28(3):25-48.",
                           "tipo": "artigo", "url": "https://www.nber.org/papers/w20358",
                           "uso": "sucesso é raro, assimétrico e só se conhece investindo em etapas — fundamenta a escada de decisão (experimento → MVP → projeto)"},
    "CAMUFFO-2020": {"cit": "Camuffo, A.; Cordova, A.; Gambardella, A.; Spina, C. (2020). A Scientific Approach to Entrepreneurial Decision Making: Evidence from a Randomized Control Trial. Management Science 66(2).",
                     "tipo": "artigo", "url": "https://doi.org/10.1287/mnsc.2018.3249",
                     "uso": "hipótese + teste rigoroso reduz falsos positivos — fundamenta 'experimento mínimo antes de tokens'"},
    "CAMUFFO-2024-SMJ": {"cit": "Camuffo, A. et al. (2024). A scientific approach to entrepreneurial decision-making: Large-scale replication and extension. Strategic Management Journal (759 firmas, 4 RCTs).",
                         "tipo": "artigo", "url": "https://repositorio.ie.edu/entities/publication/6aae4961-2c1d-45ed-97eb-e8bee19a2471",
                         "uso": "replicação: dúvida metódica é o mecanismo dominante — o analisador privilegia o veto do erro caro"},
    "DIXIT-PINDYCK-1994": {"cit": "Dixit, A.; Pindyck, R. (1994). Investment under Uncertainty. Princeton University Press.",
                           "tipo": "livro", "url": "", "uso": "opções reais: valor de esperar/experimentar; opcionalidade como critério"},
    "HOWARD-1966-VOI": {"cit": "Howard, R. A. (1966). Information Value Theory. IEEE Trans. Systems Science and Cybernetics 2(1).",
                        "tipo": "artigo", "url": "https://doi.org/10.1109/TSSC.1966.300074",
                        "uso": "EVPI — quanto vale saber antes de gastar tokens"},
    "KELLY-1956": {"cit": "Kelly, J. L. (1956). A New Interpretation of Information Rate. Bell System Technical Journal 35(4).",
                   "tipo": "artigo", "url": "https://doi.org/10.1002/j.1538-7305.1956.tb03809.x",
                   "uso": "fração de Kelly: quanto do orçamento de tokens apostar numa ideia"},
    "GOSSEN-1854": {"cit": "Gossen, H. H. (1854). Entwickelung der Gesetze des menschlichen Verkehrs (lei da utilidade marginal decrescente); Jevons (1871), Menger (1871).",
                    "tipo": "livro", "url": "",
                    "uso": "utilidade marginal do capital-token: quanto valor esperado cada real ADICIONAL de construção compra (teste → MVP → projeto)"},
    "SHANNON-1948": {"cit": "Shannon, C. E. (1948). A Mathematical Theory of Communication. Bell System Technical Journal 27.",
                     "tipo": "artigo", "url": "https://doi.org/10.1002/j.1538-7305.1948.tb01338.x",
                     "uso": "entropia de usos/segmentos e entropia de lacunas da descrição"},
    "HHI": {"cit": "Herfindahl-Hirschman Index — Hirschman (1945); Herfindahl (1950).",
            "tipo": "índice", "url": "", "uso": "concentração de usos/receita (inverso da versatilidade)"},
    # ── Planejamento, previsão e custo de software ─────────────────────────
    "FLYVBJERG-BUDZIER-2011": {"cit": "Flyvbjerg, B.; Budzier, A. (2011). Why Your IT Project May Be Riskier Than You Think. Harvard Business Review 89(9).",
                               "tipo": "artigo", "url": "https://hbr.org/2011/09/why-your-it-project-may-be-riskier-than-you-think",
                               "uso": "cauda gorda em TI: 1.471 projetos, sobrecusto médio na cauda > 400% — termo de cauda no Monte Carlo de tokens"},
    "FLYVBJERG-GARDNER-2023": {"cit": "Flyvbjerg, B.; Gardner, D. (2023). How Big Things Get Done. Currency (16.000+ projetos, 136 países).",
                               "tipo": "livro", "url": "",
                               "uso": "previsão por classe de referência (outside view); só 0,5% entregam no prazo, custo e benefício"},
    "KAHNEMAN-LOVALLO-1993": {"cit": "Kahneman, D.; Lovallo, D. (1993). Timid choices and bold forecasts. Management Science 39(1).",
                              "tipo": "artigo", "url": "https://doi.org/10.1287/mnsc.39.1.17",
                              "uso": "falácia do planejamento — priors vêm da classe de referência, não do entusiasmo do autor"},
    "BOEHM-2000-COCOMO": {"cit": "Boehm, B. et al. (2000). Software Cost Estimation with COCOMO II. Prentice Hall.",
                          "tipo": "livro", "url": "", "uso": "esforço ∝ tamanho^E com multiplicadores de complexidade"},
    "ALBRECHT-1979-FP": {"cit": "Albrecht, A. J. (1979). Measuring Application Development Productivity (Function Points). IBM.",
                         "tipo": "artigo", "url": "", "uso": "tamanho funcional estimado a partir de funcionalidades/integrações citadas no texto"},
    "BAI-2026-TOKENS": {"cit": "Bai, L.; Huang, Z.; Wang, X.; Sun, J.; Mihalcea, R.; Brynjolfsson, E.; Pentland, A.; Pei, J. (2026). How Do AI Agents Spend Your Money? Analyzing and Predicting Token Consumption in Agentic Coding Tasks. arXiv:2604.22750.",
                        "tipo": "artigo", "url": "https://arxiv.org/abs/2604.22750",
                        "uso": "tarefas agênticas consomem ~1000× mais tokens que chat; entrada domina o custo; variação de até 30× entre execuções; modelos não preveem o próprio custo (r ≤ 0,39) — calibra a dispersão do Monte Carlo"},
    "ELRAMLY-2026-ACEM": {"cit": "El-Ramly, M. (2026). ACEM: A Cost Estimation Model for Agentic Software Engineering. arXiv:2608.02582.",
                          "tipo": "artigo", "url": "https://arxiv.org/abs/2608.02582",
                          "uso": "custo = tokens + supervisão humana (HITL) + infraestrutura; Revision Factor, Context Factor e HITL Intensity Score"},
    "TOKENCAST": {"cit": "krulewis/tokencostscope (tokencast) — heurísticas de tokens por atividade de desenvolvimento agêntico (MIT).",
                  "tipo": "software", "url": "https://github.com/krulewis/tokencostscope",
                  "uso": "tabela de tokens por atividade (ler/editar/escrever arquivo, revisão, planejamento) e faixas otimista/pessimista"},
    "TOKENCOST": {"cit": "AgentOps-AI/tokencost — contagem e preço de tokens para 400+ LLMs (MIT).",
                  "tipo": "software", "url": "https://github.com/AgentOps-AI/tokencost",
                  "uso": "referência de estrutura de tabela de preços"},
    "IDEA-EVALUATOR": {"cit": "sandeepkunkunuru/idea-evaluator — RICE/WSJF/CD3/EMV, rubrica de 10 dimensões com resiliência a IA (MIT, 2026).",
                       "tipo": "software", "url": "https://github.com/sandeepkunkunuru/idea-evaluator",
                       "uso": "inspira o indicador de resiliência à comoditização por IA e a triagem RICE/EMV"},
    "PYDECISION": {"cit": "Valdecy/pyDecision — 70+ métodos MCDA, incluindo variantes fuzzy.",
                   "tipo": "software", "url": "https://github.com/Valdecy/pyDecision",
                   "uso": "conferência cruzada de métodos e caminho para variantes fuzzy"},
    "PRECOS-CLAUDE-2026": {"cit": "Tabela de preços da API Claude por milhão de tokens (cache de 25/09/2026): Fable 5.1 $10/$50; Opus 5.5 $4/$20; Sonnet 5.5 $2/$10; Haiku 4.5 $1/$5.",
                              "tipo": "tabela", "url": "https://claude.com/pricing",
                              "uso": "custo em US$ por fase e por modelo"},
    # ── Falha de startups e taxa-base ───────────────────────────────────────
    "CBINSIGHTS-FAIL": {"cit": "CB Insights — The Top Reasons Startups Fail (post-mortems; 'sem necessidade de mercado' em 35–42%; falta de caixa 29%; time errado 23%).",
                        "tipo": "relatório", "url": "https://www.cbinsights.com/research/report/startup-failure-reasons-top/",
                        "uso": "peso da dimensão Problema & Demanda e pergunta incômoda nº 1"},
    "GITHUB-FUNDING-2023": {"cit": "Estudo com 160.065 startups dos EUA (Crunchbase × GitHub): engajamento em open source aumenta a probabilidade de captação (arXiv:2309.15552).",
                            "tipo": "artigo", "url": "https://arxiv.org/abs/2309.15552",
                            "uso": "atividade pública no GitHub como sinal de tração do repositório"},
    "RIES-2011": {"cit": "Ries, E. (2011). The Lean Startup. Crown Business.",
                  "tipo": "livro", "url": "", "uso": "ciclo construir-medir-aprender; MVP como experimento"},
    "SMAA-1998": {"cit": "Lahdelma, R.; Hokkanen, J.; Salminen, P. (1998). SMAA — Stochastic multiobjective acceptability analysis. European Journal of Operational Research 106(1).",
                  "tipo": "artigo", "url": "https://doi.org/10.1016/S0377-2217(97)00163-X",
                  "uso": "índices de aceitabilidade: % do espaço de pesos (e de notas incertas) em que cada alternativa vence — base da robustez dupla"},
    "CONFORMAL-DECISAO-2025": {"cit": "Decision Theoretic Foundations for Conformal Prediction (2025). arXiv:2502.02561; Conformal Prediction and Human Decision Making (2025). arXiv:2503.11709.",
                               "tipo": "artigo", "url": "https://arxiv.org/abs/2502.02561",
                               "uso": "roteiro: calibrar o IC80 de p(viável) com predição conformal quando houver histórico de desfechos (conjuntos ótimos para decisor avesso a risco/VaR)"},
    "LLM-JUIZ-2025": {"cit": "How to Correctly Report LLM-as-a-Judge Evaluations (2025). arXiv:2511.21140 — e estudos de 2025 sobre viés de concordância (TPR > 96%, TNR < 25%) mitigado por veto de minoria.",
                      "tipo": "artigo", "url": "https://arxiv.org/abs/2511.21140",
                      "uso": "LLM não aprova ideia sozinho: o veredito é quantitativo e não compensatório (veto ELECTRE/VIKOR); o LLM entra só nas perguntas qualitativas"},
    "MCDM-STUDIO": {"cit": "MCDM Studio — Modelos Multicritério de Decisão (ProfBru © 2026): 9 escolas + consenso de Borda + robustez de Dirichlet.",
                    "tipo": "software", "url": "multicriteriadecisionmodels/",
                    "uso": "motor de decisão vendorizado em apmv/mcdm"},
}


def citar(*ids: str) -> str:
    """Devolve as citações curtas, separadas por ' · ', na ordem pedida."""
    return " · ".join(REFERENCIAS[i]["cit"].split(".")[0] for i in ids if i in REFERENCIAS)


def validar(ids: list[str]) -> list[str]:
    """Lista ids inexistentes (usado pelos testes: indicador sem fonte não entra)."""
    return [i for i in ids if i not in REFERENCIAS]
