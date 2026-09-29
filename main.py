import asyncio
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from config import GEMINI_MODEL
from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from qna import get_answer
from quiz_module import (
    create_quiz_session,
    delete_quiz_session,
    generate_quiz,
    get_quiz_session,
    score_quiz,
)
from summary_module import summarize_text

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="EduGenie",
    description="Google Gemini Powered Learning Assistant",
    version="1.1.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

PAGES = {
    "index": {"title": "Home", "icon": "🏠"},
    "qa": {"title": "Ask a Question", "icon": "❓"},
    "explain": {"title": "Explain a Topic", "icon": "💡"},
    "quiz": {"title": "Quiz", "icon": "📝"},
    "summarize": {"title": "Summarize", "icon": "📄"},
    "learning_path": {"title": "Learning Path", "icon": "🗺️"},
}


# --- Request schemas ---

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


class TopicRequest(BaseModel):
    topic: str = Field(..., min_length=1)


class QuizRequest(BaseModel):
    topic_or_text: str = Field(..., min_length=1)
    num_questions: int = Field(default=5, ge=3, le=10)


class QuizSubmitRequest(BaseModel):
    quiz_id: str = Field(..., min_length=1)
    answers: list[str] = Field(..., min_length=1)


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=10)


class LearningPathRequest(BaseModel):
    topic: str = Field(..., min_length=1)


# --- Helpers ---

def page_context(request: Request, active: str) -> dict:
    return {"request": request, "active": active, "pages": PAGES}


def success_response(data: dict) -> JSONResponse:
    return JSONResponse({"success": True, "data": data, "model": GEMINI_MODEL})


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        {"success": False, "error": message},
        status_code=status_code,
    )


async def run_ai(func, *args):
    """Run blocking Gemini calls in a thread so the server stays responsive."""
    return await asyncio.to_thread(func, *args)


# --- Page routes ---

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(BASE_DIR / "static" / "edugenie.png")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request, "index.html", page_context(request, "index")
    )


@app.get("/qa", response_class=HTMLResponse)
async def qa_page(request: Request):
    return templates.TemplateResponse(
        request, "qa.html", page_context(request, "qa")
    )


@app.get("/explain", response_class=HTMLResponse)
async def explain_page(request: Request):
    return templates.TemplateResponse(
        request, "explain.html", page_context(request, "explain")
    )


@app.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request):
    return templates.TemplateResponse(
        request, "quiz.html", page_context(request, "quiz")
    )


@app.get("/summarize", response_class=HTMLResponse)
async def summarize_page(request: Request):
    return templates.TemplateResponse(
        request, "summarize.html", page_context(request, "summarize")
    )


@app.get("/learning-path", response_class=HTMLResponse)
async def learning_path_page(request: Request):
    return templates.TemplateResponse(
        request, "learning_path.html", page_context(request, "learning_path")
    )


# --- API routes ---

@app.post("/qa")
async def question_answering(body: QuestionRequest):
    question = body.question.strip()
    if not question:
        return error_response("Please enter a question.")
    try:
        result = await run_ai(get_answer, question)
        return success_response(result)
    except ValueError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f"Failed to get answer: {exc}", 500)


@app.post("/explain")
async def explain(body: TopicRequest):
    topic = body.topic.strip()
    if not topic:
        return error_response("Please enter a topic.")
    try:
        result = await run_ai(explain_topic, topic)
        return success_response(result)
    except ValueError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f"Failed to explain topic: {exc}", 500)


@app.post("/quiz")
async def quiz(body: QuizRequest):
    content = body.topic_or_text.strip()
    if not content:
        return error_response("Please enter a topic or passage.")
    try:
        result = await run_ai(generate_quiz, content, body.num_questions)
        quiz_id = create_quiz_session(result)
        public_questions = [
            {"question": q["question"], "options": q["options"]}
            for q in result
        ]
        return success_response({
            "quiz_id": quiz_id,
            "questions": public_questions,
            "total": len(result),
        })
    except ValueError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f"Failed to generate quiz: {exc}", 500)


@app.post("/quiz/submit")
async def quiz_submit(body: QuizSubmitRequest):
    stored = get_quiz_session(body.quiz_id)
    if not stored:
        return error_response("Quiz session expired. Please create a new quiz.")

    if len(body.answers) != len(stored):
        return error_response("Please answer all questions before submitting.")

    try:
        result = score_quiz(stored, body.answers)
        delete_quiz_session(body.quiz_id)
        return success_response(result)
    except ValueError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f"Failed to score quiz: {exc}", 500)


@app.post("/summarize")
async def summarize(body: SummarizeRequest):
    text = body.text.strip()
    if len(text) < 10:
        return error_response("Please enter at least 10 characters of text.")
    try:
        result = await run_ai(summarize_text, text)
        return success_response(result)
    except ValueError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f"Failed to summarize text: {exc}", 500)


@app.post("/learn/recommendations")
async def learning_recommendations(body: LearningPathRequest):
    topic = body.topic.strip()
    if not topic:
        return error_response("Please enter a topic.")
    try:
        result = await run_ai(get_learning_recommendations, topic)
        return success_response(result)
    except ValueError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f"Failed to generate learning path: {exc}", 500)


@app.get("/learn/recommendations")
async def learning_recommendations_get(topic: str = ""):
    topic = topic.strip()
    if not topic:
        return error_response("Please provide a topic query parameter.")
    try:
        result = await run_ai(get_learning_recommendations, topic)
        return success_response(result)
    except ValueError as exc:
        return error_response(str(exc))
    except Exception as exc:
        return error_response(f"Failed to generate learning path: {exc}", 500)
