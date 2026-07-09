"""
Resume formatting analysis service.
Checks structure, section headers, length, bullet points, and overall quality.
"""
import re


EXPECTED_SECTIONS = [
    "education", "experience", "work experience", "skills",
    "projects", "certifications", "summary", "objective",
    "achievements", "awards", "publications", "references",
    "professional experience", "technical skills", "interests",
    "volunteer", "training", "courses"
]

CORE_SECTIONS = ["education", "experience", "work experience", "skills"]


def analyze_formatting(text: str) -> dict:
    """
    Analyze resume formatting and return a detailed quality report.
    
    Returns:
        dict with formatting_score, sections_found, sections_missing,
        issues, page_estimate, and word_count.
    """
    if not text or not text.strip():
        return {
            "formatting_score": 0,
            "sections_found": [],
            "sections_missing": list(CORE_SECTIONS),
            "issues": ["Resume appears to be empty or unreadable."],
            "page_estimate": 0,
            "word_count": 0
        }

    text_lower = text.lower()
    lines = text.strip().split("\n")
    words = text.split()
    word_count = len(words)
    issues = []
    score = 0

    # --- Section Detection (30 points) ---
    sections_found = []
    for section in EXPECTED_SECTIONS:
        # Look for section headers — typically a line that starts with the section name
        pattern = r'(?:^|\n)\s*' + re.escape(section) + r'\s*(?:\n|:|\-|$)'
        if re.search(pattern, text_lower):
            sections_found.append(section.title())

    # Normalize duplicates (e.g., "Experience" and "Work Experience")
    sections_found = list(set(sections_found))

    core_found = sum(
        1 for s in CORE_SECTIONS
        if s.title() in sections_found or
        any(s in found.lower() for found in sections_found)
    )
    section_score = min(core_found * 7.5, 30)
    score += section_score

    # Check missing core sections
    sections_missing = []
    for s in CORE_SECTIONS:
        if s.title() not in sections_found and not any(s in found.lower() for found in sections_found):
            sections_missing.append(s.title())

    if sections_missing:
        issues.append(f"Missing important sections: {', '.join(sections_missing)}.")

    # --- Length Check (20 points) ---
    if word_count < 150:
        issues.append("Resume is too short. Aim for at least 300 words for a one-page resume.")
        score += 5
    elif word_count < 300:
        issues.append("Resume could be more detailed. Consider expanding your descriptions.")
        score += 12
    elif word_count <= 1000:
        score += 20  # Ideal length
    elif word_count <= 1500:
        score += 15
        issues.append("Resume may be too long. Consider trimming to 1-2 pages for most roles.")
    else:
        score += 8
        issues.append("Resume is very long. Recruiters typically spend 6-7 seconds scanning — keep it concise.")

    # --- Bullet Point Usage (15 points) ---
    bullet_patterns = [r'^\s*[\•\-\*\→\▪\●\○]', r'^\s*\d+[\.\)]']
    bullet_count = 0
    for line in lines:
        for pattern in bullet_patterns:
            if re.match(pattern, line):
                bullet_count += 1
                break

    if bullet_count >= 8:
        score += 15
    elif bullet_count >= 4:
        score += 10
    elif bullet_count >= 1:
        score += 5
        issues.append("Use more bullet points to improve readability.")
    else:
        issues.append("No bullet points detected. Use bullet points to list achievements and responsibilities.")

    # --- Contact Information (10 points) ---
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    has_phone = bool(re.search(r'[\+]?[\d\s\-\(\)]{7,15}', text))
    has_linkedin = bool(re.search(r'linkedin', text_lower))

    contact_score = 0
    if has_email:
        contact_score += 4
    else:
        issues.append("No email address detected.")
    if has_phone:
        contact_score += 3
    else:
        issues.append("No phone number detected.")
    if has_linkedin:
        contact_score += 3

    score += contact_score

    # --- Consistency Checks (15 points) ---
    consistency_score = 0

    # Check for all-caps section headers (good formatting practice)
    caps_headers = len(re.findall(r'^[A-Z][A-Z\s&]{2,}$', text, re.MULTILINE))
    if caps_headers >= 2:
        consistency_score += 5

    # Check for reasonable line length (not walls of text)
    long_lines = sum(1 for line in lines if len(line) > 150)
    if long_lines == 0:
        consistency_score += 5
    elif long_lines <= 3:
        consistency_score += 3
    else:
        issues.append("Some lines are very long. Break up long paragraphs for better readability.")

    # Check for reasonable number of lines (not too dense)
    non_empty_lines = [l for l in lines if l.strip()]
    if len(non_empty_lines) >= 15:
        consistency_score += 5
    elif len(non_empty_lines) >= 8:
        consistency_score += 3

    score += consistency_score

    # --- Dates Detection (10 points) ---
    date_patterns = [
        r'\b\d{4}\b',  # Year like 2023
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}\b',  # Month Year
        r'\b\d{1,2}/\d{4}\b',  # MM/YYYY
    ]
    dates_found = 0
    for pattern in date_patterns:
        dates_found += len(re.findall(pattern, text_lower))

    if dates_found >= 4:
        score += 10
    elif dates_found >= 2:
        score += 6
    elif dates_found >= 1:
        score += 3
    else:
        issues.append("No dates detected. Include dates for your experience and education.")

    # Clamp score
    score = min(round(score), 100)

    # Page estimate (approx 500 words per page)
    page_estimate = max(1, round(word_count / 500, 1))

    # If no issues, give positive feedback
    if not issues:
        issues.append("Your resume is well-formatted with good structure and readability.")

    return {
        "formatting_score": score,
        "sections_found": sections_found,
        "sections_missing": sections_missing,
        "issues": issues,
        "page_estimate": page_estimate,
        "word_count": word_count
    }
