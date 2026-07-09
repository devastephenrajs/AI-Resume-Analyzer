"""
Scoring, skill extraction, and analysis services.
"""
import re
import math
from collections import Counter
from services.skills_db import get_all_skills, get_category_for_skill


# English stop words for filtering
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "this", "that", "these",
    "those", "i", "you", "he", "she", "it", "we", "they", "me", "him",
    "her", "us", "them", "my", "your", "his", "its", "our", "their",
    "what", "which", "who", "whom", "where", "when", "why", "how",
    "not", "no", "nor", "if", "then", "else", "so", "as", "from",
    "about", "into", "through", "during", "before", "after", "above",
    "below", "between", "up", "down", "out", "off", "over", "under",
    "again", "further", "once", "here", "there", "all", "each", "every",
    "both", "few", "more", "most", "other", "some", "such", "only",
    "own", "same", "than", "too", "very", "just", "because", "also"
}


def _cosine_similarity(text1: str, text2: str) -> float:
    """Pure-Python cosine similarity using word frequency vectors."""
    words1 = [w for w in re.findall(r'\w+', text1.lower()) if w not in STOP_WORDS and len(w) > 1]
    words2 = [w for w in re.findall(r'\w+', text2.lower()) if w not in STOP_WORDS and len(w) > 1]

    if not words1 or not words2:
        return 0.0

    freq1 = Counter(words1)
    freq2 = Counter(words2)

    # Get all unique words
    all_words = set(freq1.keys()) | set(freq2.keys())

    # Dot product and magnitudes
    dot_product = sum(freq1.get(w, 0) * freq2.get(w, 0) for w in all_words)
    magnitude1 = math.sqrt(sum(v ** 2 for v in freq1.values()))
    magnitude2 = math.sqrt(sum(v ** 2 for v in freq2.values()))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def extract_skills(text: str) -> list[dict]:
    """
    Extract skills from text using the expanded skills database.
    Returns a list of dicts: [{"name": "python", "category": "Programming Languages"}, ...]
    """
    text_lower = text.lower()
    found_skills = []
    seen = set()

    for skill in get_all_skills():
        if skill in text_lower and skill not in seen:
            seen.add(skill)
            category = get_category_for_skill(skill) or "Other"
            found_skills.append({"name": skill, "category": category})

    return found_skills


def calculate_ats_score(text: str, skills: list) -> int:
    """Calculate ATS Score based on predefined heuristic."""
    score = 0
    text_lower = text.lower()

    # Extract skill count (handle both dict and string formats)
    skill_count = len(skills)

    # Skills = 40 points (scales with larger DB: ~2 pts per skill, max 40)
    score += min(skill_count * 2, 40)

    # Education = 20
    edu_keywords = [
        "education", "university", "college", "degree", "bachelor",
        "master", "phd", "b.tech", "b.sc", "b.a.", "m.tech", "m.sc",
        "diploma", "certification"
    ]
    if any(word in text_lower for word in edu_keywords):
        score += 20

    # Experience = 20
    exp_keywords = [
        "experience", "work", "employment", "job", "internship", "role",
        "position", "professional", "career", "responsibility"
    ]
    if any(word in text_lower for word in exp_keywords):
        score += 20

    # Projects = 20
    proj_keywords = [
        "projects", "portfolio", "github", "developed", "built",
        "created", "implemented", "designed", "deployed", "architected"
    ]
    if any(word in text_lower for word in proj_keywords):
        score += 20

    return min(score, 100)


