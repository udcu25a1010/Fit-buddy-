import json
import uuid
from typing import Any

from utils import call_gemini, clean_json_response, parse_gemini_json

# In-memory quiz sessions (quiz_id -> full questions with answers)
_quiz_sessions: dict[str, list[dict[str, Any]]] = {}


def generate_quiz(topic_or_text: str, num_questions: int = 5) -> list[dict[str, Any]]:
    prompt = f"""You are EduGenie, an educational quiz generator for students.

Generate exactly {num_questions} multiple-choice questions based on the topic or passage below.
Each question must have exactly 4 options (A, B, C, D) and one correct answer letter.

Return ONLY valid JSON as an array:
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "First option",
      "B": "Second option",
      "C": "Third option",
      "D": "Fourth option"
    }},
    "answer": "A"
  }}
]

Topic or passage:
{topic_or_text}"""

    raw = call_gemini(prompt, temperature=0.8)

    try:
        parsed = parse_gemini_json(raw)
    except json.JSONDecodeError:
        cleaned = clean_json_response(raw)
        start = cleaned.find("[")
        end = cleaned.rfind("]") + 1
        if start >= 0 and end > start:
            parsed = json.loads(cleaned[start:end])
        else:
            raise ValueError("Could not parse quiz JSON from model response.")

    if isinstance(parsed, dict) and "questions" in parsed:
        parsed = parsed["questions"]

    if not isinstance(parsed, list):
        raise ValueError("Quiz response must be a list of questions.")

    return parsed


def create_quiz_session(questions: list[dict[str, Any]]) -> str:
    quiz_id = str(uuid.uuid4())
    _quiz_sessions[quiz_id] = questions
    return quiz_id


def get_quiz_session(quiz_id: str) -> list[dict[str, Any]] | None:
    return _quiz_sessions.get(quiz_id)


def delete_quiz_session(quiz_id: str) -> None:
    _quiz_sessions.pop(quiz_id, None)


def score_quiz(questions: list[dict[str, Any]], user_answers: list[str]) -> dict[str, Any]:
    if len(user_answers) != len(questions):
        raise ValueError("Please answer all questions before submitting.")

    results = []
    correct_count = 0

    for i, q in enumerate(questions):
        correct = str(q.get("answer", "")).upper().strip()
        user = str(user_answers[i]).upper().strip()
        is_correct = user == correct
        if is_correct:
            correct_count += 1

        results.append({
            "question": q.get("question", ""),
            "options": q.get("options", {}),
            "your_answer": user,
            "correct_answer": correct,
            "is_correct": is_correct,
        })

    total = len(questions)
    return {
        "score": correct_count,
        "total": total,
        "percentage": round(correct_count / total * 100) if total else 0,
        "results": results,
    }
