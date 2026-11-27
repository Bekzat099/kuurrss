from dataclasses import dataclass
from typing import Any
from urllib.error import URLError

import jwt
from jwt.exceptions import PyJWKClientConnectionError

from app.core.exceptions import AuthError, ServiceUnavailableError

APP_ROLES = ("admin", "teacher", "student")


@dataclass(frozen=True)
class Identity:
    keycloak_id: str
    email: str | None = None
    name: str | None = None
    role: str | None = None


class KeycloakVerifier:
    def __init__(self, issuer: str, jwks_url: str, audience: str) -> None:
        self.issuer = issuer
        self.jwks_url = jwks_url
        self.audience = audience
        self._jwks = jwt.PyJWKClient(jwks_url, cache_keys=True)

    def verify(self, token: str) -> dict[str, Any]:
        try:
            key = self._jwks.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                key.key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={"require": ["exp", "iat", "iss", "sub", "aud"]},
            )
        except (PyJWKClientConnectionError, URLError) as exc:
            raise ServiceUnavailableError("Keycloak JWKS сервисі қолжетімсіз") from exc
        except jwt.PyJWTError as exc:
            raise AuthError("Жарамсыз немесе мерзімі өткен токен") from exc


def identity_from_claims(claims: dict[str, Any]) -> Identity:
    roles = set(claims.get("realm_access", {}).get("roles", []))
    role = next((r for r in APP_ROLES if r in roles), None)
    return Identity(
        keycloak_id=claims["sub"],
        email=claims.get("email"),
        name=claims.get("name") or claims.get("preferred_username"),
        role=role,
    )
