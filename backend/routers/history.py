"""
Resume history router — CRUD operations for past analyses.
"""
from fastapi import APIRouter, HTTPException
from services.database import get_all_analyses, get_analysis, delete_analysis

router = APIRouter()


@router.get("/history")
async def list_history():
    """Return all past analyses (summary view)."""
    analyses = await get_all_analyses()
    return {"analyses": analyses}


@router.get("/history/{analysis_id}")
async def get_history_item(analysis_id: str):
    """Return a specific analysis by ID."""
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.delete("/history/{analysis_id}")
async def delete_history_item(analysis_id: str):
    """Delete a specific analysis."""
    deleted = await delete_analysis(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"message": "Analysis deleted successfully"}
