from builtins import list as ListType

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Identity
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> ListType[User]:
        stmt = select(User).order_by(User.id)
        return ListType(self.db.scalars(stmt).all())

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_keycloak_id(self, keycloak_id: str) -> User | None:
        stmt = select(User).where(User.keycloak_id == keycloak_id)
        return self.db.scalars(stmt).first()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()

    def sync(self, identity: Identity, role: str) -> User:
        email = identity.email or f"{identity.keycloak_id}@quizai.local"
        full_name = identity.name or email

        user = self.get_by_keycloak_id(identity.keycloak_id)
        if user is None:
            # Привязка legacy-записи по email, если она существовала ранее
            user = self.get_by_email(email)
            if user is not None:
                user.keycloak_id = identity.keycloak_id
                user.full_name = full_name
                user.role = role
            else:
                user = User(
                    keycloak_id=identity.keycloak_id,
                    email=email,
                    full_name=full_name,
                    role=role,
                )
                self.db.add(user)
        else:
            user.email = email
            user.full_name = full_name
            user.role = role

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
