# ai_interview_coach/prompt_templates.py

RESUME_QUESTION_PROMPT = """
You are an expert interviewer.
Read the candidate resume summary below and generate interview questions.

Categories:
- HR: 4 questions
- Technical: 8 questions
- Project: 4 questions

Return JSON with keys: 'hr', 'technical', 'project'

<RESUME_SUMMARY>
{summary}
</RESUME_SUMMARY>
"""
