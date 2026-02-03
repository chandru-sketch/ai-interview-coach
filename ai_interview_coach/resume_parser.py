# ai_interview_coach/resume_parser.py
import os
import re
import pdfplumber
import docx2txt

def _extract_pdf_text(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            text_parts.append(txt)
    return "\n".join(text_parts)

def _extract_docx_text(path: str) -> str:
    return docx2txt.process(path) or ""

def extract_resume_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return _extract_pdf_text(file_path)
    if ext in [".docx", ".doc"]:
        return _extract_docx_text(file_path)
    return ""

def parse_sections(raw: str):
    text = raw.replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n\n", text)

    headers = ["education", "skills", "projects", "experience"]
    patt = r"^(?P<header>" + r"|".join(headers) + r")\b"

    lines = text.split("\n")
    sections = {"misc": []}
    current = "misc"

    for ln in lines:
        ln_norm = ln.strip().lower()
        if re.match(patt, ln_norm):
            current = ln_norm
            sections[current] = []
        else:
            sections[current].append(ln)

    return {k: "\n".join(v).strip() for k, v in sections.items() if v}

def make_resume_summary(raw_text: str) -> str:
    sections = parse_sections(raw_text)
    skills = sections.get("skills", "(not found)")
    projects = sections.get("projects", "(not found)")
    experience = sections.get("experience", "(not found)")
    education = sections.get("education", "(not found)")

    return f"""
== SUMMARY FROM RESUME ==
Skills: {skills}
Projects: {projects}
Experience: {experience}
Education: {education}
""".strip()
