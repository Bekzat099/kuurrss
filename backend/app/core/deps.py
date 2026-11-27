from collections.abc import Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AuthError, ForbiddenError
from app.core.security import Identity, KeycloakVerifier, identity_from_claims
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_token_verifier() -> KeycloakVerifier:
    return KeycloakVerifier(
        issuer=settings.keycloak_issuer,
        jwks_url=settings.jwks_url,
        audience=settings.keycloak_audience,
    )


get_verifier = get_token_verifier


def get_current_identity(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    verifier: Annotated[KeycloakVerifier, Depends(get_token_verifier)],
) -> Identity:
    if credentials is None or not credentials.credentials:
        raise AuthError("Bearer токен берілмеген")
    claims = verifier.verify(credentials.credentials)
    return identity_from_claims(claims)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    identity: Annotated[Identity, Depends(get_current_identity)],
) -> User:
    if identity.role is None:
        raise ForbiddenError("Пайдаланушыға қолданба рөлі тағайындалмаған")
    repo = UserRepository(db)
    return repo.sync(identity, identity.role)


def require_role(*allowed_roles: str) -> Callable[[User], User]:
    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed_roles:
            raise ForbiddenError("Бұл әрекетке рұқсатыңыз жоқ")
        return user

    return dependency


require_roles = require_role
