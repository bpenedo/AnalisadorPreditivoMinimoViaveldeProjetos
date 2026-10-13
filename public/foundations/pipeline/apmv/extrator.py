# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Extrator de sinais: de UMA frase de ideia a um vetor de evidências auditável.

O problema que este módulo resolve é o caso mais difícil do projeto: a ideia chega
sem nicho, sem setor, sem números — às vezes uma frase só. Não dá para "prever" a
partir do nada, e o módulo não finge que dá. Ele faz três coisas honestas:

1. **Detecta sinais** por léxico PT/EN (regex com fronteira de palavra). Cada sinal
   guarda AS PALAVRAS que o dispararam — o relatório mostra a evidência, não só a nota.
2. **Classifica a classe de referência** (outside view de Kahneman & Lovallo, 1993;
   Flyvbjerg, 2023): a ideia herda os priors da classe de projetos parecidos, em vez
   do entusiasmo de quem a escreveu.
3. **Mede a própria ignorância**: completude da descrição (quantas das perguntas
   essenciais o texto responde). Pouca informação ⇒ confiança baixa ⇒ o veredito
   empurra para "teste antes de gastar tokens", nunca para "invista".

Determinístico e sem rede: a mesma frase gera sempre o mesmo vetor.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

# ─────────────────────────────────────────────────────────────────────────────
# Léxico de sinais — PT-BR e EN. Fronteira de palavra à esquerda; à direita o
# radical pode continuar (automatiz → automatizar/automatização).
# ─────────────────────────────────────────────────────────────────────────────
SINAIS: dict[str, list[str]] = {
    "dor": [r"dor", r"problema", r"perd[ae]", r"prejuizo", r"multa", r"demora", r"lent[oa]",
            r"manual", r"retrabalho", r"erro", r"car[oa]s?\b", r"desperdic", r"gargalo", r"atras",
            r"pain", r"problem", r"waste", r"slow", r"costly", r"tedious", r"burocra", r"dificil", r"complicad"],
    "frequencia": [r"diari", r"todo dia", r"todos os dias", r"semanal", r"recorrente", r"toda vez",
                   r"sempre que", r"daily", r"weekly", r"recurring", r"mensal", r"constante"],
    "pagamento": [r"assinatura", r"mensalidade", r"cobrar", r"vender", r"venda", r"preco", r"r\$",
                  r"pagar", r"comissao", r"taxa", r"subscription", r"pricing", r"\bfee", r"monetiz",
                  r"receita", r"lucro", r"faturar", r"licenc", r"freemium", r"premium"],
    "b2b": [r"empresa", r"pme", r"smb", r"b2b", r"corporativ", r"negocio", r"clinica", r"escritorio",
            r"industria", r"varejo", r"loja", r"enterprise", r"comercio", r"restaurante", r"oficina",
            r"contador", r"advogad", r"consultorio", r"academia", r"escola", r"hospital", r"fabrica"],
    "b2c": [r"consumidor", r"pessoas", r"usuario final", r"b2c", r"jovens", r"familias", r"estudantes",
            r"pais\b", r"maes", r"idosos", r"gamers", r"motoristas", r"pacientes", r"consumers"],
    "digital": [r"app", r"aplicativo", r"saas", r"plataforma", r"\bapi", r"\bweb", r"online", r"software",
                r"digital", r"cloud", r"nuvem", r"site", r"sistema", r"ferramenta", r"extensao", r"bot", r"robo"],
    "rede": [r"marketplace", r"comunidade", r"rede social", r"convid", r"network", r"two.sided",
             r"compradores e vendedores", r"conecta[r]? (pessoas|clientes|profissionais)", r"matching", r"intermedia"],
    "dados": [r"dados", r"dataset", r"base de dados", r"historico", r"coleta", r"analytics", r"\bdata\b",
              r"metricas", r"indicadores", r"dashboard", r"relatorio"],
    "ia": [r"\bia\b", r"inteligencia artificial", r"\bllm", r"\bgpt", r"claude", r"chatbot", r"agente",
           r"machine learning", r"aprendizado de maquina", r"\bai\b", r"generativ", r"modelo de linguagem", r"rag\b"],
    "integracao": [r"\bapi", r"integra", r"whatsapp", r"telegram", r"stripe", r"\bpix", r"mercado livre",
                   r"shopee", r"\bb3\b", r"binance", r"\berp", r"\bcrm", r"\bsap\b", r"google", r"instagram",
                   r"webhook", r"open finance", r"nota fiscal", r"\bnfe?\b", r"sefaz", r"gmail", r"slack", r"hubspot"],
    "regulado": [r"saude", r"medic", r"paciente", r"anvisa", r"\bcvm", r"banco central", r"bacen",
                 r"investiment", r"credito", r"emprestimo", r"\blgpd", r"dados pessoais", r"juridic",
                 r"seguro", r"crianca", r"apostas", r"\bbet\b", r"cassino", r"remedio", r"receita medica",
                 r"diagnostic", r"previdenc", r"tribut", r"fiscal", r"\bhipaa", r"\bgdpr"],
    "arbitragem": [r"arbitragem", r"trading", r"\btrade", r"robo (de )?investiment", r"bot de trading", r"cripto",
                   r"bitcoin", r"forex", r"day ?trade", r"\bacoes\b", r"opcoes", r"spread", r"hedge",
                   r"dropshipping", r"revenda", r"revender", r"diferenca de preco", r"\bflip", r"ganho de capital",
                   r"mini ?indice", r"mini ?dolar", r"\bexpert advisor", r"\bea\b", r"\bmt[45]\b", r"metatrader",
                   r"prop ?firm", r"ftmo", r"futuros", r"defi\b", r"staking", r"yield"],
    "hardware": [r"hardware", r"sensor", r"\biot", r"dispositivo", r"arduino", r"raspberry", r"impressora",
                 r"maquina", r"drone", r"robo fisico", r"wearable", r"embarcad", r"esp32"],
    "efemero": [r"tendencia", r"viral", r"\bhype", r"\bmoda\b", r"\btrend", r"\bmeme", r"temporada",
                r"copa do mundo", r"eleic", r"black friday", r"carnaval", r"natal"],
    "plataforma_unica": [r"plugin d[oa]", r"extensao do chrome", r"depende d[oa]", r"so no instagram",
                         r"apenas no (instagram|tiktok|whatsapp)", r"shopify app", r"app da shopify",
                         r"\bgpt store", r"custom gpt", r"api d[oa] (twitter|x|instagram|whatsapp)"],
    "automacao": [r"automatiz", r"\brpa\b", r"workflow", r"pipeline", r"agendad", r"\bcron", r"scraping",
                  r"raspagem", r"extrair", r"preencher automaticamente", r"automation"],
    "conteudo": [r"curso", r"aula", r"conteudo", r"\bblog", r"newsletter", r"video", r"educa", r"mentoria",
                 r"ebook", r"treinamento", r"podcast", r"livro"],
    "validacao": [r"clientes? (pagantes|interessados)", r"ja vend", r"lista de espera", r"pre.venda", r"piloto",
                  r"entrevist", r"validad", r"pagantes", r"waitlist", r"\bpilot", r"paying", r"\bmrr",
                  r"usuarios ativos", r"ja tenho clientes", r"ja uso", r"uso interno", r"interessad",
                  r"\d+ (clientes|clinicas|empresas|lojas|usuarios|escritorios) (querem|pediram|usam|testaram)", r"carta de intencao", r"loi\b"],
    "competencia": [r"tenho experiencia", r"trabalho com", r"trabalho (na|no|em)", r"sou (desenvolvedor|programador|medico|advogado|contador|professor|engenheiro|designer|trader)",
                    r"domino", r"anos de experiencia", r"especialista", r"minha area", r"sou [a-z]+(ista|logo|loga|eiro|eira|ico|ica|or|ora)\b",
                    r"sou dono", r"tenho uma? (empresa|clinica|loja|escritorio)", r"atuo (como|em|na|no)"],
    "concorrencia": [r"concorrente", r"ja existe", r"como o\b", r"alternativa a", r"igual ao", r"clone",
                     r"tipo (o )?(uber|ifood|airbnb|notion|canva|nubank)", r"melhor que", r"competidor"],
    "ui": [r"app mobile", r"aplicativo", r"dashboard", r"painel", r"\bsite", r"interface", r"\btelas?\b",
           r"frontend", r"android", r"\bios\b", r"\bpwa", r"landing page", r"portal"],
    "tempo_real": [r"tempo real", r"real.time", r"streaming", r"baixa latencia", r"websocket", r"ao vivo", r"alta frequencia"],
    "escala_humana": [r"consultoria", r"servico personalizado", r"atendimento humano", r"agencia", r"freelanc",
                      r"presencial", r"sob medida", r"feito a mao", r"artesanal", r"one.on.one"],
    "custo_zero": [r"gratuit", r"open source", r"codigo aberto", r"gratis", r"sem custo", r"client.side",
                   r"offline", r"local", r"navegador", r"colab"],
    "reuso": [r"reutiliz", r"biblioteca", r"componente", r"framework", r"modular", r"template",
              r"boilerplate", r"\bsdk", r"motor", r"engine", r"skill"],
    "recorrencia": [r"assinatura", r"recorrente", r"mensal", r"\bsaas", r"subscription", r"plano (mensal|anual)"],
    "global": [r"global", r"mundial", r"internacional", r"todos os paises", r"worldwide", r"qualquer idioma",
               r"multi.?idioma", r"exterior", r"\beua\b", r"europa"],
    "nicho": [r"nicho", r"especific", r"apenas para", r"somente para", r"exclusivo para", r"so para"],
    "backtest": [r"backtest", r"sharpe", r"drawdown", r"paper trading", r"walk.forward", r"fora da amostra",
                 r"out.of.sample", r"simulac"],
    "terceiros": [r"clientes investidores", r"dinheiro de terceiros", r"recursos de terceiros", r"\bfundo\b",
                  r"gestao de carteira", r"recomendac", r"sinais (pagos|para clientes)", r"copy ?trad"],
    "efeito_dados": [r"aprende com", r"melhora com o uso", r"quanto mais (usuarios|dados)", r"feedback loop",
                     r"historico proprio", r"base proprietaria", r"proprietari"],
}

