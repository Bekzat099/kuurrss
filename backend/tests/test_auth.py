from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


def test_auth_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_auth_me_with_malformed_token_returns_401(client: TestClient) -> None:
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-jwt-token"},
    )
    assert response.status_code == 401


def test_auth_me_with_expired_token_returns_401(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    token = make_token(exp_offset=-60)
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_auth_me_with_wrong_issuer_returns_401(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    token = make_token(iss="http://evil.local/realms/quizai")
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_auth_me_with_wrong_audience_returns_401(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    token = make_token(aud="other-api")
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_auth_me_with_wrong_signature_returns_401(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    token = make_token(use_other_key=True)
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_auth_me_without_app_role_returns_403(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    token = make_token(roles=["offline_access", "uma_authorization"])
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_first_login_creates_user_and_picks_highest_role(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    token = make_token(
        sub="kc-teacher-1",
        email="teacher@demo.kz",
        name="Teacher Demo",
        roles=["student", "teacher"],
    )
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["keycloak_id"] == "kc-teacher-1"
    assert body["email"] == "teacher@demo.kz"
    assert body["role"] == "teacher"


def test_legacy_user_bound_by_email_on_sync(
    client: TestClient,
    db_session: Session,
    make_token: Callable[..., str],
) -> None:
    legacy = User(
        keycloak_id="legacy-placeholder",
        email="legacy@demo.kz",
        full_name="Legacy User",
        role="student",
    )
    db_session.add(legacy)
    db_session.commit()
    db_session.refresh(legacy)

    token = make_token(
        sub="kc-new-sub-99",
        email="legacy@demo.kz",
        name="Updated Legacy",
        roles=["teacher"],
    )
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == legacy.id
    assert body["keycloak_id"] == "kc-new-sub-99"
    assert body["role"] == "teacher"


def test_admin_users_endpoints_and_self_delete_protection(
    client: TestClient,
    make_token: Callable[..., str],
) -> None:
    student_token = make_token(
        sub="kc-student-1",
        email="student@demo.kz",
        roles=["student"],
    )
    admin_token = make_token(
        sub="kc-admin-1",
        email="admin@demo.kz",
        roles=["admin"],
    )

    # Student attempts to list users -> 403
    r_forbidden = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert r_forbidden.status_code == 403

    # Register student in DB via /api/auth/me
    r_student = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    student_id = r_student.json()["id"]

    # Admin lists users -> 200
    r_list = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 2

    # Admin gets own profile to check self-delete protection -> 400
    r_admin = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    admin_id = r_admin.json()["id"]
    r_self_del = client.delete(
        f"/api/users/{admin_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_self_del.status_code == 400

    # Admin deletes student -> 204
    r_del = client.delete(
        f"/api/users/{student_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_del.status_code == 204
