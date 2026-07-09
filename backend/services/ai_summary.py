"""
AI-powered resume summary using Google Gemini.
Falls back to rule-based summary if the API key is not set or the call fails.
"""
import os
from services.scoring import generate_summary as rule_based_summary

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

SUMMARY_PROMPT = """You are an expert HR consultant and resume reviewer. 
Analyze the following resume text and extracted skills, then produce a concise, 
professional summary (3-5 sentences) of the candidate. Include:

1. Their likely role/seniority level
2. Core technical strengths
3. Notable experience patterns
4. An overall assessment of their profile

Resume Text:
{resume_text}

Extracted Skills:
{skills}

Respond with ONLY the summary paragraph, no headers or bullet points."""


async def generate_ai_summary(resume_text: str, skills: list) -> dict:
    """
    Generate an AI-powered summary using Google Gemini.
    
    Returns:
        dict with 'summary' (str) and 'ai_generated' (bool)
    """
    # Extract skill names if skills are dicts with 'name' key
    skill_names = []
    for s in skills:
        if isinstance(s, dict):
            skill_names.append(s.get("name", str(s)))
        else:
            skill_names.append(str(s))

    if not GENAI_AVAILABLE or not GEMINI_API_KEY:
        return {
            "summary": rule_based_summary(skill_names),
            "ai_generated": False
        }

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = SUMMARY_PROMPT.format(
            resume_text=resume_text[:3000],  # Limit to avoid token overflow
            skills=", ".join(skill_names)
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        summary_text = response.text.strip()

        if summary_text:
            return {
                "summary": summary_text,
                "ai_generated": True
            }
    except Exception as e:
        print(f"Gemini API error (falling back to rule-based): {e}")

    return {
        "summary": rule_based_summary(skill_names),
        "ai_generated": False
    }
