from typing import Any

from utils import call_gemini, parse_gemini_json


def get_answer(question: str) -> dict[str, Any]:
    prompt = f"""You are EduGenie, a friendly educational assistant for students.

Answer the following question in a clear, student-friendly way.
Return ONLY valid JSON with this exact structure (no markdown fences):
{{
  "direct_answer": "A concise direct answer",
  "explanation": "A detailed but easy-to-understand explanation",
  "extra_learning": ["point 1", "point 2", "point 3"]
}}

Question: {question}"""

    raw = call_gemini(prompt)
    return parse_gemini_json(raw)