def generate_summary(skills: list) -> str:
    """Generate a rule-based summary of the candidate."""
    # Handle both dict and string skill formats
    skill_names = []
    for s in skills:
        if isinstance(s, dict):
            skill_names.append(s.get("name", str(s)))
        else:
            skill_names.append(str(s))

    if not skill_names:
        return "Candidate profile uploaded. More details needed to generate summary."

    # Format nicely for display
    display_skills = []
    for s in skill_names:
        if s == "node.js": display_skills.append("Node.js")
        elif s == "fastapi": display_skills.append("FastAPI")
        elif s == "mongodb": display_skills.append("MongoDB")
        elif s == "aws": display_skills.append("AWS")
        elif s == "sql": display_skills.append("SQL")
        elif s == "gcp": display_skills.append("GCP")
        elif s == "ci/cd": display_skills.append("CI/CD")
        elif s == "llm": display_skills.append("LLM")
        elif s == "nlp": display_skills.append("NLP")
        else: display_skills.append(s.title())

    if len(display_skills) == 1:
        return f"Candidate has strong experience in {display_skills[0]}."
    elif len(display_skills) == 2:
        return f"Candidate has strong experience in {display_skills[0]} and {display_skills[1]}."
    else:
        last_skill = display_skills[-1]
        joined = ", ".join(display_skills[:-1])
        return f"Candidate has strong experience in {joined}, and {last_skill}."


def match_jd(resume_text: str, jd_text: str) -> dict:
    """Match resume to Job Description, returning score and missing skills."""
    if not resume_text or not jd_text:
        return {"match_score": 0, "missing_skills": []}

    try:
        similarity = _cosine_similarity(resume_text, jd_text)
        match_score = round(similarity * 100)
    except Exception:
        match_score = 0

    # Missing Skills
    resume_skills = set(
        s["name"] if isinstance(s, dict) else s
        for s in extract_skills(resume_text)
    )
    jd_skills = set(
        s["name"] if isinstance(s, dict) else s
        for s in extract_skills(jd_text)
    )
    missing_skills = list(jd_skills - resume_skills)

    return {
        "match_score": match_score,
        "missing_skills": missing_skills,
        "jd_skills": list(jd_skills)
    }


def generate_improvements(text: str, skills: list) -> list[str]:
    """Generate actionable improvements based on the resume text and extracted skills."""
    improvements = []
    text_lower = text.lower()

    # Handle both dict and string skill formats
    skill_count = len(skills)

    # Check for Action Verbs
    action_verbs = ["developed", "led", "managed", "created", "designed", "implemented", "optimized", "built"]
    found_verbs = sum(1 for verb in action_verbs if verb in text_lower)
    if found_verbs < 3:
        improvements.append("Use more strong action verbs (e.g., 'developed', 'led', 'optimized') to describe your experience.")

    # Check for Metrics/Numbers
    if not re.search(r'\d+%|\d+k|\$\d+', text_lower):
        improvements.append("Quantify your achievements with metrics and numbers (e.g., 'increased sales by 20%', 'managed $10k budget').")

    # Check for Education details
    edu_keywords = ["education", "university", "college", "degree"]
    if not any(word in text_lower for word in edu_keywords):
        improvements.append("Ensure your education details are clearly listed.")

    # Check Skills density
    if skill_count < 5:
        improvements.append("Your resume lacks specific technical keywords. Make sure to list relevant skills clearly.")

    # Check for links/portfolio
    if not re.search(r'github|linkedin|portfolio|website|http', text_lower):
        improvements.append("Add links to your GitHub, LinkedIn, or portfolio to showcase your work.")

    # Check for certifications
    if not re.search(r'certif|licensed|accredited', text_lower):
        improvements.append("Consider adding relevant certifications to strengthen your profile.")

    if not improvements:
        improvements.append("Your resume is well-structured and uses good action verbs. Tailor it to specific job descriptions for best results.")

    return improvements


def calculate_keyword_density(text: str, skills: list) -> dict:
    """
    Calculate keyword density for detected skills.
    
    Returns:
        dict with keyword_counts, total_words, and density_percentage
    """
    words = text.lower().split()
    total_words = len(words)

    if total_words == 0:
        return {"keyword_counts": {}, "total_words": 0, "density_percentage": {}}

    text_lower = text.lower()
    keyword_counts = {}

    for skill in skills:
        skill_name = skill["name"] if isinstance(skill, dict) else skill
        # Count occurrences of the skill in the text
        count = len(re.findall(re.escape(skill_name), text_lower))
        if count > 0:
            keyword_counts[skill_name] = count

    density_percentage = {
        skill: round((count / total_words) * 100, 2)
        for skill, count in keyword_counts.items()
    }

    return {
        "keyword_counts": keyword_counts,
        "total_words": total_words,
        "density_percentage": density_percentage
    }
