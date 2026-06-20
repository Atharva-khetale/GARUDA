"""
MODULE 10: REPORT GENERATION

Generates a PDF report from a full-analysis result dict (as produced by
the /pipeline/full-analysis endpoint or the Celery task) using
ReportLab. Includes an executive summary, sequence analysis, mutation
analysis, expression analysis, protein impact, optimization
suggestions, ML predictions, and recommendations.
"""
from __future__ import annotations

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def _section_table(rows: list[tuple[str, str]]) -> Table:
    table = Table(rows, colWidths=[6 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def generate_pdf_report(analysis: dict, output_path: str) -> str:
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("GarudaTitle", parent=styles["Title"], textColor=colors.HexColor("#0f172a"))
    h2 = ParagraphStyle("GarudaH2", parent=styles["Heading2"], textColor=colors.HexColor("#0f172a"),
                         spaceBefore=12, spaceAfter=6)
    body = styles["BodyText"]

    story = []
    story.append(Paragraph("GARUDA Construct Analysis Report", title_style))
    story.append(Spacer(1, 12))

    # --- Executive Summary ---
    readiness = analysis.get("readiness_score", {})
    story.append(Paragraph("Executive Summary", h2))
    story.append(_section_table([
        ("Construct Readiness Score", f"{readiness.get('construct_score', 'N/A')} / 100"),
        ("Expression Score", f"{readiness.get('expression_score', 'N/A')} / 100 "
                              f"({readiness.get('expression_category', 'N/A')})"),
        ("Mutation Severity", str(readiness.get("mutation_severity", "N/A"))),
        ("Optimization Needed", str(readiness.get("optimization_needed", "N/A"))),
        ("Recommendation", str(readiness.get("recommendation", "N/A"))),
    ]))
    story.append(Spacer(1, 12))

    # --- Sequence Analysis ---
    seq = analysis.get("sequence_analysis", {})
    story.append(Paragraph("Sequence Analysis", h2))
    story.append(_section_table([
        ("Sequence Type", str(seq.get("seq_type", "N/A"))),
        ("Length (nt)", str(seq.get("length", "N/A"))),
        ("GC Content", f"{seq.get('gc_content', 'N/A')}%"),
        ("ORFs Detected", str(len(seq.get("orfs", [])))),
        ("Translated Protein Length", str(len(seq.get("protein_sequence", "")))),
    ]))
    story.append(Spacer(1, 12))

    # --- Mutation Analysis ---
    mutation = analysis.get("mutation_report")
    story.append(Paragraph("Mutation Analysis", h2))
    if mutation:
        summary = mutation.get("summary", {})
        story.append(_section_table([
            ("Total Mutations", str(summary.get("total_mutations", 0))),
            ("High Severity", str(summary.get("high_severity", 0))),
            ("Medium Severity", str(summary.get("medium_severity", 0))),
            ("Low Severity", str(summary.get("low_severity", 0))),
            ("Overall Severity", str(summary.get("overall_severity", "N/A"))),
        ]))
    else:
        story.append(Paragraph("No mutated sequence was provided for comparison.", body))
    story.append(Spacer(1, 12))

    # --- Protein Impact ---
    protein = analysis.get("protein_impact")
    story.append(Paragraph("Protein Impact Analysis", h2))
    if protein:
        story.append(_section_table([
            ("Functional Impact Score", f"{protein.get('functional_impact_score', 'N/A')} / 100"),
            ("Amino Acid Changes", str(protein.get("amino_acid_changes", 0))),
            ("Protein Length Change", str(protein.get("protein_length_change", 0))),
            ("Verdict", str(protein.get("verdict", "N/A"))),
        ]))
    else:
        story.append(Paragraph("Not applicable (no mutated sequence provided).", body))
    story.append(PageBreak())

    # --- Expression Analysis ---
    expr = analysis.get("expression_feasibility", {})
    story.append(Paragraph("Expression Feasibility Analysis", h2))
    story.append(_section_table([
        ("Expression Score", f"{expr.get('expression_score', 'N/A')} / 100"),
        ("Category", str(expr.get("category", "N/A"))),
        ("CAI", str(expr.get("metrics", {}).get("cai", "N/A"))),
        ("Rare Codons", f"{expr.get('metrics', {}).get('rare_codon_count', 'N/A')} / "
                        f"{expr.get('metrics', {}).get('total_codons', 'N/A')}"),
    ]))
    story.append(Spacer(1, 6))
    for line in expr.get("reasoning", []):
        story.append(Paragraph(f"• {line}", body))
    story.append(Spacer(1, 12))

    # --- Codon Optimization ---
    opt = analysis.get("codon_optimization", {})
    story.append(Paragraph("Codon Optimization Suggestions", h2))
    if opt:
        story.append(_section_table([
            ("Target Organism", str(opt.get("organism", "N/A"))),
            ("Codons Changed", f"{opt.get('codons_changed', 0)} / {opt.get('total_codons', 0)}"),
            ("CAI Before -> After",
             f"{opt.get('before', {}).get('cai', 'N/A')} -> {opt.get('after', {}).get('cai', 'N/A')}"),
            ("GC% Before -> After",
             f"{opt.get('before', {}).get('gc_content', 'N/A')} -> {opt.get('after', {}).get('gc_content', 'N/A')}"),
            ("Rare Codons Before -> After",
             f"{opt.get('before', {}).get('rare_codon_count', 'N/A')} -> "
             f"{opt.get('after', {}).get('rare_codon_count', 'N/A')}"),
        ]))
    story.append(Spacer(1, 12))

    # --- Restriction Sites ---
    restriction = analysis.get("restriction_analysis", {})
    story.append(Paragraph("Restriction Enzyme Analysis", h2))
    enz_rows = [("Enzyme", "Cut Sites")]
    for enzyme, data in restriction.get("enzymes", {}).items():
        enz_rows.append((enzyme, str(data.get("num_cuts", 0))))
    if len(enz_rows) > 1:
        story.append(_section_table(enz_rows))
    else:
        story.append(Paragraph("No restriction sites detected for the analyzed enzyme panel.", body))
    story.append(Spacer(1, 12))

    # --- ML Predictions ---
    ml = analysis.get("ml_prediction", {})
    story.append(Paragraph("Machine Learning Predictions", h2))
    if ml:
        story.append(_section_table([
            ("Model", str(ml.get("model", "N/A"))),
            ("Prediction", str(ml.get("prediction", "N/A"))),
            ("Confidence", str(ml.get("confidence", "N/A"))),
            ("Viability Probability", str(ml.get("viability_probability", "N/A"))),
        ]))
    story.append(Spacer(1, 12))

    # --- Recommendation ---
    story.append(Paragraph("Recommendation", h2))
    story.append(Paragraph(str(readiness.get("recommendation", "N/A")), body))

    doc.build(story)
    return output_path
