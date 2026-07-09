"""
Resume comparison router — side-by-side analysis of two resumes.
"""
import os
import shutil
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from services.extraction import extract_text
from services.scoring import extract_skills, calculate_ats_score, calculate_keyword_density
from services.formatting import analyze_formatting
from services.ai_summary import generate_ai_summary

router = APIRouter()

UPLOAD_DIR = "uploads"


async def _analyze_single(file: UploadFile) -> dict:
    """Run full analysis on a single uploaded file."""
    file_path = os.path.join(UPLOAD_DIR, f"compare_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text(file_path)
        skills = extract_skills(text)
        ats_score = calculate_ats_score(text, skills)
        formatting = analyze_formatting(text)
        keyword_density = calculate_keyword_density(text, skills)
        summary_result = await generate_ai_summary(text, skills)

        return {
            "filename": file.filename,
            "extracted_text": text,
            "skills": skills,
            "ats_score": ats_score,
            "formatting": formatting,
            "keyword_density": keyword_density,
            "summary": summary_result["summary"],
            "ai_generated": summary_result["ai_generated"],
        }
    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)


@router.post("/compare")
async def compare_resumes(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """Compare two resumes side by side."""
    allowed_extensions = (".pdf", ".docx", ".txt")

    for f in [file1, file2]:
        if not f.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' is not supported. Accepted: PDF, DOCX, TXT."
            )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    analysis1 = await _analyze_single(file1)
    analysis2 = await _analyze_single(file2)

    # Compute comparison metrics
    skills1 = set(s["name"] if isinstance(s, dict) else s for s in analysis1["skills"])
    skills2 = set(s["name"] if isinstance(s, dict) else s for s in analysis2["skills"])

    shared_skills = list(skills1 & skills2)
    unique_to_1 = list(skills1 - skills2)
    unique_to_2 = list(skills2 - skills1)

    return {
        "resume1": analysis1,
        "resume2": analysis2,
        "comparison": {
            "shared_skills": shared_skills,
            "unique_to_resume1": unique_to_1,
            "unique_to_resume2": unique_to_2,
            "ats_difference": analysis1["ats_score"] - analysis2["ats_score"],
            "formatting_difference": (
                analysis1["formatting"]["formatting_score"] -
                analysis2["formatting"]["formatting_score"]
            ),
        }
    }
