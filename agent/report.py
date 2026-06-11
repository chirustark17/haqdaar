"""Builds a downloadable report (PDF for English; plain text otherwise) from a
Haqdaar result. Presentation-only; imports nothing from the locked pipeline."""
from io import BytesIO


def _latin1_safe(text: str) -> str:
    # fpdf2 core fonts are Latin-1 only; replace common unicode punctuation,
    # then drop anything still unencodable so PDF generation never crashes.
    repl = {
        "\u2014": "-", "\u2013": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u2022": "-",
        "\u00b7": "-", "\u20b9": "INR ",
    }
    for a, b in repl.items():
        text = text.replace(a, b)
    return text.encode("latin-1", "ignore").decode("latin-1")


def build_report_text(result: dict) -> str:
    """A clean plain-text version of the full result."""
    lines = ["HAQDAAR - YOUR RIGHTS SUMMARY", "=" * 32, ""]
    if result.get("explanation"):
        lines += ["EXPLANATION", result["explanation"], ""]
    rights = result.get("rights", [])
    if rights:
        lines.append("RIGHTS & BENEFITS YOU MAY QUALIFY FOR")
        for r in rights:
            lines.append(f"- {r.get('name', 'Benefit')}")
            if r.get("why_eligible"):
                lines.append(f"  Why: {r['why_eligible']}")
            if r.get("citation"):
                lines.append(f"  Source: {r['citation']}")
        lines.append("")
    steps = result.get("action_plan", [])
    if steps:
        lines.append("ACTION PLAN")
        for i, s in enumerate(steps, 1):
            lines.append(f"{i}. {s}")
        lines.append("")
    if result.get("letter"):
        lines += ["DRAFTED LETTER", result["letter"], ""]
    if result.get("sources"):
        lines.append("Grounded in sources: " + ", ".join(result["sources"]))
    if result.get("disclaimer"):
        lines += ["", result["disclaimer"]]
    return "\n".join(lines)


def build_report_pdf(result: dict) -> bytes:
    """Render an English report to PDF bytes (fpdf2 core fonts, Latin-1)."""
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    def heading(txt):
        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(0, 8, _latin1_safe(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)

    def body(txt):
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, _latin1_safe(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 10, "Haqdaar - Your Rights Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    if result.get("explanation"):
        heading("Explanation")
        body(result["explanation"])
        pdf.ln(2)
    rights = result.get("rights", [])
    if rights:
        heading("Rights & benefits you may qualify for")
        for r in rights:
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, _latin1_safe(r.get("name", "Benefit")), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if r.get("why_eligible"):
                body(r["why_eligible"])
            if r.get("citation"):
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(0, 5, _latin1_safe("Source: " + str(r["citation"])), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        pdf.ln(1)
    steps = result.get("action_plan", [])
    if steps:
        heading("Action plan")
        for i, s in enumerate(steps, 1):
            body(f"{i}. {s}")
        pdf.ln(2)
    if result.get("letter"):
        heading("Drafted letter")
        body(result["letter"])
        pdf.ln(2)
    if result.get("sources"):
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(0, 5, _latin1_safe("Grounded in sources: " + ", ".join(result["sources"])), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if result.get("disclaimer"):
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 8)
        pdf.multi_cell(0, 4, _latin1_safe(result["disclaimer"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    out = pdf.output()
    return bytes(out) if not isinstance(out, (bytes, bytearray)) else bytes(out)
