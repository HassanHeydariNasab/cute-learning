from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str = Field(
        description="The content of the question. It could be a complete question, single word, sentence, fill-in-the-blank, etc.",
    )
    answer: str = Field(
        description="The answer to the question. It should be one of the choices.",
    )
    choices: list[str]
    explanation: str = Field(
        description="A brief explanation of the question and answer. If it's a tricky/confusing/difficult question, provide a detailed explanation.",
    )
    difficulty: int = Field(
        description="The difficulty of the question. 1 is the easiest, 5 is the hardest.",
        ge=1,
        le=5,
    )


class Course(BaseModel):
    name: str
    description: str
    questions: list[Question] = Field(
        description="A list of 3-5 questions. Must contain at least 3 questions."
    )
