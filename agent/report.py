"""Builds a downloadable report (PDF for English; plain text otherwise) from a
Haqdaar result. Presentation-only; imports nothing from the locked pipeline."""
from io import BytesIO


def _latin1_safe(text: str) -> str:
    # fpdf2 core fonts are Latin-1 only; replace common unicode punctuation,
    # then drop anything still unencodable so PDF generation never crashes.
    repl = {
        "—": "-", "–": "-", "‘": "'", "’": "'",
        "“": '"', "”": '"', "…": "...", "•": "-",
        "·": "-", "₹": "INR ",
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


# Set False to fall back to the plain (pre-restyle) PDF builder.
USE_STYLED_PDF = True


def build_report_pdf(result: dict) -> bytes:
    """Render an English report to PDF bytes. Dispatches to the styled or plain builder."""
    if USE_STYLED_PDF:
        return _build_report_pdf_styled(result)
    return _build_report_pdf_plain(result)


def _build_report_pdf_styled(result: dict) -> bytes:
    """Microsoft-standard styled report (fpdf2 core fonts, Latin-1)."""
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    BLUE = (0, 120, 212)
    NAVY = (36, 58, 94)
    INK = (50, 49, 48)
    MUTED = (96, 94, 92)
    HAIR = (225, 223, 221)
    PANEL = (247, 246, 245)

    FOOTER_LINE = _latin1_safe(
        "Haqdaar · Microsoft Agents League 2026 - Creative Apps track · "
        "Grounded by Foundry IQ on Azure AI Search · Built with GitHub Copilot & VS Code"
    )
    DISCLAIMER = _latin1_safe(
        "Synthetic demo knowledge base - informational only, not legal or financial advice."
    )

    class Report(FPDF):
        def footer(self):
            self.set_y(-17)
            self.set_draw_color(*HAIR)
            self.set_line_width(0.3)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(1.5)
            self.set_text_color(*MUTED)
            self.set_font("Helvetica", size=7.5)
            self.multi_cell(0, 3.6, FOOTER_LINE, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            self.set_font("Helvetica", "I", 7)
            self.multi_cell(0, 3.6, DISCLAIMER, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf = Report()
    pdf.set_auto_page_break(auto=True, margin=24)
    pdf.set_margins(18, 16, 18)
    pdf.add_page()

    band_h = 34
    pdf.set_fill_color(*BLUE)
    pdf.rect(0, 0, pdf.w, band_h, "F")
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 4, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(pdf.l_margin, 9)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, _latin1_safe("Microsoft Agents League · Creative Apps"),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(pdf.l_margin, 14)
    pdf.set_font("Helvetica", "B", 26)
    pdf.cell(0, 12, _latin1_safe("Haqdaar"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(pdf.l_margin, 27)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(225, 238, 251)
    pdf.cell(0, 5, _latin1_safe("Know your rights. Get what you're due."),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(band_h + 8)
    pdf.set_text_color(*INK)
    pdf.set_font("Helvetica", "", 10.5)
    pdf.multi_cell(
        0, 5.6,
        _latin1_safe(
            "A grounded civic-rights co-pilot: describe your situation or paste an official "
            "notice, and Haqdaar explains it, finds the benefits you may qualify for, plans "
            "your next steps, and drafts a ready-to-send letter — every claim cited."
        ),
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )

    def section(title):
        pdf.ln(4)
        pdf.set_text_color(*BLUE)
        pdf.set_font("Helvetica", "B", 13)
        pdf.multi_cell(0, 7, _latin1_safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        y = pdf.get_y() + 0.5
        pdf.set_draw_color(*HAIR)
        pdf.set_line_width(0.3)
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.ln(3)
        pdf.set_text_color(*INK)

    def body(txt, size=10.5):
        pdf.set_text_color(*INK)
        pdf.set_font("Helvetica", "", size)
        pdf.multi_cell(0, 5.6, _latin1_safe(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if result.get("explanation"):
        section("Explanation")
        body(result["explanation"])

    rights = result.get("rights", [])
    if rights:
        section("Rights & benefits you may qualify for")
        for r in rights:
            x0 = pdf.l_margin
            y0 = pdf.get_y()
            pdf.set_x(x0 + 6)
            pdf.set_text_color(*INK)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 5.8, _latin1_safe(r.get("name", "Benefit")),
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if r.get("why_eligible"):
                pdf.set_x(x0 + 6)
                pdf.set_font("Helvetica", "", 10.5)
                pdf.multi_cell(0, 5.4, _latin1_safe(r["why_eligible"]),
                               new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if r.get("citation"):
                pdf.set_x(x0 + 6)
                pdf.set_text_color(*MUTED)
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(0, 4.8, _latin1_safe("Source: " + str(r["citation"])),
                               new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            y1 = pdf.get_y()
            pdf.set_fill_color(*BLUE)
            pdf.rect(x0, y0, 1.6, max(y1 - y0 - 1, 2), "F")
            pdf.ln(3)

    steps = result.get("action_plan", [])
    if steps:
        section("Action plan")
        pdf.set_font("Helvetica", "", 10.5)
        pdf.set_text_color(*INK)
        for i, s in enumerate(steps, 1):
            x0 = pdf.l_margin
            pdf.set_x(x0)
            pdf.cell(7, 5.6, f"{i}.", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.set_x(x0 + 7)
            pdf.multi_cell(0, 5.6, _latin1_safe(str(s)), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(0.6)

    if result.get("letter"):
        section("Drafted letter")
        pdf.set_fill_color(*PANEL)
        pdf.set_text_color(*INK)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5.4, _latin1_safe(result["letter"]),
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    if result.get("sources"):
        section("Grounded in sources")
        pdf.set_text_color(*MUTED)
        pdf.set_font("Helvetica", "", 10)
        for src in result["sources"]:
            pdf.multi_cell(0, 5.2, _latin1_safe("- " + str(src)),
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    out = pdf.output()
    return bytes(out) if not isinstance(out, (bytes, bytearray)) else bytes(out)


def _build_report_pdf_plain(result: dict) -> bytes:
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
