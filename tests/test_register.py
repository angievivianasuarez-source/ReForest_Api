from uuid import UUID

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.core.security import password_hasher
from app.models.user import User

PAYLOAD = {"nombre": "  María Niño  ", "correo": " PERSONA@EXAMPLE.COM ",
           "password": "una-clave-segura", "rol": "CIUDADANO"}


@pytest.mark.parametrize("role", ["CIUDADANO", "VOLUNTARIO", "ENTIDAD"])
def test_register_persists_hash_and_public_fields(client, db, role):
    payload = {**PAYLOAD, "rol": role}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "nombre", "correo", "rol"}
    UUID(body["id"])
    assert body["nombre"] == "María Niño"
    assert body["correo"] == "persona@example.com"
    assert body["rol"] == role
    user = db.scalar(select(User).where(User.correo == body["correo"]))
    assert user is not None and user.activo is True
    assert user.password_hash != payload["password"]
    assert user.password_hash.startswith("$argon2id$")
    assert password_hasher.verify(payload["password"], user.password_hash)
    assert user.created_at.tzinfo is not None


def test_duplicate_email_is_normalized_and_returns_409(client, db):
    assert client.post("/api/v1/auth/register", json=PAYLOAD).status_code == 201
    response = client.post("/api/v1/auth/register", json={**PAYLOAD, "correo": "persona@example.com"})
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "EMAIL_ALREADY_REGISTERED"
    assert len(db.scalars(select(User)).all()) == 1


@pytest.mark.parametrize("field,value", [
    ("nombre", "   "), ("nombre", "x" * 121), ("correo", "invalid"),
    ("password", "short"), ("password", "x" * 129), ("password", " " * 8),
    ("rol", "ADMINISTRADOR"), ("rol", "OTHER"), ("password_hash", "secret")])
def test_invalid_input_does_not_persist_or_echo_password(client, db, field, value):
    payload = {**PAYLOAD, field: value}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "VALIDATION_ERROR"
    assert payload["password"] not in response.text
    assert "password_hash" not in response.text or field == "password_hash"
    assert db.scalar(select(User)) is None


def test_database_rejects_invalid_role_and_duplicate_email(db):
    base = "INSERT INTO users (id,nombre,correo,password_hash,rol) VALUES (:id,:nombre,:correo,:hash,:rol)"
    parameters = {"id": "00000000-0000-0000-0000-000000000001", "nombre": "Prueba", "correo": "test@example.com", "hash": "hash", "rol": "OTHER"}
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(text(base), parameters)
    parameters["rol"] = "CIUDADANO"
    db.execute(text(base), parameters)
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(text(base), {**parameters, "id": "00000000-0000-0000-0000-000000000002"})


def test_cors_allows_local_angular(client):
    response = client.options("/api/v1/auth/register", headers={"Origin": "http://localhost:4200", "Access-Control-Request-Method": "POST"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4200"
