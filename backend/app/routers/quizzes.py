from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.repositories.quiz_repository import QuizRepository
from app.schemas.quiz import QuizCreate, QuizForTeacher, QuizUpdate
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


def get_quiz_service(db: Annotated[Session, Depends(get_db)]) -> QuizService:
    return QuizService(QuizRepository(db))


@router.get("", response_model=list[QuizForTeacher])
def list_quizzes(
    service: Annotated[QuizService, Depends(get_quiz_service)],
) -> list[QuizForTeacher]:
    return service.list_quizzes()


@router.post("", response_model=QuizForTeacher, status_code=status.HTTP_201_CREATED)
def create_quiz(
    data: QuizCreate,
    service: Annotated[QuizService, Depends(get_quiz_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> QuizForTeacher:
    return service.create_quiz(data, user)


@router.get("/{quiz_id}", response_model=QuizForTeacher)
def get_quiz(
    quiz_id: int,
    service: Annotated[QuizService, Depends(get_quiz_service)],
) -> QuizForTeacher:
    return service.get_quiz(quiz_id)


@router.patch("/{quiz_id}", response_model=QuizForTeacher)
def update_quiz(
    quiz_id: int,
    data: QuizUpdate,
    service: Annotated[QuizService, Depends(get_quiz_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> QuizForTeacher:
    return service.update_quiz(quiz_id, data, user)


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    service: Annotated[QuizService, Depends(get_quiz_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> None:
    service.delete_quiz(quiz_id, user)
