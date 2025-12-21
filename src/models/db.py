from pydantic import BaseModel


class Question(BaseModel):
    id: int
    question: str
    answer: str
    choices: list[str]
    explanation: str
    difficulty: int
    created_at: int
    course_id: int


class Course(BaseModel):
    id: int
    name: str
    description: str
    created_at: int
