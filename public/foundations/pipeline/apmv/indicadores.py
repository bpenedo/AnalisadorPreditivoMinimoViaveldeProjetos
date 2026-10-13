# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Catálogo de indicadores — o "painel de instrumentos" do GPS preditivo.

Cada indicador devolve três números:
  • `nota`      0..1, sempre orientada para VIABILIDADE (1 = favorável);
  • `confianca` 0..1, quanto o texto/repositório sustenta essa nota;
  • `evidencia` a frase que explica de onde a nota saiu.

Sem informação, a nota fica em 0,5 com confiança baixa — e é ISSO que aparece no
relatório. Indicador que inventa certeza é pior que indicador ausente.

Dimensões (inspiradas no meta-prompt da KB — Durabilidade, Escalabilidade,
Cumulatividade, Robustez, Alinhamento — e na literatura de avaliação de startups):

  DEM  Problema & Demanda        CB Insights: falta de mercado mata 35–42%
  MER  Mercado & Diversidade     Shannon/Simpson/HHI aplicados a usos e segmentos (KB)
  TEC  Viabilidade técnica       pontos de função, integrações, maturidade do código
  ECO  Viabilidade econômica     VPL vs CDI, payback, break-even, Kelly
  DUR  Durabilidade              resistência ao tempo e a mudanças de contexto
  ESC  Escalabilidade            custo marginal, efeito de rede, automação
  CUM  Cumulatividade            o que fica se falhar: código, dados, reputação
  ROB  Robustez & Risco          regulação, dependências externas, cauda
  ALI  Alinhamento & Testabilidade  vantagem do autor, experimento mínimo
  INF  Informação & Incerteza    completude, confiança, valor da informação
  ARB  Arbitragem financeira     (só se a ideia for estratégia financeira)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

DIMENSOES: dict[str, dict] = {
    "DEM": {"nome": "Problema & Demanda", "peso": 0.18},
    "MER": {"nome": "Mercado & Diversidade", "peso": 0.09},
    "TEC": {"nome": "Viabilidade técnica", "peso": 0.10},
    "ECO": {"nome": "Viabilidade econômica", "peso": 0.13},
    "DUR": {"nome": "Durabilidade", "peso": 0.10},
    "ESC": {"nome": "Escalabilidade", "peso": 0.09},
    "CUM": {"nome": "Cumulatividade", "peso": 0.11},
    "ROB": {"nome": "Robustez & Risco", "peso": 0.09},
    "ALI": {"nome": "Alinhamento & Testabilidade", "peso": 0.07},
    "INF": {"nome": "Informação & Incerteza", "peso": 0.04},
    "ARB": {"nome": "Arbitragem financeira", "peso": 0.00},   # ganha peso só se aplicável
}
# Dimensões que alimentam a probabilidade de viabilidade. ECO fica de fora porque
# DEPENDE dessa probabilidade (evita raciocínio circular); INF entra só como confiança.
DIMENSOES_PREDITIVAS = ("DEM", "MER", "TEC", "DUR", "ESC", "CUM", "ROB", "ALI", "ARB")


@dataclass(frozen=True)
class Indicador:
    id: str
    nome: str
    dimensao: str
    tipo: str                 # "quali" (linguístico → nota) · "quanti" (fórmula)
    formula: str
    fontes: tuple[str, ...]
    evidencia_minima: str     # o que firmaria a nota — em vez de inventar