# Verbos/artefatos funcionais — contagem DISTINTA vira estimativa de tamanho funcional
# (pontos de função grosseiros a partir do texto — Albrecht, 1979).
FUNCIONALIDADES = [
    r"gera", r"cria", r"calcul", r"envi", r"notific", r"cadastr", r"busc", r"analis", r"integr",
    r"export", r"import", r"agend", r"monitor", r"classific", r"prev[eêi]", r"recomend", r"compar",
    r"pag", r"autentic", r"login", r"relatori", r"dashboard", r"painel", r"chat", r"traduz", r"resum",
    r"extrai", r"valid", r"simul", r"otimiz", r"precific", r"alert", r"sincroniz", r"publica", r"vend",
    r"compr", r"rastre", r"emit", r"lembr", r"transcrev", r"reconhec", r"filtr", r"orden", r"ranque",
]

# Segmentos/usos — usados na entropia de Shannon de diversidade de usos (KB-SHANNON).
SEGMENTOS: dict[str, list[str]] = {
    "saude": [r"saude", r"clinica", r"medic", r"paciente", r"hospital", r"odonto", r"psicolog"],
    "juridico": [r"juridic", r"advog", r"processo judicial", r"contrato", r"tribunal", r"\bpje"],
    "contabil_fiscal": [r"contab", r"fiscal", r"tribut", r"nota fiscal", r"imposto", r"\bnfe"],
    "varejo_ecommerce": [r"varejo", r"loja", r"e.?commerce", r"mercado livre", r"shopee", r"produto", r"estoque"],
    "educacao": [r"educa", r"escola", r"aluno", r"curso", r"professor", r"estud"],
    "financas": [r"financ", r"investiment", r"trading", r"cripto", r"credito", r"banco", r"\bacoes\b"],
    "industria": [r"industria", r"fabrica", r"manufatura", r"producao", r"\boee\b", r"manutencao"],
    "servicos_locais": [r"restaurante", r"oficina", r"salao", r"academia", r"pet", r"delivery", r"barbearia"],
    "marketing_conteudo": [r"marketing", r"instagram", r"tiktok", r"youtube", r"conteudo", r"anuncio", r"seo"],
    "rh_pessoas": [r"\brh\b", r"recrut", r"curriculo", r"funcionari", r"folha de pagamento", r"talento"],
    "logistica": [r"logistic", r"frete", r"entrega", r"transport", r"rota", r"frota"],
    "agro": [r"\bagro", r"fazenda", r"lavoura", r"safra", r"rebanho", r"agricult"],
    "imobiliario": [r"imovel", r"imobiliari", r"aluguel", r"condominio", r"corretor"],
    "dev_ferramentas": [r"desenvolvedor", r"programador", r"github", r"codigo", r"\bapi", r"devops", r"\bcli\b"],
    "governo_publico": [r"governo", r"prefeitura", r"licitac", r"publico", r"municip"],
    "grafica": [r"grafica", r"impressao", r"encadern", r"adesivo", r"sticker", r"canteadeira"],
}


