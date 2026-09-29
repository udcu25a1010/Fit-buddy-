from typing import Any

from utils import call_gemini, parse_gemini_json


def summarize_text(text: str) -> dict[str, Any]:
    prompt = f"""You are EduGenie, an educational summarization assistant for students.

Summarize the following educational text.
Return ONLY valid JSON with this exact structure (no markdown fences):
{{
  "short_summary": "A concise summary in 2-4 sentences",
  "key_points": ["point 1", "point 2", "point 3"],
  "concepts": ["concept 1", "concept 2", "concept 3"]
}}

Text to summarize:
{text}"""

    raw = call_gemini(prompt)
    return parse_gemini_json(raw)
