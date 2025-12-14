from pydantic import BaseModel, Field


class LearningItem(BaseModel):
    question: str = Field(
        description="The question of the learning item. It could be a question, a word, a fill-in-the-blank, a multiple-choice, etc.",
    )
    answer: str
    choices: list[str]
    explanation: str
    difficulty: int = Field(
        description="The difficulty of the learning item. 1 is the easiest, 5 is the hardest.",
        ge=1,
        le=5,
    )


class Learning(BaseModel):
    items: list[LearningItem] = Field(
        description="A list of 3-5 learning items. Must contain at least 3 items."
    )