@dataclass(frozen=True)
class ClasseReferencia:
    """Perfil 'outside view' de uma classe de projetos parecidos.

    `prior` é a probabilidade a priori de a ideia RETORNAR MAIS DO QUE CUSTA (tokens +
    horas) no horizonte declarado — NÃO é probabilidade de virar unicórnio. São priors
    heurísticos DECLARADOS e calibráveis (ADR-002): a literatura dá ordens de grandeza
    (sucesso é evento raro — VCBench: índice de mercado com 1,9% de precisão para
    sucesso de fundador; CB Insights: 35–42% morrem por falta de mercado), não um
    número por classe. O relatório sempre exibe o prior usado.
    """
    nome: str
    rotulo: str
    prior: float
    funcionalidades_base: int     # tamanho funcional mínimo típico da classe
    receita_mensal_cons: float    # cenário conservador (R$/mês) se a ideia funcionar
    receita_mensal_otim: float    # cenário otimista (R$/mês)
    durabilidade: float           # 0..1 — quanto a classe resiste ao tempo
    escalabilidade: float         # 0..1 — custo marginal e alcance típicos
    comoditizacao_ia: float       # 0..1 — risco de um LLM genérico engolir a proposta
    regulacao: float              # 0..1 — exposição regulatória típica
    experimento: str              # experimento mínimo (≤ 5 dias, custo ~0) que MATA a ideia se der negativo
    palavras: tuple[str, ...] = field(default_factory=tuple)


