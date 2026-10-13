# AnalisadorPreditivoMinimoViaveldeProjetos
# Autor: ProfBru - Bruno Penedo © 2026 - TODOS OS DIREITOS RESERVADOS
# E-mail: profbruanbima@gmail.com
"""Exporta o relatório do GPS em três formatos: Markdown, HTML e PDF em formato OCR.

PDF em formato OCR (e não PDF de texto puro):
  1. o HTML é diagramado em páginas A4 pelo motor do MuPDF (`fitz.Story`);
  2. cada página é RASTERIZADA (imagem) sobre um fundo branco que já traz a logo do
     projeto, grande e centralizada, a 50% de transparência — a marca d'água fica ATRÁS
     do conteúdo, em todas as páginas;
  3. a página final recebe a imagem + uma CAMADA DE TEXTO INVISÍVEL (render mode 3) com
     cada palavra na sua posição original — a mesma estrutura que um OCR produz: o PDF
     é pesquisável e o texto é selecionável, mas a página é imagem, não texto puro.

Sem rede, sem serviço externo: PyMuPDF + Pillow + markdown, tudo local (zero-cost).
"""
from __future__ import annotations

import base64
import html
import io
import re
from pathlib import Path

import fitz  # PyMuPDF
import markdown as md
from PIL import Image

from config import ENCODING, RAIZ

LOGO = RAIZ / "docs" / "logo_capa.png"
OPACIDADE_MARCA = 0.50
DPI_PAGINA = 170
JPEG_QUALIDADE = 85      # PNG custava ~6 s/página e 1,3 MB/página; JPEG 85 mantém o texto nítido a 170 dpi
A4 = fitz.paper_rect("a4")
MARGEM = 42

CSS = """
:root { --fundo:#fcfcfb; --tinta:#0b0b0b; --tinta2:#52514e; --mudo:#898781; --grade:#e1e0d9; --azul:#2a78d6; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --fundo:#1a1a19; --tinta:#ffffff; --tinta2:#c3c2b7; --mudo:#898781; --grade:#2c2c2a; --azul:#3987e5; } }
:root[data-theme="dark"] { --fundo:#1a1a19; --tinta:#ffffff; --tinta2:#c3c2b7; --mudo:#898781; --grade:#2c2c2a; --azul:#3987e5; }
* { box-sizing: border-box; }
body { margin:0; background:var(--fundo); color:var(--tinta); font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,"DejaVu Sans",sans-serif; }
.marca { position:fixed; inset:0; background:url(data:image/png;base64,{LOGO64}) center/60% no-repeat; opacity:.5; pointer-events:none; z-index:0; }
main { position:relative; z-index:1; max-width:1040px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:1.7rem; margin:.4em 0; } h2 { font-size:1.25rem; margin-top:1.8em; border-bottom:1px solid var(--grade); padding-bottom:.2em; }
table { border-collapse:collapse; width:100%; margin:.8em 0; font-size:.92rem; display:block; overflow-x:auto; }
th, td { border:1px solid var(--grade); padding:6px 8px; text-align:left; vertical-align:top; }
th { background:color-mix(in srgb, var(--azul) 10%, transparent); }
blockquote { margin:1em 0; padding:.6em 1em; border-left:4px solid var(--azul); color:var(--tinta2); background:color-mix(in srgb, var(--azul) 6%, transparent); }
code, pre { font-family:"DejaVu Sans Mono",ui-monospace,monospace; font-size:.86rem; }
pre { white-space:pre-wrap; padding:12px; border:1px solid var(--grade); border-radius:6px; }
img.tela { width:100%; height:auto; border:1px solid var(--grade); border-radius:6px; margin:.6em 0; background:#fff; }
footer { color:var(--mudo); font-size:.8rem; margin-top:3em; text-align:center; }
"""

# Emojis: o MuPDF não tem fonte de emoji — no PDF viram marcadores coloridos com rótulo.
_EMOJI_PDF = {"🟢": '<span style="color:#0ca30c">●</span>', "🟡": '<span style="color:#d49100">●</span>',
              "🔴": '<span style="color:#d03b3b">●</span>', "⚖️": "", "✅": "✔", "❌": "✖", "⚠️": "!"}
