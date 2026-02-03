# ai_llm.py
import requests
from typing import List, Dict
import os

# Default model
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:3b")

SYSTEM_PROMPT = """You are an AI Interview Coach.
- Ask one interview question at a time.
- Adapt to the user's field: {field}; difficulty: {difficulty}; tag/keyword: {tag}. 
- Keep questions concise and clear.
- After the user answers, briefly (1–2 lines) give constructive feedback,
  then ask the next question.
- Stop after ~5–8 questions or when asked to stop.
"""

def chat_with_model(history: List[Dict[str, str]], user_msg: str,
                   field: str = "General", difficulty: str = "Any", tag: str = "") -> str:
    """
    Interactive chat mode with AI coach.
    The AI will ask questions according to the selected difficulty: easy, medium, hard.
    """
    sys_msg = {
        "role": "system",
        "content": SYSTEM_PROMPT.format(field=field, difficulty=difficulty, tag=tag)
    }

    messages = [sys_msg] + history + [{"role": "user", "content": user_msg}]

    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/chat",
            json={"model": MODEL_NAME, "messages": messages, "stream": False},
            timeout=600
        )
        response.raise_for_status()
        data = response.json()

        if "message" in data and "content" in data["message"]:
            return data["message"]["content"].strip()
        else:
            return f"Coach: Unexpected response format: {data}"

    except requests.exceptions.RequestException as e:
        return f"Coach: Error contacting AI coach: {e}"



# 🚀 New function for structured questions (resume-based)
def generate_resume_questions(summary: str, field: str = "General") -> Dict[str, List[str]]:
    """
    Generate HR, Technical, and Project-specific questions from a resume summary.
    """

    prompt = f"""
You are an AI interview coach.
The candidate's field is **{field}**.
Here is their resume summary:
---
{summary}
---

Now generate three separate sets of interview questions:

1. HR Questions (4–5 common HR questions)
2. Technical Questions (6–8 questions tailored to {field})
3. Project-Specific Questions (3–4 questions based on resume and {field})

Return the output in **JSON format** like this:
{{
  "hr": ["q1", "q2", ...],
  "technical": ["q1", "q2", ...],
  "project": ["q1", "q2", ...]
}}
    """

    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=600
        )
        response.raise_for_status()
        data = response.json()

        if "response" in data:
            import json
            try:
                return json.loads(data["response"])
            except Exception:
                # fallback: just return raw text
                return {"raw_output": data["response"]}
        else:
            return {"error": f"Unexpected format: {data}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error contacting AI coach: {e}"}