CLASSES: tuple[ClasseReferencia, ...] = (
    ClasseReferencia("automacao_interna", "Automação/RPA de processo interno", 0.35, 4, 1500, 8000, 0.60, 0.45, 0.45, 0.15,
                     "Cronometre o processo manual em 3 execuções reais e calcule horas/mês × valor-hora; se a economia anual < 10× o custo P90 de tokens, mate a ideia.",
                     ("automatiz", "rpa", "planilha", "preencher", "processo", "workflow", "rotina", "relatorio")),
    ClasseReferencia("saas_b2b", "SaaS B2B / ferramenta para empresas", 0.22, 8, 2000, 25000, 0.70, 0.75, 0.40, 0.25,
                     "Landing page + 15 mensagens diretas para o público-alvo pedindo uma call ou pré-venda; menos de 3 respostas qualificadas em 5 dias = sem dor suficiente.",
                     ("empresa", "pme", "b2b", "gestao", "saas", "clinica", "escritorio", "erp", "crm")),
    ClasseReferencia("ferramenta_dev", "Ferramenta para desenvolvedores / open source", 0.18, 6, 500, 10000, 0.55, 0.80, 0.65, 0.05,
                     "Publique um README + demo em GIF e poste em 3 comunidades (Reddit, HN, Discord); < 50 estrelas/inscrições em 5 dias = sem tração orgânica.",
                     ("github", "desenvolvedor", "cli", "biblioteca", "sdk", "devops", "codigo", "skill", "plugin")),
    ClasseReferencia("marketplace", "Marketplace / plataforma de dois lados", 0.08, 12, 1000, 40000, 0.70, 0.90, 0.25, 0.20,
                     "Faça o matching MANUALMENTE (WhatsApp + planilha) para 10 transações; se não fechar 3 em 5 dias, o lado da oferta ou da demanda não existe.",
                     ("marketplace", "conecta", "compradores", "vendedores", "intermedia", "profissionais")),
    ClasseReferencia("app_consumo", "App de consumo (B2C)", 0.07, 10, 500, 30000, 0.40, 0.85, 0.50, 0.15,
                     "Anúncio de R$ 50 levando a uma landing com botão 'quero'; CTR × conversão abaixo de 2% = sem desejo.",
                     ("app", "consumidor", "pessoas", "jovens", "usuarios", "rede social", "jogo")),
    ClasseReferencia("fintech_trading", "Fintech / trading / arbitragem financeira", 0.10, 7, 0, 20000, 0.35, 0.70, 0.40, 0.75,
                     "Backtest + 30 dias de paper trading com custos reais (corretagem, slippage, impostos); Sharpe < 1 ou drawdown > orçamento = mate a estratégia antes de codificar produto.",
                     ("trading", "arbitragem", "cripto", "acoes", "forex", "investimento", "robo", "mt5", "ea")),
    ClasseReferencia("conteudo_educacao", "Conteúdo / educação / infoproduto", 0.30, 3, 800, 15000, 0.55, 0.65, 0.70, 0.05,
                     "Publique 3 peças gratuitas do conteúdo e meça salvamentos/compartilhamentos; ofereça pré-venda — zero compras em 5 dias = proposta fraca.",
                     ("curso", "aula", "conteudo", "educacao", "mentoria", "ebook", "newsletter")),
    ClasseReferencia("ecommerce", "E-commerce / produto físico / revenda", 0.20, 5, 1500, 20000, 0.45, 0.50, 0.20, 0.20,
                     "Anuncie 1 SKU em marketplace (Mercado Livre/Shopee) com estoque sob demanda; margem líquida após taxas < 15% = arbitragem inexistente.",
                     ("loja", "vender", "produto", "estoque", "mercado livre", "shopee", "revenda", "dropshipping")),
    ClasseReferencia("saude_regulado", "Saúde / jurídico / setor regulado", 0.12, 9, 3000, 30000, 0.80, 0.55, 0.35, 0.85,
                     "Mapeie a exigência regulatória (ANVISA/CFM/OAB/LGPD) e entreviste 5 profissionais licenciados; se a exigência inviabiliza o MVP sem certificação, pare.",
                     ("saude", "medico", "paciente", "juridico", "advogado", "clinica", "hospital")),
    ClasseReferencia("ia_wrapper", "Aplicação sobre LLM (camada fina de IA)", 0.12, 5, 1000, 15000, 0.25, 0.85, 0.90, 0.20,
                     "Faça o resultado prometido com um prompt num chat comum diante de 5 usuários-alvo; se o chat genérico já resolve, não há produto.",
                     ("ia", "gpt", "llm", "chatbot", "agente", "claude", "prompt", "generativa")),
    ClasseReferencia("hardware_iot", "Hardware / IoT / dispositivo", 0.08, 8, 1000, 25000, 0.65, 0.35, 0.10, 0.35,
                     "Protótipo de bancada com módulos prontos (ESP32/Raspberry) + vídeo de demonstração para 10 compradores potenciais; sem 2 cartas de intenção, pare.",
                     ("hardware", "sensor", "iot", "dispositivo", "arduino", "raspberry", "esp32", "drone")),
    ClasseReferencia("generico", "Ideia sem setor identificável", 0.15, 6, 1000, 15000, 0.50, 0.60, 0.50, 0.20,
                     "Escreva em 1 parágrafo QUEM tem a dor, QUANTO ela custa e COMO resolve hoje; se não conseguir, a ideia ainda é abstrata demais para testar.",
                     ()),
)
CLASSES_POR_NOME = {c.nome: c for c in CLASSES}

