"""
PDF export router — generates and returns a styled PDF report.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from services.pdf_export import generate_report_pdf

router = APIRouter()


class ExportRequest(BaseModel):
    filename: str = "resume"
    ats_score: int = 0
    summary: str = ""
    ai_generated: bool = False
    skills: list = []
    improvements: list = []
    formatting: dict = {}
    keyword_density: dict = {}
    match: dict | None = None
    extracted_text: str = ""


@router.post("/export-pdf")
async def export_pdf(request: ExportRequest):
    """Generate a PDF report from the analysis data."""
    try:
        analysis_data = request.model_dump()
        pdf_bytes = generate_report_pdf(analysis_data)

        safe_filename = request.filename.replace(".pdf", "").replace(".docx", "").replace(".txt", "")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_filename}_report.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
