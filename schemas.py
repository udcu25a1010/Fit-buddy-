"""
Pydantic schemas mirroring the ERD domain model.
Ready for future SQLite/SQLAlchemy persistence — not wired to DB yet.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class QueryType(str, Enum):
    QNA = "QnA"
    EXPLANATION = "Explanation"
    QUIZ = "Quiz"
    SUMMARY = "Summary"
    RECOMMENDATION = "Recommendation"


class User(BaseModel):
    user_id: Optional[int] = None
    name: str
    email: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserQuery(BaseModel):
    query_id: Optional[int] = None
    user_id: Optional[int] = None
    query_type: QueryType
    query_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIResponse(BaseModel):
    response_id: Optional[int] = None
    query_id: Optional[int] = None
    response_text: str
    model_used: str = "gemini"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QuizRecord(BaseModel):
    quiz_id: Optional[int] = None
    query_id: Optional[int] = None
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SummaryRecord(BaseModel):
    summary_id: Optional[int] = None
    query_id: Optional[int] = None
    summary_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LearningPathRecord(BaseModel):
    path_id: Optional[int] = None
    query_id: Optional[int] = None
    topic: str
    difficulty_level: str
    recommended_resources: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
