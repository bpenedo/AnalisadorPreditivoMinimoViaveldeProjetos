# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Parâmetros do motor multicritério das 9 escolas (vendorizado do MCDM Studio, mesmo autor).

Os nomes são os mesmos do projeto de origem para que `nucleo.py`, `metodos_br.py` e
`robustez.py` sejam cópias fiéis e possam ser ressincronizados com `diff`.
Variáveis de ambiente usam o prefixo `ANALISADORPR_` (ver config.py do projeto).
"""
import os


def _env(nome, padrao):
    return os.environ.get(f"ANALISADORPR_{nome}", padrao)


ELECTRE_C = float(_env("ELECTRE_C", "0.65"))        # concordância mínima
ELECTRE_D = float(_env("ELECTRE_D", "0.35"))        # discordância máxima
PROMETHEE_TIPO = _env("PROMETHEE_TIPO", "linear")
PROMETHEE_Q = float(_env("PROMETHEE_Q", "0.10"))    # quantil do limiar de indiferença
PROMETHEE_P = float(_env("PROMETHEE_P", "0.90"))    # quantil do limiar de preferência
MAUT_AVERSAO = float(_env("MAUT_AVERSAO", "2.0"))   # r > 0 ⇒ aversão a risco
MCDAC_NEUTRO = float(_env("MCDAC_NEUTRO", "0.25"))
MCDAC_BOM = float(_env("MCDAC_BOM", "0.75"))
AHP_CR_LIMITE = float(_env("AHP_CR_LIMITE", "0.10"))
ROBUSTEZ_ITER = int(_env("ROBUSTEZ_ITER", "2000"))
ROBUSTEZ_KAPPA = float(_env("ROBUSTEZ_KAPPA", "200"))
SEED = int(_env("SEED", "42"))
N_WORKERS = int(_env("WORKERS", "0")) or (os.cpu_count() or 4)
LIMIAR_TRABALHO_PARALELO = int(_env("LIMIAR_TRABALHO", "1500000"))
USAR_NUMBA = _env("NUMBA", "1") not in ("0", "false", "False")
