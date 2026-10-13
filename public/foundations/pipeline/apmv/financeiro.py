# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Tokens são capital. Este módulo compara gastá-los na ideia com as alternativas.

A pergunta errada é "a ideia é boa?". A certa é: **dado o que eu sei hoje, gastar
R$ X em tokens e horas nesta ideia rende mais do que deixar o mesmo dinheiro no
CDI — ou do que gastar uma fração dele para saber mais antes?**

Ferramentas, cada uma com a sua fonte:
  • VPL descontado pelo CDI (custo de oportunidade do capital-token);
  • probabilidade de break-even p* = custo / VP(receitas) — a ideia precisa de
    p_viável > p* para valer a pena; a razão p_viável / p* é a margem de segurança;
  • EVPI — valor esperado da informação perfeita (Howard, 1966): quanto vale saber
    o resultado ANTES de investir; se o experimento mínimo custa menos que o EVPI,
    testar primeiro domina;
  • opções reais (Dixit & Pindyck, 1994; Kerr, Nanda & Rhodes-Kropf, 2014): investir
    em etapas (experimento → MVP → projeto) compra o direito de parar;
  • fração de Kelly (Kelly, 1956): quanto do orçamento mensal de tokens apostar.

Os cenários de receita vêm da classe de referência (ou do usuário, via parâmetro) e
são HIPÓTESES declaradas no relatório — nunca fatos.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

# ── Parâmetros padrão (todos sobrescrevíveis pela CLI) ──────────────────────
CAMBIO_BRL = 5.50          # R$/US$ — atualize com --cambio
CDI_ANUAL = 0.14           # atualize com --cdi (fração ao ano)
HORIZONTE_MESES = 12
VALOR_HORA = 80.0          # R$/h do autor — custo de oportunidade do tempo
RAMPA_MESES = 6            # receita cresce linearmente até o patamar em 6 meses
ACURACIA_EXPERIMENTO = 0.75  # sensibilidade = especificidade do experimento mínimo
HORAS_EXPERIMENTO = 10.0   # ~5 dias × 2 h
CUSTO_FIXO_EXPERIMENTO = 50.0  # R$ (anúncio, domínio, landing)
FRACAO_MVP = 0.35          # MVP enxuto custa ~35% do projeto completo
ACURACIA_MVP = 0.85
CUSTO_OPERACAO_MES = 0.0   # infraestrutura: zero-cost por padrão (D27); declarar se houver VPS
MESES_ATE_DESISTIR = 3     # se não funcionar, quanto tempo se opera antes de perceber e parar

# Operar o negócio custa — e é o custo que a planilha de tokens esquece (BUG-006).
# classe -> (horas/mês do autor para vender, atender e manter; margem de contribuição)
# Ordens de grandeza declaradas e calibráveis (ADR-002): serviço/marketplace exigem
# mais horas; software puro tem margem alta; produto físico, margem baixa.
OPERACAO = {
    "automacao_interna": (4, 0.95), "saas_b2b": (30, 0.80), "ferramenta_dev": (15, 0.85),
    "marketplace": (60, 0.60), "app_consumo": (40, 0.70), "fintech_trading": (15, 0.90),
    "conteudo_educacao": (25, 0.85), "ecommerce": (40, 0.25), "saude_regulado": (40, 0.75),
    "ia_wrapper": (20, 0.65), "hardware_iot": (50, 0.35), "generico": (30, 0.70),
}


@dataclass
class Premissas:
    cambio: float = CAMBIO_BRL
    cdi_anual: float = CDI_ANUAL
    horizonte_meses: int = HORIZONTE_MESES
    valor_hora: float = VALOR_HORA
    receita_mensal_cons: float | None = None
    receita_mensal_otim: float | None = None
    custo_operacao_mes: float = CUSTO_OPERACAO_MES
    capital_trading: float | None = None


@dataclass
class Rota:
    codigo: str
    nome: str
    custo: float                 # R$ comprometidos
    valor_esperado: float        # R$ líquidos (VPL esperado)
    p_perda_total: float         # probabilidade de perder tudo que foi comprometido
    tempo_ate_evidencia_dias: float
    reversibilidade: float       # 0..1 — quanto do gasto vira ativo reutilizável
    descricao: str


@dataclass
class AnaliseFinanceira:
    premissas: Premissas
    custo_tokens_brl: dict
    custo_horas_brl: dict
    custo_total: dict             # p50/p90 — CONSTRUIR (tokens + horas)
    custo_operar: float           # R$ no horizonte, se lançar (horas do autor + infraestrutura)
    custo_desistir: float         # R$ de operação perdidos até perceber que não funciona
    margem_contribuicao: float
    vp_receita_cons: float
    vp_receita_otim: float
    vp_receita_esperado: float
    vpl_esperado: float
    roi_esperado: float
    payback_meses: float | None
    p_breakeven: float
    margem_seguranca: float
    custo_oportunidade_cdi: float
    evpi: float
    custo_experimento: float
    kelly: float
    utilidade_marginal: dict = field(default_factory=dict)   # degrau da fronteira -> R$ de valor por R$ adicional
    rotas_dominadas: list = field(default_factory=list)       # rotas fora da fronteira eficiente (renunciar)
    rotas: list[Rota] = field(default_factory=list)
    alertas_arbitragem: list[str] = field(default_factory=list)

    def como_dict(self) -> dict:
        d = asdict(self)
        return d


