"""
PDF report generation service using ReportLab.
Creates a styled, professional analysis report.
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# Color palette
DARK_BG = HexColor("#0f172a")
SURFACE = HexColor("#1e293b")
BLUE = HexColor("#3b82f6")
GREEN = HexColor("#10b981")
RED = HexColor("#ef4444")
AMBER = HexColor("#f59e0b")
WHITE = HexColor("#ffffff")
LIGHT_GRAY = HexColor("#94a3b8")
DARK_TEXT = HexColor("#1e293b")


def _create_styles():
    """Create custom paragraph styles for the report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=DARK_TEXT,
        alignment=TA_CENTER,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontName="Helvetica",
        fontSize=11,
        textColor=LIGHT_GRAY,
        alignment=TA_CENTER,
        spaceAfter=20
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=BLUE,
        spaceBefore=16,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="BodyText2",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK_TEXT,
        leading=14,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="BulletItem",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK_TEXT,
        leading=14,
        leftIndent=20,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="ScoreLabel",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=DARK_TEXT,
        alignment=TA_CENTER
    ))

    return styles


def _get_score_color(score: int) -> HexColor:
    """Return a color based on score value."""
    if score >= 75:
        return GREEN
    elif score >= 50:
        return AMBER
    else:
        return RED


def generate_report_pdf(analysis_data: dict) -> bytes:
    """
    Generate a styled PDF report from analysis data.
    
    Args:
        analysis_data: dict containing all analysis results
        
    Returns:
        bytes of the generated PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25 * mm,
        leftMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm
    )

    styles = _create_styles()
    elements = []

    # --- Title ---
    elements.append(Paragraph("AI Resume Analysis Report", styles["ReportTitle"]))
    filename = analysis_data.get("filename", "Unknown")
    elements.append(Paragraph(f"File: {filename}", styles["ReportSubtitle"]))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=BLUE,
        spaceAfter=16, spaceBefore=4
    ))

    # --- Scores Overview ---
    elements.append(Paragraph("Score Overview", styles["SectionHeader"]))

    ats_score = analysis_data.get("ats_score", 0)
    formatting_score = analysis_data.get("formatting", {}).get("formatting_score", 0)
    match_score = analysis_data.get("match", {}).get("match_score", None) if analysis_data.get("match") else None

    score_data = [
        ["Metric", "Score", "Rating"],
        [
            "ATS Score",
            f"{ats_score}/100",
            "Excellent" if ats_score >= 75 else "Good" if ats_score >= 50 else "Needs Work"
        ],
        [
            "Formatting",
            f"{formatting_score}/100",
            "Excellent" if formatting_score >= 75 else "Good" if formatting_score >= 50 else "Needs Work"
        ],
    ]

    if match_score is not None:
        score_data.append([
            "JD Match",
            f"{match_score}/100",
            "Strong" if match_score >= 70 else "Moderate" if match_score >= 40 else "Weak"
        ])

    score_table = Table(score_data, colWidths=[200, 100, 150])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, HexColor("#f1f5f9")]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 12))

    # --- AI Summary ---
    summary = analysis_data.get("summary", "")
    if summary:
        elements.append(Paragraph("Candidate Summary", styles["SectionHeader"]))
        ai_tag = " (AI-Generated)" if analysis_data.get("ai_generated", False) else ""
        elements.append(Paragraph(f"{summary}{ai_tag}", styles["BodyText2"]))
        elements.append(Spacer(1, 8))

    # --- Skills ---
    skills = analysis_data.get("skills", [])
    if skills:
        elements.append(Paragraph(f"Detected Skills ({len(skills)})", styles["SectionHeader"]))

        # Group by category if available
        categorized = {}
        for skill in skills:
            if isinstance(skill, dict):
                cat = skill.get("category", "Other")
                name = skill.get("name", str(skill))
            else:
                cat = "General"
                name = str(skill)
            categorized.setdefault(cat, []).append(name)

        for category, skill_list in categorized.items():
            skills_text = ", ".join(s.title() for s in skill_list)
            elements.append(Paragraph(
                f"<b>{category}:</b> {skills_text}",
                styles["BodyText2"]
            ))
        elements.append(Spacer(1, 8))

    # --- Formatting Analysis ---
    formatting = analysis_data.get("formatting", {})
    if formatting:
        elements.append(Paragraph("Formatting Analysis", styles["SectionHeader"]))

        fmt_items = [
            f"Word Count: {formatting.get('word_count', 'N/A')}",
            f"Estimated Pages: {formatting.get('page_estimate', 'N/A')}",
            f"Sections Found: {', '.join(formatting.get('sections_found', []))}",
        ]
        for item in fmt_items:
            elements.append(Paragraph(f"• {item}", styles["BulletItem"]))

        missing = formatting.get("sections_missing", [])
        if missing:
            elements.append(Paragraph(
                f"• Missing Sections: {', '.join(missing)}",
                styles["BulletItem"]
            ))
        elements.append(Spacer(1, 8))

    # --- Improvements ---
    improvements = analysis_data.get("improvements", [])
    if improvements:
        elements.append(Paragraph("Recommended Improvements", styles["SectionHeader"]))
        for imp in improvements:
            elements.append(Paragraph(f"• {imp}", styles["BulletItem"]))
        elements.append(Spacer(1, 8))

    # --- JD Match Details ---
    match_data = analysis_data.get("match")
    if match_data:
        elements.append(Paragraph("Job Description Match", styles["SectionHeader"]))
        elements.append(Paragraph(
            f"Match Score: {match_data.get('match_score', 0)}%",
            styles["BodyText2"]
        ))

        missing_skills = match_data.get("missing_skills", [])
        if missing_skills:
            elements.append(Paragraph(
                f"Missing Skills: {', '.join(s.title() for s in missing_skills)}",
                styles["BodyText2"]
            ))
        else:
            elements.append(Paragraph(
                "You have all the required skills!",
                styles["BodyText2"]
            ))

    # --- Footer ---
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(
        width="100%", thickness=0.5, color=LIGHT_GRAY,
        spaceAfter=8, spaceBefore=8
    ))
    elements.append(Paragraph(
        "Generated by AI Resume Analyzer",
        ParagraphStyle(
            name="Footer",
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=LIGHT_GRAY,
            alignment=TA_CENTER
        )
    ))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
