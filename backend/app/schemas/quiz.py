from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QuizCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    source_text: str = Field(..., min_length=200)


class QuizUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    source_text: str | None = Field(default=None, min_length=200)
    status: Literal["draft", "published"] | None = None


class QuizRead(BaseModel):
    id: int
    title: str
    source_text: str
    status: str
    teacher_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizForTeacher(QuizRead):
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
