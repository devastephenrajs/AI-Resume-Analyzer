import os
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from services.extraction import extract_text
from services.scoring import (
    extract_skills, calculate_ats_score, generate_improvements,
    match_jd, calculate_keyword_density
)
from services.formatting import analyze_formatting
from services.ai_summary import generate_ai_summary
from services.database import save_analysis

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")


class JDMatchRequest(BaseModel):
    resume_text: str
    jd_text: str


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Accepted formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract Text (multi-format)
    resume_text = extract_text(file_path)

    # Skill Extraction (categorized)
    skills = extract_skills(resume_text)

    # ATS Score
    ats_score = calculate_ats_score(resume_text, skills)

    # Formatting Analysis
    formatting = analyze_formatting(resume_text)

    # Keyword Density
    keyword_density = calculate_keyword_density(resume_text, skills)

    # AI Summary (with fallback)
    summary_result = await generate_ai_summary(resume_text, skills)

    # Improvements
    improvements = generate_improvements(resume_text, skills)

    result = {
        "filename": file.filename,
        "extracted_text": resume_text,
        "skills": skills,
        "ats_score": ats_score,
        "formatting": formatting,
        "keyword_density": keyword_density,
        "summary": summary_result["summary"],
        "ai_generated": summary_result["ai_generated"],
        "improvements": improvements
    }

    # Save to MongoDB
    try:
        analysis_id = await save_analysis(result.copy())
        result["id"] = analysis_id
    except Exception as e:
        print(f"MongoDB save failed (non-blocking): {e}")
        result["id"] = None

    return result


@router.post("/match-jd")
async def match_job_description(request: JDMatchRequest):
    result = match_jd(request.resume_text, request.jd_text)
    return result
