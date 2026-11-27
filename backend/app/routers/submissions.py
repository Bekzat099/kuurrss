from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import BadRequestError
from app.models.user import User
from app.schemas.submission import SubmissionCreate, SubmissionRead
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/api", tags=["submissions"])


def get_submission_service(
    db: Annotated[Session, Depends(get_db)],
) -> SubmissionService:
    return SubmissionService(db)


@router.post(
    "/quizzes/{quiz_id}/submissions",
    response_model=SubmissionRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_quiz_by_id(
    quiz_id: int,
    data: SubmissionCreate,
    service: Annotated[SubmissionService, Depends(get_submission_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> SubmissionRead:
    return service.submit_quiz(quiz_id, data, user)


@router.post(
    "/submissions",
    response_model=SubmissionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_submission(
    data: SubmissionCreate,
    service: Annotated[SubmissionService, Depends(get_submission_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> SubmissionRead:
    if data.quiz_id is None:
        raise BadRequestError("quiz_id міндетті түрде көрсетілуі керек")
    return service.submit_quiz(data.quiz_id, data, user)


@router.get("/submissions/me", response_model=list[SubmissionRead])
def list_my_submissions(
    service: Annotated[SubmissionService, Depends(get_submission_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[SubmissionRead]:
    return service.list_my_submissions(user)


@router.get("/submissions", response_model=list[SubmissionRead])
def list_submissions(
    service: Annotated[SubmissionService, Depends(get_submission_service)],
    user: Annotated[User, Depends(get_current_user)],
    quiz_id: Annotated[int | None, Query()] = None,
) -> list[SubmissionRead]:
    return service.list_submissions(user, quiz_id=quiz_id)
