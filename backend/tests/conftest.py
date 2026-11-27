import time
from collections.abc import Callable, Generator
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.core.deps import get_token_verifier
from app.core.exceptions import AuthError
from app.core.security import KeycloakVerifier
from app.main import app

TEST_ISSUER = "http://localhost:8080/realms/quizai"
TEST_AUDIENCE = "quizai-api"


@pytest.fixture(scope="session")
def rsa_keys() -> dict[str, Any]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    other_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return {
        "private": private_key,
        "public": public_key,
        "other_private": other_private_key,
    }


class FakeKeycloakVerifier(KeycloakVerifier):
    def __init__(self, public_key: Any, issuer: str, audience: str) -> None:
        self.issuer = issuer
        self.jwks_url = "http://localhost:8080/realms/quizai/protocol/openid-connect/certs"
        self.audience = audience
        self._public_key = public_key

    def verify(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._public_key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={"require": ["exp", "iat", "iss", "sub", "aud"]},
            )
        except jwt.PyJWTError as exc:
            raise AuthError("Жарамсыз немесе мерзімі өткен токен") from exc


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(
    db_session: Session,
    rsa_keys: dict[str, Any],
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_verifier() -> KeycloakVerifier:
        return FakeKeycloakVerifier(
            public_key=rsa_keys["public"],
            issuer=TEST_ISSUER,
            audience=TEST_AUDIENCE,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_token_verifier] = override_get_verifier
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def make_token(rsa_keys: dict[str, Any]) -> Callable[..., str]:
    def _make_token(
        sub: str = "kc-user-1",
        email: str = "user@demo.kz",
        name: str = "Demo User",
        roles: list[str] | None = None,
        iss: str = TEST_ISSUER,
        aud: str = TEST_AUDIENCE,
        exp_offset: int = 300,
        use_other_key: bool = False,
    ) -> str:
        now = int(time.time())
        payload: dict[str, Any] = {
            "sub": sub,
            "email": email,
            "name": name,
            "iss": iss,
            "aud": aud,
            "iat": now,
            "exp": now + exp_offset,
            "realm_access": {"roles": roles if roles is not None else ["student"]},
        }
        signing_key = (
            rsa_keys["other_private"] if use_other_key else rsa_keys["private"]
        )
        return jwt.encode(payload, signing_key, algorithm="RS256")

    return _make_token