_RX_EMOJI = re.compile("[\U0001F000-\U0001FFFF☀-➿️]")


def _b64(p: Path) -> str:
    return base64.b64encode(Path(p).read_bytes()).decode("ascii")


_RX_DETAILS = re.compile(r"<details>\s*<summary>(?:<b>)?(.*?)(?:</b>)?</summary>", re.S)


def _md_para_html(texto_md: str) -> str:
    texto_md = re.sub(r"^> \[!(WARNING|NOTE|IMPORTANT|TIP)\]\s*$", r"> **\1**", texto_md, flags=re.M)
    # <details> esconde Markdown do conversor (a tabela saía como texto corrido — BUG-017):
    # no relatório exportado o conteúdo vai aberto, com o resumo como subtítulo.
    texto_md = _RX_DETAILS.sub(lambda m: f"\n**{m.group(1).strip()}**\n", texto_md).replace("</details>", "")
    return md.markdown(texto_md, extensions=["tables", "fenced_code", "sane_lists", "md_in_html"])


def html_relatorio(texto_md: str, titulo: str, telas: list[Path] | None = None) -> str:
    """HTML autocontido: CSS com tema claro/escuro, marca d'água a 50% e telas embutidas."""
    corpo = _md_para_html(texto_md)
    if telas:
        corpo += "<h2>Telas</h2>" + "".join(
            f'<img class="tela" alt="{html.escape(t.stem)}" src="data:image/png;base64,{_b64(t)}"/>' for t in telas)
    css = CSS.replace("{LOGO64}", _b64(LOGO))
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{html.escape(titulo)}</title><style>{css}</style></head>"
            f'<body><div class="marca"></div><main>{corpo}'
            f"<footer>Analisador Preditivo Mínimo Viável de Projetos · ProfBru © 2026 — TODOS OS DIREITOS RESERVADOS · profbruanbima@gmail.com</footer>"
            f"</main></body></html>")


def _html_para_pdf_vetorial(texto_md: str, telas: list[Path]) -> bytes:
    """Diagramação A4 do conteúdo (sem marca d'água) com fitz.Story."""
    for k, v in _EMOJI_PDF.items():
        texto_md = texto_md.replace(k, v)
    texto_md = _RX_EMOJI.sub("", texto_md)
    corpo = _md_para_html(texto_md)
    arquivo = fitz.Archive()
    imgs = ""
    for t in telas or []:
        arquivo.add(t.read_bytes(), t.name)
        imgs += f'<p><img src="{t.name}" width="100%"/></p>'
    css = ("body{font-family:sans-serif;font-size:9.5pt;color:#0b0b0b;} h1{font-size:16pt;} h2{font-size:12.5pt;margin-top:10pt;}"
           "table{border-collapse:collapse;} td,th{border:0.5pt solid #c3c2b7;padding:2pt 3pt;font-size:8pt;}"
           "blockquote{color:#52514e;margin-left:8pt;} pre,code{font-family:monospace;font-size:7.5pt;}")
    rodape = '<p style="font-size:7pt;color:#898781;text-align:center;">Analisador Preditivo Mínimo Viável de Projetos · ProfBru © 2026 — TODOS OS DIREITOS RESERVADOS</p>'
    story = fitz.Story(html=corpo + (("<h2>Telas</h2>" + imgs) if imgs else "") + rodape, user_css=css, archive=arquivo)
    buf = io.BytesIO()
    escritor = fitz.DocumentWriter(buf)
    area = A4 + (MARGEM, MARGEM, -MARGEM, -MARGEM)
    mais = True
    while mais:
        disp = escritor.begin_page(A4)
        mais, _ = story.place(area)
        story.draw(disp)
        escritor.end_page()
    escritor.close()
    return buf.getvalue()


