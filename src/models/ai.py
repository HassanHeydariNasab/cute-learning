from pydantic import BaseModel, Field


class CreateQuestionInput(BaseModel):
    question: str = Field(
        description="The content of the question. It could be a complete question, single word, sentence, fill-in-the-blank, etc.",
    )
    answer: str = Field(
        description="The answer to the question. It should be one of the choices.",
    )
    choices: list[str] = Field(
        description="A list of 2-4 choices. The answer should be one of the choices.",
        min_length=2,
        max_length=4,
    )
    explanation: str = Field(
        description="A brief explanation of the question and answer. If it's a tricky/confusing/difficult question, provide a detailed explanation.",
    )
    difficulty: int = Field(
        description="The difficulty of the question. 1 is the easiest, 5 is the hardest.",
        ge=1,
        le=5,
    )


class CreateCourseInput(BaseModel):
    name: str
    description: str
    questions: list[CreateQuestionInput] = Field(
        description="A list of 3-5 questions. Must contain at least 3 questions."
    )