# Perguntas essenciais — a completude da descrição mede quantas o texto responde.
PERGUNTAS_ESSENCIAIS: dict[str, tuple[str, ...]] = {
    "quem tem a dor (cliente)": ("b2b", "b2c"),
    "qual é a dor": ("dor",),
    "com que frequência dói": ("frequencia",),
    "como se ganha dinheiro": ("pagamento", "recorrencia", "arbitragem"),
    "o que já foi validado": ("validacao",),
    "por que você (vantagem do autor)": ("competencia",),
    "quem já resolve isso (concorrência)": ("concorrencia",),
    "o que precisa ser construído": ("digital", "automacao", "ui", "hardware", "conteudo"),
}


def normalizar(texto: str) -> str:
    """Minúsculas, sem acento (NFD → remove marcas), espaços colapsados."""
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", t).strip()


_COMPILADOS = {s: [re.compile(r"(?<![a-z0-9])" + p) for p in pats] for s, pats in SINAIS.items()}
_FUNC = [re.compile(r"(?<![a-z0-9])" + p) for p in FUNCIONALIDADES]
_SEG = {s: [re.compile(r"(?<![a-z0-9])" + p) for p in pats] for s, pats in SEGMENTOS.items()}
_URL_GH = re.compile(r"https?://github\.com/[\w.-]+/[\w.-]+", re.I)


