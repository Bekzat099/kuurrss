from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_role("admin"))],
) -> list[UserRead]:
    repo = UserRepository(db)
    return [UserRead.model_validate(u) for u in repo.list()]


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_role("admin"))],
) -> UserRead:
    repo = UserRepository(db)
    target = repo.get(user_id)
    if target is None:
        raise NotFoundError(f"Пайдаланушы табылмады: id={user_id}")
    return UserRead.model_validate(target)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(require_role("admin"))],
) -> None:
    if user_id == admin.id:
        raise BadRequestError("Әкімші өзін-өзі өшіре алмайды")
    repo = UserRepository(db)
    target = repo.get(user_id)
    if target is None:
        raise NotFoundError(f"Пайдаланушы табылмады: id={user_id}")
    repo.delete(target)
