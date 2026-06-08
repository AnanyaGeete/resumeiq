# parser.py — Extracts text from uploaded resume files

import fitz   # PyMuPDF — reads PDF files
import re


def extract_text(uploaded_file) -> str:
    """
    Reads the uploaded file and returns plain text.
    Supports PDF and TXT formats.
    """

    name = uploaded_file.name.lower()

    # ── TXT FILE ──
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    # ── PDF FILE ──
    if name.endswith(".pdf"):
        pdf_bytes = uploaded_file.read()
        doc       = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages     = [doc[i].get_text() for i in range(len(doc))]
        doc.close()
        return clean_text("\n".join(pages))

    raise ValueError(f"Unsupported file: {name}. Please upload PDF or TXT.")


def clean_text(text: str) -> str:
    """Removes noise from extracted PDF text."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.replace('\t', ' ')
    lines = [' '.join(line.split()) for line in text.split('\n')]
    return '\n'.join(lines).strip()


def get_word_count(text: str) -> int:
    return len(text.split())


def get_resume_sections(text: str) -> dict:
    """Detects which standard resume sections are present."""
    t = text.lower()
    return {
        "experience":     any(w in t for w in ["experience", "work history", "employment"]),
        "education":      any(w in t for w in ["education", "degree", "university", "college"]),
        "skills":         any(w in t for w in ["skills", "technologies", "tools"]),
        "summary":        any(w in t for w in ["summary", "objective", "profile", "about"]),
        "projects":       any(w in t for w in ["projects", "portfolio"]),
        "certifications": any(w in t for w in ["certification", "certified", "certificate"]),
    }