_PALAVRA = re.compile(r"[a-z0-9$#+.-]*[a-z0-9$]")


def _palavra(norm: str, inicio: int) -> str:
    """Palavra inteira a partir de `inicio`, sem pontuação colada (BUG-002)."""
    m = _PALAVRA.match(norm, inicio)
    return m.group(0) if m else norm[inicio:inicio + 12]


def _trecho(norm: str, m: re.Match) -> str:
    """Trecho casado, estendido até o fim da última palavra: “sou dentista”, não “sou” (BUG-010)."""
    fim = m.end()
    while fim < len(norm) and (norm[fim].isalnum() or norm[fim] in "$"):
        fim += 1
    return norm[m.start():fim].strip(" ,.;:")


@dataclass
class Sinais:
    """Resultado da extração — tudo que o resto do analisador sabe sobre a ideia."""
    texto: str
    contagens: dict[str, int]
    evidencias: dict[str, list[str]]
    n_funcionalidades: int
    funcionalidades: list[str]
    segmentos: dict[str, int]
    classe: ClasseReferencia
    afinidade_classes: dict[str, float]
    completude: float                       # 0..1 — fração das perguntas essenciais respondidas
    lacunas: list[str]                      # perguntas essenciais NÃO respondidas
    repos: list[str]
    n_palavras: int

    def tem(self, sinal: str) -> bool:
        return self.contagens.get(sinal, 0) > 0

    def forca(self, sinal: str, saturacao: int = 3) -> float:
        """Intensidade 0..1 do sinal com saturação (3 menções ≈ certeza)."""
        return min(self.contagens.get(sinal, 0), saturacao) / saturacao


