# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Motor das 9 escolas multicritério (ELECTRE I/II, PROMETHEE II, MAUT, MCDA-C,
AHP-TOPSIS 2n, VIKOR, TODIM, SAPEVO-M) + consenso de Borda + robustez de Dirichlet.

Procedência: vendorizado de `multicriteriadecisionmodels/public/foundations/pipeline`
(MCDM Studio, mesmo autor). Únicas alterações: imports relativos e `config_mcdm.py`.
"""
from .nucleo import CONSENSO, METODOS, preparar
from .robustez import DESCRICAO_VEREDITO, classificar, resumir, simular

__all__ = ["CONSENSO", "METODOS", "preparar", "simular", "resumir", "classificar",
           "DESCRICAO_VEREDITO"]
