"""
MongoDB persistence layer for resume analyses.
Uses Motor (async MongoDB driver) for non-blocking database operations.
"""
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.resume_analyzer
analyses_collection = database.get_collection("analyses")


def _analysis_helper(analysis: dict) -> dict:
    """Convert MongoDB document to a JSON-serializable dict."""
    return {
        "id": str(analysis["_id"]),
        "filename": analysis.get("filename", ""),
        "ats_score": analysis.get("ats_score", 0),
        "summary": analysis.get("summary", ""),
        "ai_generated": analysis.get("ai_generated", False),
        "skills": analysis.get("skills", []),
        "improvements": analysis.get("improvements", []),
        "formatting": analysis.get("formatting", {}),
        "keyword_density": analysis.get("keyword_density", {}),
        "match": analysis.get("match", None),
        "extracted_text": analysis.get("extracted_text", ""),
        "created_at": analysis.get("created_at", ""),
    }


async def save_analysis(data: dict) -> str:
    """Save an analysis result to MongoDB. Returns the inserted ID."""
    data["created_at"] = datetime.now(timezone.utc).isoformat()
    result = await analyses_collection.insert_one(data)
    return str(result.inserted_id)


async def get_all_analyses() -> list[dict]:
    """Return all analyses, sorted by most recent first (summary view)."""
    analyses = []
    async for analysis in analyses_collection.find().sort("created_at", -1):
        analyses.append({
            "id": str(analysis["_id"]),
            "filename": analysis.get("filename", ""),
            "ats_score": analysis.get("ats_score", 0),
            "summary": analysis.get("summary", "")[:100] + "...",
            "skills_count": len(analysis.get("skills", [])),
            "created_at": analysis.get("created_at", ""),
        })
    return analyses


async def get_analysis(analysis_id: str) -> dict | None:
    """Return a single analysis by its ID."""
    try:
        analysis = await analyses_collection.find_one({"_id": ObjectId(analysis_id)})
        if analysis:
            return _analysis_helper(analysis)
    except Exception:
        return None
    return None


async def delete_analysis(analysis_id: str) -> bool:
    """Delete a single analysis by its ID. Returns True if deleted."""
    try:
        result = await analyses_collection.delete_one({"_id": ObjectId(analysis_id)})
        return result.deleted_count == 1
    except Exception:
        return False
