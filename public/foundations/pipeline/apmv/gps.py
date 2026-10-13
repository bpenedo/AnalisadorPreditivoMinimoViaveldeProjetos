# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""GPS preditivo — orquestra extração, tokens, finanças, previsão e decisão.

Saída para o usuário, antes de gastar UM token de código:
  🟢 INVISTA (projeto ou reaproveitamento)   🟢 INVISTA NO MVP
  🟡 TESTE ANTES (experimento mínimo)        🔴 NÃO INVISTA AGORA

Além do semáforo, o GPS entrega o que um LLM sabe fazer bem e o modelo
quantitativo não (referencias.txt da KB): perguntas incômodas, teste de
reversibilidade, experimento mínimo que mataria a ideia e mapa honesto de
dependências — e, no modo comparação, qual ideia eliminar primeiro.
"""
from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field

from . import decisao as dec
from . import financeiro, indicadores, preditivo, repositorio, tokens
from .extrator import extrair

PERGUNTAS = {
    "DEM-01": "Quanto essa dor custa, em reais por mês, para UM cliente real que você consegue nomear?",
    "DEM-02": "Com que frequência o problema acontece — e o que o cliente faz hoje quando acontece?",
    "DEM-03": "Quem já pagou (ou disse que pagaria) e quanto? Se ninguém, por que pagariam a você?",
    "DEM-04": "Qual é a evidência, fora da sua cabeça, de que alguém quer isso?",
    "DEM-05": "Descreva o cliente típico em uma frase: cargo, porte, contexto. Se não consegue, quem é?",
    "MER-01": "Quantos clientes existem de verdade — e quantos você alcança sem anúncio?",
    "MER-02": "Se o primeiro segmento não comprar, qual é o segundo? Existe?",
    "MER-05": "Por que o cliente trocaria a solução atual (incluindo planilha e WhatsApp) pela sua?",
    "TEC-01": "Qual é a menor versão que entrega valor — com no máximo 5 funcionalidades?",
    "TEC-02": "O que acontece se a API de terceiros mudar o preço ou cortar o acesso amanhã?",
    "TEC-05": "Por que um chat genérico de IA não vai resolver isso de graça em 24 meses?",
    "DUR-01": "Esse problema ainda existirá daqui a 10 anos? O que o faria desaparecer?",
    "DUR-02": "A demanda existia antes da tendência atual — ou é o hype que está falando?",
    "DUR-03": "Se a plataforma da qual você depende mudar a regra, o negócio sobrevive?",
    "ESC-01": "Quanto custa atender o milésimo cliente? Se a resposta envolve uma pessoa, não escala.",
    "CUM-01": "Se falhar em 3 meses, que código ou componente sobrevive para o próximo projeto?",
    "CUM-02": "Que dado proprietário fica mais valioso a cada uso?",
    "ROB-01": "Qual licença, registro ou norma pode proibir o MVP — e você já leu a norma?",
    "ROB-02": "Quantas coisas precisam dar certo FORA do seu controle para isso funcionar?",
    "ALI-01": "Por que VOCÊ? O que você sabe ou acessa que outro desenvolvedor não?",
    "ALI-02": "Qual experimento de 5 dias mataria essa ideia se desse errado?",
    "ARB-01": "Se a arbitragem é real, por que ainda não foi explorada até sumir?",
    "ARB-03": "Qual é o Sharpe fora da amostra, depois de custos e impostos?",
    "ARB-04": "O capital é só seu? Se envolve terceiros, você tem registro na CVM?",
}

MENSAGENS = {
    "VERDE": ("🟢", "INVISTA", "A rota de investimento vence nas nove escolas com margem: pode gastar tokens com método."),
    "VERDE-MVP": ("🟢", "INVISTA NO MVP", "Gaste só o MVP enxuto e decida no meio — é o melhor equilíbrio entre aprender e arriscar."),
    "AMARELO": ("🟡", "TESTE ANTES", "Ainda não gaste tokens de código: rode o experimento mínimo e volte com a evidência."),
    "VERMELHO": ("🔴", "NÃO INVISTA AGORA", "Nenhuma rota de investimento bate o CDI com risco aceitável no que se sabe hoje."),
}


@dataclass
class ResultadoAnalise:
    texto: str
    sinais: object
    repo: object | None
    tamanho: object
    tokens: object
    medidas: dict
    dimensoes: dict
    previsao: object
    financeiro: object
    decisao: object
    semaforo: str
    rota_recomendada: str
    perguntas_incomodas: list[str]
    reversibilidade: str
    experimento_minimo: str
    dependencias: dict
    lacunas: list[str]
    tempo_s: float
    avisos: list[str] = field(default_factory=list)


def _semaforo(r_dec, fin, sinais, prev) -> tuple[str, list[str]]:
    avisos = []
    lider = r_dec.lider
    if lider == "A0":
        cor = "VERMELHO"
    elif lider == "A1":
        cor = "AMARELO"
    elif lider == "A2":
        cor = "VERDE-MVP"
    else:
        cor = "VERDE" if fin.margem_seguranca >= 1.5 and r_dec.veredito_robustez != "FRÁGIL" else "VERDE-MVP"
    if sinais.completude < 0.30 and cor.startswith("VERDE"):
        cor = "AMARELO"
        avisos.append("Descrição responde a menos de 30% das perguntas essenciais: o GPS não autoriza investir sem evidência.")
    if r_dec.veredito_robustez == "FRÁGIL":
        avisos.append("A rota vencedora é FRÁGIL (< 60% dos universos de pesos): a decisão depende da sua calibração — releia as premissas.")
    ev_lider = next((r.valor_esperado for r in fin.rotas if r.codigo == lider), 0.0)
    if lider != "A0" and ev_lider < 0:
        avisos.append("Mesmo a rota vencedora tem valor esperado negativo nas premissas atuais: ela só se justifica "
                      "se o teste puder MUDAR as premissas (receita, preço, probabilidade). Senão, fique no CDI.")
    if fin.margem_seguranca < 1 and cor.startswith("VERDE"):
        avisos.append("p_viável abaixo da probabilidade de break-even: só invista no que for barato o bastante para errar.")
    return cor, avisos


def _dependencias(s) -> dict:
    so_voce = ["escrever e testar o código", "definir o escopo mínimo"]
    mundo = []
    if s.tem("validacao") is False:
        mundo.append("existir demanda pagante (ainda não demonstrada)")
    if s.tem("integracao"):
        mundo.append("APIs de terceiros: " + ", ".join(s.evidencias.get("integracao", [])))
    if s.tem("rede"):
        mundo.append("adoção simultânea dos dois lados da rede")
    if s.tem("regulado") or s.classe.regulacao >= 0.5:
        mundo.append("regulação/licenciamento do setor")
    if s.tem("plataforma_unica"):
        mundo.append("política de uma plataforma única")
    if s.tem("arbitragem"):
        mundo.append("persistência da ineficiência de mercado (alfa)")
    if s.tem("competencia"):
        so_voce.append("aplicar a sua experiência no domínio")
    if s.tem("custo_zero"):
        so_voce.append("operar sem custo recorrente (client-side)")
    return {"so_de_voce": so_voce, "do_mundo": mundo or ["nenhuma dependência externa detectada no texto"]}


def analisar_ideia(texto: str, repo: str | None = None, premissas: financeiro.Premissas | None = None,
                   n_iter: int = 2000, semente: int = 42, destino_clone=None) -> ResultadoAnalise:
    t0 = time.perf_counter()
    s = extrair(texto)
    info_repo = None
    alvo_repo = repo or (s.repos[0] if s.repos else None)
    avisos = []
    if alvo_repo:
        try:
            info_repo = repositorio.analisar(alvo_repo, destino_clone)
        except Exception as e:  # noqa: BLE001 — repositório ausente não derruba a análise
            avisos.append(f"Repositório não analisado ({e.__class__.__name__}: {e}). Seguindo sem código existente.")
    est = tokens.estimar(s, info_repo, semente=semente)
    med = indicadores.medir_qualitativos(s, est.tamanho, info_repo)
    prev = preditivo.prever(med, s, semente=semente)
    fin = financeiro.analisar(est, prev.p_viavel, s, info_repo, premissas)
    med = indicadores.medir_economicos(med, est, fin)
    dims = indicadores.notas_por_dimensao(med)
    r_dec = dec.decidir_rotas(fin, est, dims, n_iter=n_iter, semente=semente)
    cor, av2 = _semaforo(r_dec, fin, s, prev)
    piores = sorted((m for m in med.items() if m[0] in PERGUNTAS), key=lambda kv: kv[1].nota * (0.5 + kv[1].confianca))[:3]
    cum = med["CUM-03"].nota
    rev = "ALTA" if cum >= 0.65 else ("MÉDIA" if cum >= 0.45 else "BAIXA")
    rev_txt = {"ALTA": "o que se constrói (código, dados, aprendizado do domínio) serve a outros projetos.",
               "MÉDIA": "parte do esforço vira ativo reutilizável; parte se perde se a ideia morrer.",
               "BAIXA": "quase tudo é específico desta ideia — se falhar, sobra pouco."}[rev]
    experimento = (s.classe.experimento if s.completude >= 0.25 or s.classe.nome != "generico"
                   else "Essa ideia ainda está abstrata demais para testar: responda às lacunas abaixo antes.")
    return ResultadoAnalise(texto, s, info_repo, est.tamanho, est, med, dims, prev, fin, r_dec, cor,
                            r_dec.lider, [PERGUNTAS[k] for k, _ in piores], f"{rev} — {rev_txt}", experimento,
                            _dependencias(s), s.lacunas, time.perf_counter() - t0, avisos + av2)


def _analisar_tarefa(args):
    texto, premissas, n_iter, semente = args
    return analisar_ideia(texto, premissas=premissas, n_iter=n_iter, semente=semente)


def comparar_ideias(textos: list[str], premissas=None, n_iter: int = 2000, semente: int = 42,
                    workers: int | None = None) -> tuple[list[ResultadoAnalise], object]:
    """Analisa várias ideias em paralelo (ProcessPoolExecutor — D8) e as compara nas 9 escolas.

    Partição fixa: uma tarefa por ideia, sempre na mesma ordem e com a mesma semente —
    o resultado não depende do número de processos.
    """
    tarefas = [(t, premissas, n_iter, semente) for t in textos]
    if len(textos) <= 1 or workers == 1:
        res = [_analisar_tarefa(t) for t in tarefas]
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            res = list(ex.map(_analisar_tarefa, tarefas))
    return res, dec.decidir_ideias(res, n_iter=n_iter, semente=semente)
