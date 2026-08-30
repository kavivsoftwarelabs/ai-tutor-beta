from pydantic import BaseModel


class DiagnosticRequest(BaseModel):
    topic: str
    weak_areas: list[str] = []


class QuizItem(BaseModel):
    id: str
    question: str
    options: list[str]
    correct_answer: str


class SessionPlan(BaseModel):
    priority: float
    recommended_topic: str
    actions: list[str]