def _vp_receita(mensal: float, p: Premissas) -> float:
    """VP das receitas com rampa linear e desconto mensal pelo CDI."""
    i = (1 + p.cdi_anual) ** (1 / 12) - 1
    vp = 0.0
    for m in range(1, p.horizonte_meses + 1):
        fluxo = mensal * min(1.0, m / RAMPA_MESES) - p.custo_operacao_mes
        vp += fluxo / (1 + i) ** m
    return vp


def _payback(receita_liquida: float, custo_mes: float, custo: float, p: Premissas) -> float | None:
    """Meses até o fluxo acumulado (receita com rampa − operação) pagar a construção."""
    acumulado = 0.0
    for m in range(1, 61):
        acumulado += receita_liquida * min(1.0, m / RAMPA_MESES) - custo_mes - p.custo_operacao_mes
        if acumulado >= custo:
            return float(m)
    return None


def fronteira_incremental(rotas: list) -> tuple[dict, list]:
    """Utilidade marginal (Gossen, 1854) sobre a FRONTEIRA EFICIENTE das rotas.

    Análise incremental clássica (a mesma lógica do ICER em avaliação econômica):
      1. ordena por capital comprometido;
      2. remove dominância forte (custa mais e vale menos que outra);
      3. remove dominância estendida (razão incremental que CRESCE: a fronteira tem de
         ser côncava — utilidade marginal decrescente);
      4. utilidade marginal de cada degrau = ΔValor esperado / ΔCapital.
    Devolve ({"A0→A2": UM, ...}, [rotas dominadas — candidatas à renúncia]).
    """
    pts = sorted(rotas, key=lambda r: (r.custo, -r.valor_esperado))
    dominadas = [r.codigo for r in pts if any(o is not r and o.custo <= r.custo and o.valor_esperado >= r.valor_esperado
                                              and (o.custo < r.custo or o.valor_esperado > r.valor_esperado) for o in pts)]
    front = [r for r in pts if r.codigo not in dominadas]
    mudou = True
    while mudou and len(front) > 2:
        mudou = False
        razoes = [(b.valor_esperado - a.valor_esperado) / max(b.custo - a.custo, 1e-9) for a, b in zip(front, front[1:])]
        for i in range(1, len(razoes)):
            if razoes[i] > razoes[i - 1]:              # ponto do meio fica abaixo da corda
                dominadas.append(front[i].codigo)
                del front[i]
                mudou = True
                break
    um = {f"{a.codigo}→{b.codigo}": (b.valor_esperado - a.valor_esperado) / max(b.custo - a.custo, 1e-9)
          for a, b in zip(front, front[1:])}
    return um, sorted(dominadas)


