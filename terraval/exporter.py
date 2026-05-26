"""Export laudo to .md / .docx / .pdf."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


# ── helpers ───────────────────────────────────────────────────────────────────

def _slug_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _output_dir() -> Path:
    d = Path.home() / "Documents" / "TerraVal"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Markdown ──────────────────────────────────────────────────────────────────

def export_md(text: str, stem: str | None = None) -> Path:
    path = _output_dir() / f"{stem or _slug_timestamp()}.md"
    path.write_text(text, encoding="utf-8")
    return path


# ── DOCX ──────────────────────────────────────────────────────────────────────

def _add_inline(paragraph, line: str) -> None:
    """Parse **bold**, *italic*, `code` inline and add runs to paragraph."""
    token = re.compile(r"(\*\*[^*\n]+\*\*|\*[^*\n]+\*|`[^`\n]+`)")
    for part in token.split(line):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and part.endswith("*"):
            paragraph.add_run(part[1:-1]).italic = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Courier New"
        else:
            paragraph.add_run(part)


def export_docx(text: str, stem: str | None = None) -> Path:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()

    # ── page margins ─────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin   = Inches(1.2)
        section.right_margin  = Inches(1.2)

    # ── cover header ─────────────────────────────────────────────────────────
    header_p = doc.add_paragraph()
    header_p.alignment = 1  # CENTER
    run = header_p.add_run("🌾  TerraVal — Avaliação de Imóveis Rurais")
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x2E, 0x7D, 0x32)  # dark green

    sub = doc.add_paragraph()
    sub.alignment = 1
    sub.add_run(
        f"NBR 14653  ·  Atlas INCRA 2025  ·  BACEN 4.676/2018\n"
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    ).font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_paragraph()  # spacer

    # ── parse markdown ────────────────────────────────────────────────────────
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        # headings
        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=1)

        # horizontal rule
        elif re.match(r"^[-*_]{3,}$", line.strip()):
            p = doc.add_paragraph()
            pPr = p._p.get_or_add_pPr()
            pBdr = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            bottom.set(qn("w:val"), "single")
            bottom.set(qn("w:sz"), "6")
            bottom.set(qn("w:space"), "1")
            bottom.set(qn("w:color"), "AAAAAA")
            pBdr.append(bottom)
            pPr.append(pBdr)

        # fenced code block
        elif line.startswith("```"):
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            p = doc.add_paragraph()
            run = p.add_run("\n".join(code_lines))
            run.font.name = "Courier New"
            run.font.size = Pt(9)

        # table
        elif line.startswith("|"):
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].startswith("|"):
                raw = lines[i]
                if not re.match(r"^\|[\s\-:|]+\|", raw):  # skip separator
                    cells = [c.strip() for c in raw.strip("|").split("|")]
                    rows.append(cells)
                i += 1
            if rows:
                ncols = max(len(r) for r in rows)
                tbl = doc.add_table(rows=len(rows), cols=ncols)
                tbl.style = "Table Grid"
                for r_idx, row in enumerate(rows):
                    for c_idx in range(ncols):
                        cell_text = row[c_idx] if c_idx < len(row) else ""
                        cell = tbl.cell(r_idx, c_idx)
                        cell.text = ""
                        p = cell.paragraphs[0]
                        _add_inline(p, cell_text)
                        if r_idx == 0:
                            for run in p.runs:
                                run.bold = True
                doc.add_paragraph()
            continue  # i already advanced inside loop

        # blockquote — disclaimer
        elif line.startswith("> "):
            p = doc.add_paragraph(style="Quote")
            _add_inline(p, line[2:])

        # bullet list
        elif re.match(r"^[-*+] ", line):
            p = doc.add_paragraph(style="List Bullet")
            _add_inline(p, line[2:])

        # numbered list
        elif re.match(r"^\d+\. ", line):
            p = doc.add_paragraph(style="List Number")
            _add_inline(p, re.sub(r"^\d+\. ", "", line))

        # blank line
        elif not line.strip():
            pass

        # regular paragraph
        else:
            p = doc.add_paragraph()
            _add_inline(p, line)

        i += 1

    # ── footer ────────────────────────────────────────────────────────────────
    doc.add_paragraph()
    footer_p = doc.add_paragraph()
    footer_p.alignment = 1
    footer_run = footer_p.add_run(
        "Este documento foi gerado com suporte de IA (TerraVal). "
        "Laudos com validade legal exigem vistoria e assinatura de profissional habilitado no CREA com ART."
    )
    footer_run.italic = True
    footer_run.font.size = Pt(8)
    footer_run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    path = _output_dir() / f"{stem or _slug_timestamp()}.docx"
    doc.save(str(path))
    return path


# ── PDF ───────────────────────────────────────────────────────────────────────

def export_pdf(text: str, stem: str | None = None) -> Path:
    import markdown as md_lib
    from fpdf import FPDF

    # Convert markdown → HTML
    html = md_lib.markdown(
        text,
        extensions=["tables", "fenced_code", "nl2br"],
    )

    # Wrap in minimal styled HTML
    full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body  {{ font-family: Arial, sans-serif; font-size: 11pt; color: #222; }}
  h1    {{ color: #2E7D32; font-size: 16pt; border-bottom: 2px solid #2E7D32; }}
  h2    {{ color: #1B5E20; font-size: 13pt; }}
  h3    {{ color: #333; font-size: 11pt; }}
  table {{ border-collapse: collapse; width: 100%; margin: 8px 0; }}
  th, td {{ border: 1px solid #ccc; padding: 4px 8px; font-size: 10pt; }}
  th    {{ background: #E8F5E9; font-weight: bold; }}
  code, pre {{ font-family: Courier New; font-size: 9pt; background: #f5f5f5; padding: 2px 4px; }}
  blockquote {{ border-left: 3px solid #aaa; padding-left: 10px; color: #555; font-style: italic; }}
</style>
</head><body>
<p style="color:#2E7D32;font-size:14pt;font-weight:bold;text-align:center">
  🌾 TerraVal — Avaliação de Imóveis Rurais</p>
<p style="color:#555;font-size:9pt;text-align:center">
  NBR 14653 · Atlas INCRA 2025 · BACEN 4.676/2018<br>
  Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
<hr>
{html}
<hr>
<p style="color:#aaa;font-size:8pt;text-align:center">
  Gerado com suporte de IA (TerraVal). Laudos com validade legal exigem vistoria e
  assinatura de profissional habilitado no CREA com ART.</p>
</body></html>"""

    path = _output_dir() / f"{stem or _slug_timestamp()}.pdf"

    # Use fpdf2's HTML renderer
    class _PDF(FPDF):
        pass

    pdf = _PDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    # fpdf2 write_html
    from fpdf.html import HTMLMixin  # noqa: F401 — confirm fpdf2 ≥ 2.7

    pdf2 = FPDF()
    pdf2.add_page()
    pdf2.set_margins(20, 20, 20)
    pdf2.set_auto_page_break(auto=True, margin=20)
    pdf2.set_font("Helvetica", size=11)
    pdf2.write_html(full_html)
    pdf2.output(str(path))

    return path


# ── public API ────────────────────────────────────────────────────────────────

def save_report(
    text: str,
    formats: list[str],   # e.g. ["docx", "pdf", "md"]
    stem: str | None = None,
) -> dict[str, Path]:
    """Save report in requested formats. Returns {format: path}."""
    ts = stem or _slug_timestamp()
    results: dict[str, Path] = {}

    if "md" in formats:
        results["md"] = export_md(text, ts)
    if "docx" in formats:
        results["docx"] = export_docx(text, ts)
    if "pdf" in formats:
        results["pdf"] = export_pdf(text, ts)

    return results
