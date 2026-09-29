from typing import Any

from utils import call_gemini, parse_gemini_json


def get_learning_recommendations(topic: str) -> dict[str, Any]:
    prompt = f"""You are EduGenie, a learning path advisor for students and self-learners.

Create a structured learning path for the topic below.
Return ONLY valid JSON with this exact structure (no markdown fences):
{{
  "topic": "{topic}",
  "beginner": {{
    "description": "What to learn at beginner level",
    "topics": ["topic 1", "topic 2", "topic 3"]
  }},
  "intermediate": {{
    "description": "What to learn at intermediate level",
    "topics": ["topic 1", "topic 2", "topic 3"]
  }},
  "advanced": {{
    "description": "What to learn at advanced level",
    "topics": ["topic 1", "topic 2", "topic 3"]
  }},
  "resources": [
    {{"name": "Resource name", "type": "course/book/video/docs", "description": "Why it helps"}}
  ],
  "advice": "Practical advice for learning this topic effectively"
}}

Topic: {topic}"""

    raw = call_gemini(prompt)
    return parse_gemini_json(raw)