CATALOGO: tuple[Indicador, ...] = (
    # ── DEM ─────────────────────────────────────────────────────────────────
    Indicador("DEM-01", "Severidade da dor", "DEM", "quali", "0,50 + 0,35·força(dor)",
              ("CBINSIGHTS-FAIL", "KB-METAPROMPT"), "Quanto a dor custa hoje (R$/mês ou horas/semana) para 5 clientes reais."),
    Indicador("DEM-02", "Frequência da dor", "DEM", "quali", "0,45 + 0,40·força(frequência)",
              ("CBINSIGHTS-FAIL",), "Quantas vezes por semana o cliente enfrenta o problema."),
    Indicador("DEM-03", "Disposição a pagar", "DEM", "quali", "0,40 + 0,30·força(pagamento) + 0,20·[B2B]",
              ("IDEA-EVALUATOR", "CBINSIGHTS-FAIL"), "Pré-venda, carta de intenção ou preço que 3 clientes aceitaram."),
    Indicador("DEM-04", "Evidência de demanda (validação)", "DEM", "quali", "0,30 + 0,60·força(validação)",
              ("CAMUFFO-2020", "RIES-2011"), "Lista de espera, piloto ou cliente pagante — qualquer sinal fora da cabeça do autor."),
    Indicador("DEM-05", "Clareza do cliente-alvo", "DEM", "quali", "0,35 + 0,30·[B2B] + 0,30·[B2C] (máx 0,9)",
              ("JAFARI-2025-SAISE",), "Descrição de UM cliente típico com cargo, porte e contexto."),
    # ── MER ─────────────────────────────────────────────────────────────────
    Indicador("MER-01", "Alcance de mercado", "MER", "quali", "0,45 + 0,25·[global] + 0,15·[B2B] − 0,15·[nicho]",
              ("IDEA-EVALUATOR",), "Estimativa top-down e bottom-up do mercado endereçável."),
    Indicador("MER-02", "Diversidade de usos — entropia de Shannon", "MER", "quanti", "H = −Σ pᵢ ln pᵢ sobre segmentos; nota = 0,40 + 0,50·H/ln 4",
              ("KB-SHANNON", "SHANNON-1948"), "Lista de segmentos que usariam a solução e a fração de cada um."),
    Indicador("MER-03", "Concentração de usos — HHI", "MER", "quanti", "HHI = Σ sᵢ²; nota = 1 − 0,6·HHI",
              ("KB-SHANNON", "HHI"), "Mesma lista acima; HHI alto = dependência de um único uso."),
    Indicador("MER-04", "Índice de Simpson", "MER", "quanti", "D = 1 − Σ pᵢ²; nota = 0,40 + 0,55·D",
              ("KB-SHANNON",), "Mesma lista acima."),
    Indicador("MER-06", "Índice de Versatilidade (VI)", "MER", "quanti", "VI = min(segmentos viáveis / 4, 1); nota = 0,35 + 0,60·VI (VI > 70% = robusto)",
              ("KB-SHANNON",), "Quantos segmentos distintos comprariam o mesmo núcleo."),
    Indicador("MER-05", "Pressão competitiva", "MER", "quali", "0,55 − 0,20·[concorrência citada]",
              ("IDEA-EVALUATOR",), "3 concorrentes diretos e por que o cliente trocaria."),
    # ── TEC ─────────────────────────────────────────────────────────────────
    Indicador("TEC-01", "Tamanho funcional (pontos de função)", "TEC", "quanti", "1 − 0,8·min(arquivos/80, 1)",
              ("ALBRECHT-1979-FP", "BOEHM-2000-COCOMO"), "Lista de funcionalidades do MVP (máx. 5)."),
    Indicador("TEC-02", "Dependência de integrações externas", "TEC", "quanti", "1 − 0,12·nº integrações",
              ("ELRAMLY-2026-ACEM",), "Documentação e limites de uso de cada API citada."),
    Indicador("TEC-03", "Exigência de tempo real / hardware", "TEC", "quali", "1 − 0,30·[tempo real] − 0,30·[hardware]",
              ("BOEHM-2000-COCOMO",), "Latência máxima aceitável e componentes físicos necessários."),
    Indicador("TEC-04", "Maturidade de código existente (TRL-software)", "TEC", "quanti", "maturidade do repositório (0..1); sem repo = 0,30",
              ("GITHUB-FUNDING-2023",), "Link do repositório com testes e CI."),
    Indicador("TEC-05", "Resiliência à comoditização por IA", "TEC", "quali", "1 − risco_IA(classe) + 0,15·[efeito de dados] + 0,10·[regulado]",
              ("IDEA-EVALUATOR", "VCBENCH-2025"), "Por que um chat genérico NÃO resolve o problema em 24 meses."),
    # ── ECO ─────────────────────────────────────────────────────────────────
    Indicador("ECO-01", "Custo P50 (tokens + horas)", "ECO", "quanti", "1 / (1 + custo_P50 / R$ 2.000)",
              ("BAI-2026-TOKENS", "TOKENCAST", "PRECOS-CLAUDE-2026"), "Execução piloto de 1 sessão para calibrar o consumo real."),
    Indicador("ECO-02", "Cauda de tokens (P90/P50)", "ECO", "quanti", "1 / (P90/P50)",
              ("BAI-2026-TOKENS", "FLYVBJERG-BUDZIER-2011"), "Especificação mais completa reduz a variância (Bai et al., 2026)."),
    Indicador("ECO-03", "Margem de segurança p/p*", "ECO", "quanti", "min(p_viável / p_break-even / 2, 1)",
              ("KAHNEMAN-LOVALLO-1993",), "Receita mensal realista de 3 clientes comparáveis."),
    Indicador("ECO-04", "VPL esperado vs CDI", "ECO", "quanti", "logística(VPL / custo)",
              ("DIXIT-PINDYCK-1994",), "Cenário de receita com fonte (não com esperança)."),
    Indicador("ECO-05", "Payback", "ECO", "quanti", "1 − min(meses/24, 1); sem payback em 60 meses = 0",
              ("KB-SHANNON",), "Preço × clientes no 6º mês."),
    Indicador("ECO-06", "Receita recorrente", "ECO", "quali", "0,40 + 0,50·[recorrência]",
              ("IDEA-EVALUATOR",), "Modelo de cobrança definido."),
    Indicador("ECO-07", "Fração de Kelly", "ECO", "quanti", "f* = p − (1−p)/b; nota = 0,5 + f*",
              ("KELLY-1956",), "p e b firmados por experimento."),
    Indicador("ECO-08", "Utilidade marginal do capital-token (Gossen)", "ECO", "quanti",
              "UM = ΔVE/ΔR$ do degrau MVP → projeto completo; nota = UM/(1+UM) (UM ≤ 0 → 0)",
              ("GOSSEN-1854", "KB-SHANNON", "DIXIT-PINDYCK-1994"), "Medir o uso real do MVP antes de completar o projeto."),
    # ── DUR ─────────────────────────────────────────────────────────────────
    Indicador("DUR-01", "Durabilidade da classe de referência", "DUR", "quali", "perfil da classe (outside view)",
              ("FLYVBJERG-GARDNER-2023", "KAHNEMAN-LOVALLO-1993"), "Há quantos anos o problema existe e se ainda existirá em 10."),
    Indicador("DUR-02", "Imunidade a modismo", "DUR", "quali", "1 − 0,50·força(efêmero)",
              ("KB-METAPROMPT",), "O problema existia antes da tendência atual?"),
    Indicador("DUR-03", "Independência de plataforma única", "DUR", "quali", "1 − 0,50·[plataforma única]",
              ("KB-METAPROMPT",), "Plano B se a plataforma mudar a API ou a política."),
    # ── ESC ─────────────────────────────────────────────────────────────────
    Indicador("ESC-01", "Custo marginal próximo de zero", "ESC", "quali", "0,30 + 0,50·[digital] − 0,30·[serviço humano] − 0,20·[hardware]",
              ("KB-METAPROMPT",), "Custo de atender o 1.000º cliente."),
    Indicador("ESC-02", "Efeito de rede", "ESC", "quali", "0,40 + 0,50·[rede]",
              ("KB-METAPROMPT",), "Cada novo usuário melhora o produto para os outros?"),
    Indicador("ESC-03", "Automação do processo", "ESC", "quali", "0,40 + 0,40·força(automação)",
              ("KB-METAPROMPT",), "Quais passos ainda exigem uma pessoa."),
    Indicador("ESC-04", "Escalabilidade da classe", "ESC", "quali", "perfil da classe",
              ("FLYVBJERG-GARDNER-2023",), "Casos comparáveis que escalaram."),
    # ── CUM ─────────────────────────────────────────────────────────────────
    Indicador("CUM-01", "Ativos reutilizáveis (código, componentes)", "CUM", "quali", "0,35 + 0,40·força(reuso) + 0,15·[digital]",
              ("KB-METAPROMPT", "DIXIT-PINDYCK-1994"), "Quais módulos servem a outro projeto."),
    Indicador("CUM-02", "Fosso de dados", "CUM", "quali", "0,30 + 0,40·[dados] + 0,30·[efeito de dados]",
              ("IDEA-EVALUATOR",), "Que dado proprietário cresce com o uso."),
    Indicador("CUM-03", "Reversibilidade — o que sobra se falhar", "CUM", "quali", "média(CUM-01, 0,5 + 0,3·[competência])",
              ("KB-METAPROMPT", "KERR-NANDA-RK-2014"), "Lista de skills, código, contatos e reputação que ficam."),
    Indicador("CUM-04", "Opcionalidade (pivôs possíveis)", "CUM", "quali", "0,40 + 0,30·min(segmentos/3, 1) + 0,20·[digital]",
              ("DIXIT-PINDYCK-1994",), "Dois mercados alternativos para o mesmo núcleo."),
    # ── ROB ─────────────────────────────────────────────────────────────────
    Indicador("ROB-01", "Risco regulatório", "ROB", "quali", "1 − 0,60·regulação(classe) − 0,25·[regulado]",
              ("KB-METAPROMPT",), "Parecer sobre licença/registro exigido (ANVISA, CVM, OAB, LGPD)."),
    Indicador("ROB-02", "Dependência de fatores externos", "ROB", "quali", "1 − 0,10·integrações − 0,25·[plataforma única] − 0,20·[rede]",
              ("KB-METAPROMPT",), "Mapa: o que depende só de você × do mercado, parceiros, regulação."),
    Indicador("ROB-03", "Risco de execução solo (HITL)", "ROB", "quanti", "1 − 0,15·(HIS − 1)",
              ("ELRAMLY-2026-ACEM",), "Horas semanais disponíveis e competências faltantes."),
    Indicador("ROB-04", "Perda máxima relativa (aversão à perda)", "ROB", "quanti", "1 − custo_P90 / (custo_P90 + VP_conservador)",
              ("KAHNEMAN-TVERSKY-1979", "GOMES-LIMA-1992"), "Teto de gasto aceitável se tudo der errado."),
    # ── ALI ─────────────────────────────────────────────────────────────────
    Indicador("ALI-01", "Vantagem do autor (founder-fit)", "ALI", "quali", "0,35 + 0,50·[competência]",
              ("JAFARI-2025-META", "VCBENCH-2025"), "Experiência no domínio ou acesso privilegiado aos clientes."),
    Indicador("ALI-02", "Testabilidade (experimento ≤ 5 dias)", "ALI", "quali", "0,80 se completude ≥ 50% e classe identificada; senão 0,40",
              ("CAMUFFO-2020", "CAMUFFO-2024-SMJ"), "O experimento que mataria a ideia, escrito."),
    Indicador("ALI-03", "Tempo até a 1ª evidência", "ALI", "quali", "0,80 se já há validação; 0,50 caso contrário",
              ("KERR-NANDA-RK-2014",), "Data do primeiro sinal de mercado."),
    Indicador("ALI-04", "Operação de custo zero (client-side/Colab)", "ALI", "quali", "0,50 + 0,40·[custo zero] − 0,30·[hardware]",
              ("TOKENCOST",), "Onde a solução roda e quanto custa por mês."),
    # ── INF ─────────────────────────────────────────────────────────────────
    Indicador("INF-01", "Completude da descrição", "INF", "quanti", "fração das 8 perguntas essenciais respondidas",
              ("JAFARI-2025-SAISE", "SHANNON-1948"), "Responder às lacunas listadas no relatório."),
    Indicador("INF-02", "Confiança da classe de referência", "INF", "quanti", "afinidade da classe vencedora",
              ("KAHNEMAN-LOVALLO-1993", "KNN-ICL-2026"), "Nomear o setor explicitamente."),
    Indicador("INF-03", "Valor da informação (EVPI / custo do teste)", "INF", "quanti", "min(EVPI / custo_experimento / 5, 1) — alto = testar antes compensa",
              ("HOWARD-1966-VOI",), "Rodar o experimento mínimo."),
    # ── ARB ─────────────────────────────────────────────────────────────────
    Indicador("ARB-01", "Persistência da vantagem (decaimento de alfa)", "ARB", "quali", "0,30 + 0,20·[backtest] (arbitragem decai por construção)",
              ("KERR-NANDA-RK-2014",), "Resultado fora da amostra (walk-forward) por ≥ 3 meses."),
    Indicador("ARB-02", "Custos de transação e latência", "ARB", "quali", "0,45 − 0,20·[tempo real]",
              ("FLYVBJERG-BUDZIER-2011",), "Spread médio × (corretagem + slippage + imposto)."),
    Indicador("ARB-03", "Validação estatística (backtest, Sharpe, drawdown)", "ARB", "quali", "0,25 + 0,55·força(backtest)",
              ("CAMUFFO-2020",), "Sharpe > 1 e drawdown máximo documentados."),
    Indicador("ARB-04", "Exposição regulatória financeira (CVM/BACEN)", "ARB", "quali", "0,65 − 0,40·[recursos de terceiros]",
              ("KB-METAPROMPT",), "Operar só capital próprio ou ter registro."),
)
CATALOGO_POR_ID = {i.id: i for i in CATALOGO}