def _classificar(norm: str, contagens: dict[str, int]) -> tuple[ClasseReferencia, dict[str, float]]:
    """Afinidade de cada classe = palavras-chave da classe + sinais que a caracterizam."""
    reforco = {
        "automacao_interna": contagens.get("automacao", 0) * 2,
        "saas_b2b": contagens.get("b2b", 0) + contagens.get("recorrencia", 0),
        "ferramenta_dev": 0,
        "marketplace": contagens.get("rede", 0) * 2,
        "app_consumo": contagens.get("b2c", 0),
        "fintech_trading": contagens.get("arbitragem", 0) * 2,
        "conteudo_educacao": contagens.get("conteudo", 0),
        "ecommerce": 0,
        "saude_regulado": contagens.get("regulado", 0),
        "ia_wrapper": contagens.get("ia", 0),
        "hardware_iot": contagens.get("hardware", 0) * 2,
    }
    afin: dict[str, float] = {}
    for c in CLASSES:
        if c.nome == "generico":
            continue
        kw = sum(1 for p in c.palavras if re.search(r"(?<![a-z0-9])" + re.escape(p), norm))
        afin[c.nome] = kw + reforco.get(c.nome, 0)
    # IA citada como MEIO (há outro domínio forte) não faz da ideia um "wrapper".
    outros = max((v for k, v in afin.items() if k != "ia_wrapper"), default=0)
    if afin.get("ia_wrapper", 0) and outros >= afin["ia_wrapper"]:
        afin["ia_wrapper"] *= 0.5
    total = sum(afin.values())
    if total == 0:
        return CLASSES_POR_NOME["generico"], {"generico": 1.0}
    melhor = max(afin, key=lambda k: (afin[k], -list(CLASSES_POR_NOME).index(k)))
    return CLASSES_POR_NOME[melhor], {k: v / total for k, v in sorted(afin.items(), key=lambda kv: -kv[1]) if v}


def extrair(texto: str) -> Sinais:
    """Transforma o texto livre da ideia em sinais, classe de referência e lacunas."""
    norm = normalizar(texto)
    contagens, evid = {}, {}
    for s, regs in _COMPILADOS.items():
        achados = []
        for r in regs:
            for m in r.finditer(norm):
                achados.append(_trecho(norm, m))
        contagens[s] = len(achados)
        if achados:
            evid[s] = sorted(set(achados))[:6]
    # Uma funcionalidade por RADICAL, não por flexão: "lembrete" e "lembretes" contam 1 (BUG-005).
    funcs = sorted({_palavra(norm, m.start()) for r in _FUNC if (m := r.search(norm))})
    segs = {s: sum(len(r.findall(norm)) for r in regs) for s, regs in _SEG.items()}
    segs = {s: n for s, n in segs.items() if n}
    classe, afin = _classificar(norm, contagens)
    lacunas = [p for p, sinais in PERGUNTAS_ESSENCIAIS.items() if not any(contagens.get(x, 0) for x in sinais)]
    completude = 1 - len(lacunas) / len(PERGUNTAS_ESSENCIAIS)
    return Sinais(texto=texto.strip(), contagens=contagens, evidencias=evid,
                  n_funcionalidades=len(funcs), funcionalidades=funcs, segmentos=segs,
                  classe=classe, afinidade_classes=afin, completude=completude,
                  lacunas=lacunas, repos=_URL_GH.findall(texto), n_palavras=len(norm.split()))


if __name__ == "__main__":
    import sys
    s = extrair(" ".join(sys.argv[1:]) or "App para clínicas agendarem consultas pelo WhatsApp com cobrança mensal")
    print(f"🧭 classe de referência: {s.classe.rotulo} (prior {s.classe.prior:.0%})")
    print(f"📝 completude da descrição: {s.completude:.0%} · lacunas: {', '.join(s.lacunas) or 'nenhuma'}")
    print(f"⚙️  funcionalidades ({s.n_funcionalidades}): {', '.join(s.funcionalidades)}")
    for k, v in s.evidencias.items():
        print(f"   • {k:<16} {s.contagens[k]}× → {', '.join(v)}")
