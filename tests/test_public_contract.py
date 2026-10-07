import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password, password_hasher
from app.db.session import get_db
from app.main import app


def test_hash_is_argon2_and_verifies_without_plaintext():
    original = "una-clave-segura"
    hashed = hash_password(original)
    assert hashed.startswith("$argon2id$")
    assert original not in hashed
    assert password_hasher.verify(original, hashed)
    assert not password_hasher.verify("otra-clave", hashed)


@pytest.mark.parametrize("changes", [{"rol": "ADMINISTRADOR"}, {"password": "corta"}, {"correo": "incorrecto"}, {"nombre": "   "}])
def test_invalid_http_request_never_reveals_password_or_uses_database(changes):
    def no_database():
        yield None
    app.dependency_overrides[get_db] = no_database
    try:
        with TestClient(app) as client:
            payload = {"nombre": "María", "correo": "user@example.com", "password": "una-clave-segura", "rol": "ENTIDAD", **changes}
            response = client.post("/api/v1/auth/register", json=payload)
            assert response.status_code == 422
            assert response.json()["detail"]["code"] == "VALIDATION_ERROR"
            assert payload["password"] not in response.text
            assert all("input" not in item and "ctx" not in item for item in response.json()["detail"]["errors"])
    finally:
        app.dependency_overrides.clear()


def test_openapi_has_register_request_and_public_response():
    schema = app.openapi()
    operation = schema["paths"]["/api/v1/auth/register"]["post"]
    assert {"201", "409", "422"} <= set(operation["responses"])
    assert operation["responses"]["422"]["content"]["application/json"]["schema"]["$ref"].endswith("ApiErrorResponse")
    assert set(schema["components"]["schemas"]["UserResponse"]["properties"]) == {"id", "nombre", "correo", "rol"}
    assert "ADMINISTRADOR" not in schema["components"]["schemas"]["PublicUserRole"]["enum"]


def test_database_failure_returns_safe_503_with_cors(monkeypatch):
    from unittest.mock import Mock
    from sqlalchemy.exc import OperationalError
    import app.api.v1.auth as auth_module

    session = Mock()
    def unavailable(*args):
        raise OperationalError("SELECT users", {}, RuntimeError("private database diagnostic"))
    def override_db():
        yield session
    monkeypatch.setattr(auth_module, "register_user", unavailable)
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/auth/register", json={"nombre": "Prueba", "correo": "user@example.com", "password": "una-clave-segura", "rol": "CIUDADANO"}, headers={"Origin": "http://127.0.0.1:4200"})
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "REGISTRATION_UNAVAILABLE"
        assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:4200"
        assert "private database diagnostic" not in response.text
        session.rollback.assert_called_once()
    finally:
        app.dependency_overrides.clear()
