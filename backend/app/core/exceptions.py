class DomainError(Exception):
    """Базалық домендік қате (HTTPException емес)."""


class BadRequestError(DomainError):
    """Бизнес-ереже бұзылған кезде лақтырылатын қате (HTTP 400)."""


class AuthError(DomainError):
    """Аутентификациядан өтпеген кезде лақтырылатын қате (HTTP 401)."""


UnauthorizedError = AuthError


class ForbiddenError(DomainError):
    """Құқық жеткіліксіз болған кезде лақтырылатын қате (HTTP 403)."""


class NotFoundError(DomainError):
    """Объект табылмаған кезде лақтырылатын қате (HTTP 404)."""


class ConflictError(DomainError):
    """Қайшылық / қайталану кезінде лақтырылатын қате (HTTP 409)."""


class ServiceUnavailableError(DomainError):
    """Сыртқы сервис (Keycloak) қолжетімсіз болған кездегі қате (HTTP 503)."""