def _fundo_com_marca(largura: int, altura: int) -> Image.Image:
    """Página branca com a logo grande e centralizada a 50% de opacidade."""
    fundo = Image.new("RGBA", (largura, altura), (255, 255, 255, 255))
    logo = Image.open(LOGO).convert("RGBA")
    alvo = int(largura * 0.78)
    logo = logo.resize((alvo, int(logo.height * alvo / logo.width)), Image.LANCZOS)
    alfa = logo.getchannel("A").point(lambda a: int(a * OPACIDADE_MARCA))
    logo.putalpha(alfa)
    fundo.alpha_composite(logo, ((largura - logo.width) // 2, (altura - logo.height) // 2))
    return fundo


def pdf_ocr(texto_md: str, destino: Path, telas: list[Path] | None = None, titulo: str = "") -> Path:
    """PDF em formato OCR: imagem da página (com marca d'água ao fundo) + texto invisível pesquisável."""
    vetorial = fitz.open("pdf", _html_para_pdf_vetorial(texto_md, telas or []))
    saida = fitz.open()
    fonte = Path(__import__("matplotlib").get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf"
    fonte_ocr = fitz.Font(fontfile=str(fonte))
    escala = DPI_PAGINA / 72
    fundo_cache = None
    for pg in vetorial:
        pix = pg.get_pixmap(matrix=fitz.Matrix(escala, escala), alpha=True)
        conteudo = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
        if fundo_cache is None or fundo_cache.size != conteudo.size:
            fundo_cache = _fundo_com_marca(*conteudo.size)
        pagina_img = fundo_cache.copy()
        pagina_img.alpha_composite(conteudo)               # conteúdo POR CIMA da marca d'água
        jpg = io.BytesIO()
        pagina_img.convert("RGB").save(jpg, format="JPEG", quality=JPEG_QUALIDADE, optimize=True)
        nova = saida.new_page(width=pg.rect.width, height=pg.rect.height)
        nova.insert_image(nova.rect, stream=jpg.getvalue())
        # Camada OCR: cada palavra, invisível (render_mode=3), na posição exata da imagem.
        # UM TextWriter por página: insert_text por palavra recalculava o balanço do
        # conteúdo a cada chamada — custo quadrático, 5,8 s em 2 mil palavras (BUG-019).
        tw = fitz.TextWriter(nova.rect)
        for x0, y0, x1, y1, palavra, *_ in pg.get_text("words"):
            altura = max(y1 - y0, 1.0)
            tam_h = altura * 0.82
            # Largura invisível = largura visível: a seleção cobre a palavra certa e o
            # extrator enxerga o espaço entre palavras (sem isto: "GPSpreditivo" — BUG-020).
            larg1 = fonte_ocr.text_length(palavra, fontsize=1.0) or 1.0
            tam = min(max((x1 - x0) / larg1, 0.5 * tam_h), 1.3 * tam_h)
            tw.append((x0, y1 - altura * 0.22), palavra + " ", font=fonte_ocr, fontsize=tam)
        tw.write_text(nova, render_mode=3)
    saida.set_metadata({"title": titulo or "GPS preditivo", "author": "ProfBru - Bruno Penedo",
                        "subject": "Analisador Preditivo Mínimo Viável de Projetos",
                        "creator": "AnalisadorPreditivoMinimoViaveldeProjetos", "producer": "PyMuPDF"})
    destino.parent.mkdir(parents=True, exist_ok=True)
    saida.save(destino, garbage=4, deflate=True)
    return destino


def exportar(texto_md: str, base: Path, telas: list[Path] | None = None, titulo: str = "GPS preditivo") -> dict[str, Path]:
    """Grava <base>.md, <base>.html e <base>.pdf. Devolve os caminhos."""
    base = Path(base)
    base.parent.mkdir(parents=True, exist_ok=True)
    p_md, p_html, p_pdf = base.with_suffix(".md"), base.with_suffix(".html"), base.with_suffix(".pdf")
    from stamp import carimbo                       # fonte única do carimbo (D18)
    selo = carimbo("md")                           # comentário HTML: invisível na leitura
    p_md.write_text(selo + "\n\n" + texto_md, encoding=ENCODING)
    p_html.write_text(html_relatorio(texto_md, titulo, telas).replace("<!doctype html>", "<!doctype html>\n" + selo, 1),
                      encoding=ENCODING)
    pdf_ocr(texto_md, p_pdf, telas, titulo)
    return {"md": p_md, "html": p_html, "pdf": p_pdf}
