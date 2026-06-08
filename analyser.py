# analyser.py — Uses Groq API (free, no credit card, no quota errors)
# Groq runs Llama 3 (Meta's open source AI) for free
# Free limits: 14,400 requests/day, 30 requests/minute — very generous

import json
import re
from groq import Groq
from parser import get_word_count, get_resume_sections


def build_prompt(resume_text: str, job_desc: str = "") -> str:
    """
    PROMPT ENGINEERING — carefully crafted instructions for the AI.
    The better the prompt, the better the output.
    """

    word_count       = get_word_count(resume_text)
    sections         = get_resume_sections(resume_text)
    found_sections   = [k for k, v in sections.items() if v]
    missing_sections = [k for k, v in sections.items() if not v]

    # Inject job description into prompt if provided (RAG-lite technique)
    job_context = ""
    if job_desc and job_desc.strip():
        job_context = f"""
JOB DESCRIPTION (match the resume against this):
{job_desc.strip()}

Because a job description is provided, include "jobMatch" as an extra score (0-100).
"""

    prompt = f"""You are a senior HR consultant and ATS expert with 15 years of experience.

Analyse the resume below and return ONLY a valid JSON object. No extra text. No markdown. Just raw JSON.

RESUME INFO:
- Word count: {word_count}
- Sections found: {', '.join(found_sections) if found_sections else 'none detected'}
- Sections missing: {', '.join(missing_sections) if missing_sections else 'none'}
{job_context}

RESUME TEXT:
{resume_text[:4000]}

Return exactly this JSON (add jobMatch inside scores only if job description was given):
{{
  "scores": {{
    "overall": <integer 0-100>,
    "ats": <integer 0-100>,
    "impact": <integer 0-100>,
    "clarity": <integer 0-100>
  }},
  "summary": "<2-3 sentence honest assessment of this resume>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>", "<strength 4>"],
  "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>", "<improvement 4>"],
  "keywordsFound": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"],
  "keywordsMissing": ["<missing1>", "<missing2>", "<missing3>", "<missing4>"],
  "rewrittenSummary": "<A powerful 3-4 sentence professional summary rewritten for ATS and recruiters based on this candidate's actual background>"
}}

Scoring rules:
- Be honest. Average resumes score 40-65. Only exceptional ones score 80+.
- ats: standard headers, no tables blocking parsing, relevant keywords present
- impact: strong action verbs, quantified achievements (numbers/%)
- clarity: well structured, easy to scan in 6 seconds
- Reference actual content from the resume in strengths and improvements."""

    return prompt


def call_groq(prompt: str, api_key: str) -> str:
    """
    Calls Groq API with Llama 3.
    Groq is FREE — no credit card, 14,400 requests/day limit.
    API key starts with gsk_
    """

    # Create Groq client
    client = Groq(api_key=api_key)

    # Call the model
    # llama-3.3-70b-versatile = very smart, completely free on Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional resume analyst. "
                    "Always respond with raw valid JSON only. "
                    "No markdown code fences. No explanations. Just the JSON object."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,       # Low = more consistent output
        max_tokens=2000,
    )

    # Extract text from response
    return response.choices[0].message.content


def parse_response(raw: str) -> dict:
    """
    Converts AI text response → Python dictionary.
    Handles cases where the model adds extra text or markdown.
    """

    cleaned = raw.strip()

    # Remove markdown code fences if model added them
    cleaned = re.sub(r'^```json\s*', '', cleaned)
    cleaned = re.sub(r'^```\s*',     '', cleaned)
    cleaned = re.sub(r'```\s*$',     '', cleaned)
    cleaned = cleaned.strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from within the text
    match = re.search(r'\{[\s\S]*\}', cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not parse AI response. Please try again.")


def validate_scores(result: dict) -> dict:
    """Makes sure all scores are valid integers between 0 and 100."""
    if "scores" in result:
        for key in result["scores"]:
            try:
                result["scores"][key] = max(0, min(100, int(result["scores"][key])))
            except (ValueError, TypeError):
                result["scores"][key] = 50
    return result


def analyse_resume(resume_text: str, job_desc: str, api_key: str) -> dict:
    """
    Main function — called from app.py
    1. Build prompt
    2. Call Groq (Llama 3)
    3. Parse JSON response
    4. Return result
    """
    prompt     = build_prompt(resume_text, job_desc)
    raw        = call_groq(prompt, api_key)
    result     = parse_response(raw)
    result     = validate_scores(result)
    return result
