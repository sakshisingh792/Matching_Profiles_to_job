
from fpdf import FPDF

def generate_pdf_report(
    candidate_name,
    report_text
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )

    pdf.multi_cell(
        0,
        10,
        txt=f"""
Candidate Report

Candidate:
{candidate_name}

--------------------------------

{report_text}
"""
    )

    filename = (
        f"reports/{candidate_name}.pdf"
    )

    pdf.output(filename)

    return filename

