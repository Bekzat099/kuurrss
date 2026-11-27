from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SubmissionCreate(BaseModel):
    quiz_id: int | None = None
    answers: dict[str, int] | list[int] = Field(..., description="Жауаптар тізімі немесе сөздігі")


class SubmissionRead(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    answers: dict[str, Any] | list[Any]
    score: int
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)