@dataclass
class Medida:
    nota: float
    confianca: float
    evidencia: str


def _dec(v: float, casas: int) -> str:
    """Número PT-BR: vírgula decimal, ponto de milhar (BUG-009 — vale também para evidências)."""
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _clip(x: float, lo: float = 0.02, hi: float = 0.98) -> float:
    return max(lo, min(hi, x))


def diversidade(segmentos: dict[str, int]) -> dict[str, float]:
    """Shannon H, H normalizada, Simpson D e HHI dos segmentos detectados (KB-SHANNON)."""
    total = sum(segmentos.values())
    if total == 0:
        return {"H": 0.0, "H_norm": 0.0, "simpson": 0.0, "hhi": 1.0, "riqueza": 0}
    p = [n / total for n in segmentos.values()]
    h = -sum(x * math.log(x) for x in p if x > 0)
    return {"H": h, "H_norm": min(h / math.log(4), 1.0), "simpson": 1 - sum(x * x for x in p),
            "hhi": sum(x * x for x in p), "riqueza": len(p)}


def medir_qualitativos(s, tamanho, repo=None) -> dict[str, Medida]:
    """Indicadores que dependem só do texto, da classe e do repositório (não do financeiro)."""
    c, cl = s.contagens, s.classe
    t = lambda k: 1.0 if c.get(k, 0) else 0.0          # noqa: E731
    conf_txt = lambda *ks: 0.35 + 0.45 * max(t(k) for k in ks)   # noqa: E731
    ev = lambda k: ("“" + ", ".join(s.evidencias[k]) + "”") if k in s.evidencias else "sem menção no texto"  # noqa: E731
    div = diversidade(s.segmentos)
    m: dict[str, Medida] = {}
    m["DEM-01"] = Medida(_clip(0.50 + 0.35 * s.forca("dor")), conf_txt("dor"), ev("dor"))
    m["DEM-02"] = Medida(_clip(0.45 + 0.40 * s.forca("frequencia")), conf_txt("frequencia"), ev("frequencia"))
    m["DEM-03"] = Medida(_clip(0.40 + 0.30 * s.forca("pagamento") + 0.20 * t("b2b")), conf_txt("pagamento", "b2b"), ev("pagamento"))
    m["DEM-04"] = Medida(_clip(0.30 + 0.60 * s.forca("validacao", 2)), 0.40 + 0.50 * t("validacao"), ev("validacao"))
    m["DEM-05"] = Medida(_clip(min(0.35 + 0.30 * t("b2b") + 0.30 * t("b2c"), 0.90)), conf_txt("b2b", "b2c"),
                         ev("b2b") if "b2b" in s.evidencias else ev("b2c"))
    m["MER-01"] = Medida(_clip(0.45 + 0.25 * t("global") + 0.15 * t("b2b") - 0.15 * t("nicho")), conf_txt("global", "nicho", "b2b"), ev("global"))
    rot_seg = ", ".join(f"{k}={v}" for k, v in s.segmentos.items()) or "nenhum segmento detectado"
    conf_div = 0.25 + 0.15 * min(div["riqueza"], 4)
    m["MER-02"] = Medida(_clip(0.40 + 0.50 * div["H_norm"]), conf_div, "H = " + f"{abs(div['H']):.2f}".replace(".", ",") + f" ({rot_seg})")
    m["MER-03"] = Medida(_clip(1 - 0.60 * div["hhi"]), conf_div, "HHI = " + f"{div['hhi']:.2f}".replace(".", ","))
    m["MER-04"] = Medida(_clip(0.40 + 0.55 * div["simpson"]), conf_div, "Simpson D = " + f"{div['simpson']:.2f}".replace(".", ","))
    vi = min(div["riqueza"] / 4, 1.0)
    m["MER-06"] = Medida(_clip(0.35 + 0.60 * vi), conf_div, f"VI = {vi:.0%} ({div['riqueza']} segmento(s) viável(is))")
    m["MER-05"] = Medida(_clip(0.55 - 0.20 * t("concorrencia")), conf_txt("concorrencia"), ev("concorrencia"))
    m["TEC-01"] = Medida(_clip(1 - 0.8 * min(tamanho.arquivos_novos / 80, 1)), 0.55,
                         f"{tamanho.arquivos_novos} arquivos estimados ({tamanho.funcionalidades} funcionalidades)")
    m["TEC-02"] = Medida(_clip(1 - 0.12 * tamanho.integracoes), 0.6, ev("integracao"))
    m["TEC-03"] = Medida(_clip(1 - 0.30 * t("tempo_real") - 0.30 * t("hardware")), conf_txt("tempo_real", "hardware"),
                         ev("tempo_real") if "tempo_real" in s.evidencias else ev("hardware"))
    if repo is not None:
        m["TEC-04"] = Medida(_clip(repo.maturidade), 0.85, f"repositório {repo.nome}: {repo.loc_total:,} linhas, nível {repo.trl}")
    else:
        m["TEC-04"] = Medida(0.30, 0.90, "nenhum código existente informado — parte do zero")
    m["TEC-05"] = Medida(_clip(1 - cl.comoditizacao_ia + 0.15 * t("efeito_dados") + 0.10 * t("regulado")), 0.5,
                         f"classe “{cl.rotulo}”, risco de comoditização {cl.comoditizacao_ia:.0%}")
    m["DUR-01"] = Medida(_clip(cl.durabilidade), 0.5, f"perfil da classe “{cl.rotulo}”")
    m["DUR-02"] = Medida(_clip(1 - 0.50 * s.forca("efemero")), conf_txt("efemero"), ev("efemero"))
    m["DUR-03"] = Medida(_clip(1 - 0.50 * t("plataforma_unica")), conf_txt("plataforma_unica"), ev("plataforma_unica"))
    m["ESC-01"] = Medida(_clip(0.30 + 0.50 * t("digital") - 0.30 * t("escala_humana") - 0.20 * t("hardware")),
                         conf_txt("digital", "escala_humana"), ev("digital"))
    m["ESC-02"] = Medida(_clip(0.40 + 0.50 * t("rede")), conf_txt("rede"), ev("rede"))
    m["ESC-03"] = Medida(_clip(0.40 + 0.40 * s.forca("automacao", 2)), conf_txt("automacao"), ev("automacao"))
    m["ESC-04"] = Medida(_clip(cl.escalabilidade), 0.5, f"perfil da classe “{cl.rotulo}”")
    cum1 = _clip(0.35 + 0.40 * s.forca("reuso", 2) + 0.15 * t("digital"))
    m["CUM-01"] = Medida(cum1, conf_txt("reuso", "digital"), ev("reuso"))
    m["CUM-02"] = Medida(_clip(0.30 + 0.40 * t("dados") + 0.30 * t("efeito_dados")), conf_txt("dados", "efeito_dados"), ev("dados"))
    m["CUM-03"] = Medida(_clip((cum1 + 0.5 + 0.3 * t("competencia")) / 2), 0.5,
                         "código/skills reaproveitáveis + aprendizado do domínio")
    m["CUM-04"] = Medida(_clip(0.40 + 0.30 * min(len(s.segmentos) / 3, 1) + 0.20 * t("digital")), 0.45,
                         f"{len(s.segmentos)} segmento(s) de uso detectado(s)")
    m["ROB-01"] = Medida(_clip(1 - 0.60 * cl.regulacao - 0.25 * t("regulado")), conf_txt("regulado"), ev("regulado"))
    m["ROB-02"] = Medida(_clip(1 - 0.10 * tamanho.integracoes - 0.25 * t("plataforma_unica") - 0.20 * t("rede")), 0.55,
                         f"{tamanho.integracoes} " + ("integração externa" if tamanho.integracoes == 1 else "integrações externas"))
    m["ROB-03"] = Medida(_clip(1 - 0.15 * (tamanho.his - 1)), 0.6, f"HITL Intensity Score {tamanho.his}/4")
    m["ALI-01"] = Medida(_clip(0.35 + 0.50 * t("competencia")), conf_txt("competencia"), ev("competencia"))
    testavel = s.completude >= 0.5 and cl.nome != "generico"
    m["ALI-02"] = Medida(0.80 if testavel else 0.40, 0.6,
                         "experimento mínimo formulável" if testavel else "ideia ainda abstrata demais para um teste de 5 dias")
    m["ALI-03"] = Medida(0.80 if t("validacao") else 0.50, conf_txt("validacao"), ev("validacao"))
    m["ECO-06"] = Medida(_clip(0.40 + 0.50 * t("recorrencia")), conf_txt("recorrencia", "pagamento"), ev("recorrencia"))
    m["ALI-04"] = Medida(_clip(0.50 + 0.40 * t("custo_zero") - 0.30 * t("hardware")), conf_txt("custo_zero"), ev("custo_zero"))
    m["INF-01"] = Medida(_clip(s.completude, 0.0, 1.0), 1.0,
                         f"{round(s.completude * 8)}/8 perguntas essenciais respondidas")
    afin = max(s.afinidade_classes.values()) if s.afinidade_classes else 0.0
    m["INF-02"] = Medida(_clip(afin if cl.nome != "generico" else 0.1), 1.0,
                         ", ".join(f"{k} {v:.0%}" for k, v in list(s.afinidade_classes.items())[:3]))
    if s.tem("arbitragem"):
        m["ARB-01"] = Medida(_clip(0.30 + 0.20 * t("backtest")), 0.6, "vantagem de arbitragem decai quando é descoberta")
        m["ARB-02"] = Medida(_clip(0.45 - 0.20 * t("tempo_real")), 0.5, ev("tempo_real"))
        m["ARB-03"] = Medida(_clip(0.25 + 0.55 * s.forca("backtest", 2)), conf_txt("backtest"), ev("backtest"))
        m["ARB-04"] = Medida(_clip(0.65 - 0.40 * t("terceiros")), conf_txt("terceiros"), ev("terceiros"))
    return m


