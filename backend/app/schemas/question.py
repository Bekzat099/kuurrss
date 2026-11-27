from pydantic import BaseModel, ConfigDict, Field


class QuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=5, max_length=2000)
    options: list[str] = Field(..., min_length=2, max_length=6)
    correct_option: int = Field(..., ge=0, le=3)


class QuestionUpdate(BaseModel):
    question_text: str | None = Field(default=None, min_length=5, max_length=2000)
    options: list[str] | None = Field(default=None, min_length=2, max_length=6)
    correct_option: int | None = Field(default=None, ge=0, le=3)


class QuestionRead(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    options: list[str]
    correct_option: int

    model_config = ConfigDict(from_attributes=True)
