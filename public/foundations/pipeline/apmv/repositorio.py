# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Maturidade de um código pronto ou semi-pronto no GitHub (ou em pasta local).

Uma ideia com código existente não parte do zero — mas código existente também
CUSTA: precisa ser lido (tokens de entrada) e pode ter licença incompatível.
Este módulo mede, SEM EXECUTAR NADA do repositório (é dado não confiável):

  • linhas por linguagem, nº de arquivos-fonte;
  • presença de testes, CI, README, licença, lockfile/manifesto;
  • idade do último commit;
  • nível de prontidão (TRL-software, 1–9) e maturidade 0..1.

A maturidade reduz os tokens de CODIFICAR (o que existe não se reescreve) e a
leitura do código entra nos tokens de ESTRUTURAR/PLANEJAR (10 tokens por linha).
"""
from __future__ import annotations

import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

EXTENSOES = {
    ".py": "Python", ".rs": "Rust", ".fs": "F#", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript", ".go": "Go", ".rb": "Ruby", ".java": "Java",
    ".kt": "Kotlin", ".cs": "C#", ".php": "PHP", ".c": "C", ".cpp": "C++", ".h": "C/C++",
    ".swift": "Swift", ".dart": "Dart", ".svelte": "Svelte", ".vue": "Vue", ".sql": "SQL",
    ".sh": "Bash", ".zig": "Zig", ".mq5": "MQL5", ".mq4": "MQL4", ".r": "R", ".jl": "Julia",
    ".html": "HTML", ".css": "CSS", ".scss": "CSS", ".lua": "Lua", ".ex": "Elixir", ".scala": "Scala",
}
IGNORAR = {".git", "node_modules", "target", "dist", "build", ".venv", "venv", "__pycache__", "vendor", ".next"}
URL_GITHUB = re.compile(r"^https?://github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")


@dataclass
class InfoRepositorio:
    nome: str
    origem: str
    arquivos_fonte: int
    loc_total: int
    loc_por_linguagem: dict[str, int]
    tem_testes: bool
    tem_ci: bool
    tem_readme: bool
    licenca: str
    tem_manifesto: bool
    dias_desde_ultimo_commit: float | None
    trl: str
    maturidade: float
    observacoes: list[str] = field(default_factory=list)

    def como_dict(self) -> dict:
        return asdict(self)


def clonar(url: str, destino: Path) -> Path:
    """Clone raso num diretório NOVO e isolado. Nada do repositório é executado."""
    m = URL_GITHUB.match(url.strip())
    if not m:
        raise ValueError(f"URL do GitHub inválida: {url}")
    alvo = destino / f"{m.group(1)}__{m.group(2)}"
    if not alvo.exists():
        destino.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", "--quiet", f"https://github.com/{m.group(1)}/{m.group(2)}.git", str(alvo)],
                       check=True, timeout=300, capture_output=True)
    return alvo


def _licenca(raiz: Path) -> str:
    for nome in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "LICENCA"):
        f = raiz / nome
        if f.exists():
            t = f.read_text(encoding="utf-8", errors="ignore")[:3000].lower()
            for chave, rot in (("mit license", "MIT"), ("apache license", "Apache-2.0"),
                               ("gnu affero", "AGPL"), ("gnu general public", "GPL"),
                               ("gnu lesser", "LGPL"), ("bsd", "BSD"), ("mozilla public", "MPL-2.0"),
                               ("unlicense", "Unlicense"), ("all rights reserved", "Proprietária")):
                if chave in t:
                    return rot
            return "outra"
    return "ausente"


def _trl(loc: int, testes: bool, ci: bool, readme: bool, recente: bool) -> tuple[str, float]:
    """Nível de prontidão adaptado a software (TRL 1–9) e maturidade 0..1."""
    if loc == 0:
        return "TRL-1 (só ideia/documentação)", 0.0
    if loc < 300:
        nivel, m = "TRL-3 (prova de conceito)", 0.15
    elif loc < 2000:
        nivel, m = "TRL-4 (protótipo funcional)", 0.30
    elif loc < 10000:
        nivel, m = "TRL-5 (protótipo validável)", 0.45
    else:
        nivel, m = "TRL-6 (sistema demonstrável)", 0.55
    m += 0.12 * testes + 0.10 * ci + 0.05 * readme + 0.05 * recente
    if testes and ci and loc >= 2000:
        nivel = "TRL-7 (pronto para piloto)"
    return nivel, min(m, 0.85)      # nunca 1,0: integrar/adaptar sempre custa algo


def analisar(caminho: str | Path, destino_clone: Path | None = None) -> InfoRepositorio:
    origem = str(caminho)
    if origem.startswith("http"):
        raiz = clonar(origem, destino_clone or Path("dados/repos"))
    else:
        raiz = Path(caminho)
    loc_ling: dict[str, int] = {}
    n_fonte = 0
    testes = False
    for f in raiz.rglob("*"):
        if any(p in IGNORAR for p in f.relative_to(raiz).parts) or not f.is_file():
            continue
        rel = f.relative_to(raiz).as_posix().lower()
        if re.search(r"(^|/)(tests?|spec|__tests__)(/|$)|(^|/)test_[^/]+$|_test\.\w+$|\.spec\.\w+$|testes", rel):
            testes = True
        ling = EXTENSOES.get(f.suffix.lower())
        if not ling or f.stat().st_size > 2_000_000:
            continue
        try:
            n = sum(1 for linha in f.read_text(encoding="utf-8", errors="ignore").splitlines() if linha.strip())
        except OSError:
            continue
        n_fonte += 1
        loc_ling[ling] = loc_ling.get(ling, 0) + n
    loc = sum(loc_ling.values())
    ci = (raiz / ".github" / "workflows").exists() or (raiz / ".gitlab-ci.yml").exists()
    readme = any((raiz / r).exists() for r in ("README.md", "README.rst", "README.txt", "README"))
    manifesto = any((raiz / r).exists() for r in ("pyproject.toml", "requirements.txt", "Cargo.toml", "package.json",
                                                   "go.mod", "Gemfile", "pom.xml", "build.gradle", "composer.json"))
    dias = None
    if (raiz / ".git").exists():
        r = subprocess.run(["git", "-C", str(raiz), "log", "-1", "--format=%ct"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            dias = (time.time() - int(r.stdout.strip())) / 86400
    recente = dias is not None and dias < 180
    nivel, mat = _trl(loc, testes, ci, readme, recente)
    lic = _licenca(raiz)
    obs = []
    if lic in ("ausente", "Proprietária"):
        obs.append("Sem licença aberta: reaproveitar exige autorização do autor — inspirar não é copiar.")
    if lic in ("GPL", "AGPL"):
        obs.append(f"Licença {lic} é copyleft: derivar obriga a abrir o código derivado.")
    if dias is not None and dias > 365:
        obs.append(f"Último commit há {dias / 365:.1f} ano(s): dependências provavelmente desatualizadas.")
    if not testes:
        obs.append("Sem testes: o código existente não prova que funciona — conte com retrabalho.")
    return InfoRepositorio(raiz.name, origem, n_fonte, loc, dict(sorted(loc_ling.items(), key=lambda kv: -kv[1])),
                           testes, ci, readme, lic, manifesto, dias, nivel, mat, obs)