def medir_economicos(m: dict[str, Medida], est, fin) -> dict[str, Medida]:
    """Indicadores que dependem do estimador de tokens e da análise financeira."""
    c50 = fin.custo_total["p50"]
    m["ECO-01"] = Medida(_clip(1 / (1 + c50 / 2000)), 0.6, "R$ " + _dec(c50, 0) + " (tokens R$ " + _dec(fin.custo_tokens_brl["p50"], 0) + " + horas R$ " + _dec(fin.custo_horas_brl["p50"], 0) + ")")
    m["ECO-02"] = Medida(_clip(1 / est.cauda_p90_sobre_p50), 0.7, "P90/P50 = " + _dec(est.cauda_p90_sobre_p50, 1) + "×")
    m["ECO-03"] = Medida(_clip(min(fin.margem_seguranca / 2, 1)), 0.45,
                         f"p necessária {fin.p_breakeven:.0%} · margem " + _dec(fin.margem_seguranca, 2) + "×")
    m["ECO-04"] = Medida(_clip(1 / (1 + math.exp(-fin.vpl_esperado / max(c50, 1)))), 0.45, "VPL esperado R$ " + _dec(fin.vpl_esperado, 0))
    pb = fin.payback_meses
    m["ECO-05"] = Medida(_clip(0.0 if pb is None else 1 - min(pb / 24, 1)), 0.4,
                         "sem payback em 60 meses (cenário conservador)" if pb is None else f"{pb:.0f} meses (cenário conservador)")
    m["ECO-07"] = Medida(_clip(0.5 + fin.kelly), 0.4, "f* = " + ("+" if fin.kelly >= 0 else "") + _dec(fin.kelly, 2))
    # UM do primeiro degrau da fronteira eficiente: o valor do 1º real que sai do CDI.
    degraus = list(fin.utilidade_marginal.items())
    if degraus:
        rot, um = degraus[0]
        txt = f"{rot}: R$ " + f"{um:.2f}".replace(".", ",") + " de valor esperado por R$ adicional"
    else:
        um, txt = 0.0, "nenhuma rota de investimento na fronteira eficiente — o CDI domina"
    m["ECO-08"] = Medida(_clip(um / (1 + um) if um > 0 else 0.0), 0.45, txt)
    m["ROB-04"] = Medida(_clip(1 - fin.custo_total["p90"] / (fin.custo_total["p90"] + max(fin.vp_receita_cons, 1))), 0.5,
                         "perda máxima P90 R$ " + _dec(fin.custo_total["p90"], 0))
    m["INF-03"] = Medida(_clip(min(fin.evpi / max(fin.custo_experimento, 1) / 5, 1), 0.0, 1.0), 0.6,
                         "EVPI R$ " + _dec(fin.evpi, 0) + " vs experimento R$ " + _dec(fin.custo_experimento, 0))
    return m


def notas_por_dimensao(m: dict[str, Medida]) -> dict[str, dict]:
    """Média ponderada pela confiança, por dimensão, + confiança média."""
    out = {}
    for d in DIMENSOES:
        itens = [(mid, v) for mid, v in m.items() if CATALOGO_POR_ID[mid].dimensao == d]
        if not itens:
            continue
        pesos = sum(v.confianca for _, v in itens) or 1.0
        out[d] = {"nota": sum(v.nota * v.confianca for _, v in itens) / pesos,
                  "confianca": sum(v.confianca for _, v in itens) / len(itens),
                  "n": len(itens)}
    return out