def analisar(est_tokens, p_viavel: float, sinais, repo=None, premissas: Premissas | None = None) -> AnaliseFinanceira:
    p = premissas or Premissas()
    cl = sinais.classe
    tok = {q: est_tokens.custo_usd["rota_recomendada"][q] * p.cambio for q in ("p50", "p90")}
    hor = {q: est_tokens.horas_humanas[q] * p.valor_hora for q in ("p50", "p90")}
    custo = {q: tok[q] + hor[q] for q in ("p50", "p90")}
    c = custo["p50"]
    r_cons = p.receita_mensal_cons if p.receita_mensal_cons is not None else cl.receita_mensal_cons
    r_otim = p.receita_mensal_otim if p.receita_mensal_otim is not None else cl.receita_mensal_otim
    if sinais.tem("arbitragem") and p.capital_trading:
        # Para estratégia financeira, a "receita" é retorno sobre o capital alocado:
        # cenário conservador 0,5% a.m. líquido, otimista 2% a.m. (hipóteses declaradas).
        r_cons, r_otim = p.capital_trading * 0.005, p.capital_trading * 0.02
    horas_mes, margem_c = OPERACAO.get(cl.nome, OPERACAO["generico"])
    vp_c = _vp_receita(r_cons, p) * margem_c
    vp_o = _vp_receita(r_otim, p) * margem_c
    vp = 0.7 * vp_c + 0.3 * vp_o          # média ponderada conservadora (margem já aplicada)
    oper = (horas_mes * p.valor_hora + p.custo_operacao_mes) * p.horizonte_meses
    desistir = oper * MESES_ATE_DESISTIR / p.horizonte_meses
    # Projeto completo: constrói (c), opera; se falhar, perde c + `desistir`.
    ganho = vp - oper - c                                  # lucro líquido no sucesso
    vpl = p_viavel * (vp - oper) - (1 - p_viavel) * desistir - c
    risco = c + desistir                                   # o que se perde no fracasso
    p_be = min(1.0, risco / (vp - oper + desistir)) if vp - oper + desistir > 0 else 1.0
    margem = p_viavel / p_be if p_be > 0 else float("inf")
    oportunidade = c * ((1 + p.cdi_anual) ** (p.horizonte_meses / 12) - 1)
    # EVPI (Howard, 1966): com informação perfeita só se entra quando dá certo.
    evpi = p_viavel * max(ganho, 0.0) - max(vpl, 0.0)
    c_exp = HORAS_EXPERIMENTO * p.valor_hora + CUSTO_FIXO_EXPERIMENTO
    # Kelly: aposta = o que se perde no fracasso; ganho líquido b = lucro / aposta.
    b = ganho / risco if risco > 0 else 0.0
    kelly = (p_viavel - (1 - p_viavel) / b) if b > 0 else -1.0

    def rota_condicional(custo_inicial: float, acuracia: float, custo_restante: float) -> float:
        """Paga `custo_inicial`; segue (pagando o resto) só se o sinal for positivo."""
        acerto = p_viavel * acuracia * (vp - oper - custo_restante)
        falso_positivo = (1 - p_viavel) * (1 - acuracia) * (custo_restante + desistir)
        return -custo_inicial + acerto - falso_positivo

    mat = repo.maturidade if repo is not None else 0.0
    rev_base = 0.25 + 0.35 * sinais.forca("reuso", 2) + 0.2 * mat
    rotas = [
        # VPL já desconta pelo CDI: VPL > 0 significa "bate o CDI". Logo a rota A0 vale
        # 0 nessa régua — e nunca aprende nada (tempo até evidência = 1 ano).
        Rota("A0", "Não investir agora — capital no CDI", 0.0, 0.0, 0.0, 365.0, 1.0,
             f"Rende R$ {oportunidade:,.0f} certos no CDI em {p.horizonte_meses} meses; é a régua que a ideia precisa bater."),
        Rota("A1", "Experimento mínimo (≤ 5 dias) antes de qualquer token de código", c_exp,
             rota_condicional(c_exp, ACURACIA_EXPERIMENTO, c),
             (1 - p_viavel) * (1 - ACURACIA_EXPERIMENTO), 5.0, 0.55,
             "Compra informação barata (opção real): só se gasta o projeto se o teste der positivo."),
        Rota("A2", "MVP enxuto (≈35% do projeto) e decisão no meio", FRACAO_MVP * c,
             rota_condicional(FRACAO_MVP * c, ACURACIA_MVP, (1 - FRACAO_MVP) * c),
             (1 - p_viavel) * (1 - ACURACIA_MVP) + (1 - p_viavel) * ACURACIA_MVP * 0.5, 21.0, rev_base + 0.10,
             "Constrói o núcleo, mede uso real e decide se completa — perde no máximo o MVP."),
        Rota("A3", "Projeto completo agora", c, vpl, 1 - p_viavel, 45.0 + 15 * est_tokens.tamanho.sessoes, rev_base,
             "Gasta tudo antes de saber; só domina quando a evidência já é forte."),
    ]
    if repo is not None or sinais.tem("reuso") or cl.nome == "ferramenta_dev":
        fator = (1 - mat) if repo is not None else 0.6
        c4 = c * max(fator, 0.15)
        rotas.append(Rota("A4", "Reaproveitar/forkar código existente (repositório ou open source)", c4,
                          p_viavel * (vp - oper) - (1 - p_viavel) * desistir - c4, 1 - p_viavel, 14.0,
                          min(1.0, rev_base + 0.2),
                          "Parte do que existe: menos tokens de código, mais leitura; exige licença compatível."))
    for r in rotas[1:]:
        r.valor_esperado = max(r.valor_esperado, -(r.custo + desistir))   # perda limitada

    um, dominadas = fronteira_incremental(rotas)

    alertas = []
    if sinais.tem("arbitragem"):
        alertas = [
            "Arbitragem decai: a vantagem some quando outros a exploram — exija prova fora da amostra (walk-forward), não só backtest.",
            "Custos de transação (corretagem, spread, slippage, IR de 15–22,5% sobre ganho de capital) costumam anular spreads < 0,5%.",
            "Operar recursos de terceiros ou oferecer recomendação exige registro na CVM; bot próprio com capital próprio, não.",
            "Dimensione o capital pelo critério de Kelly fracionado (½ Kelly) sobre a estratégia — nunca pelo entusiasmo.",
            "Exija Sharpe > 1 e drawdown máximo compatível com o orçamento antes de gastar tokens em produto.",
        ]
    return AnaliseFinanceira(p, tok, hor, custo, oper, desistir, margem_c, vp_c, vp_o, vp, vpl,
                             vpl / (c + desistir) if c else 0.0, _payback(r_cons * margem_c, horas_mes * p.valor_hora, c, p),
                             p_be, margem,
                             oportunidade, evpi, c_exp, kelly, um, dominadas, rotas, alertas)
