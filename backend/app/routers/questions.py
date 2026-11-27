from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate
from app.services.question_service import QuestionService

router = APIRouter(prefix="/api", tags=["questions"])


def get_question_service(db: Annotated[Session, Depends(get_db)]) -> QuestionService:
    return QuestionService(db)


@router.post(
    "/quizzes/{quiz_id}/questions",
    response_model=QuestionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    quiz_id: int,
    data: QuestionCreate,
    service: Annotated[QuestionService, Depends(get_question_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> QuestionRead:
    return service.create_question(quiz_id, data, user)


@router.patch("/questions/{question_id}", response_model=QuestionRead)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    service: Annotated[QuestionService, Depends(get_question_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> QuestionRead:
    return service.update_question(question_id, data, user)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    service: Annotated[QuestionService, Depends(get_question_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> None:
    service.delete_question(question_id, user)
