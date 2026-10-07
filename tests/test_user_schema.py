import pytest
from pydantic import ValidationError

from app.schemas.user import RegisterRequest


def test_schema_normalizes_name_and_email_and_hides_password():
    request = RegisterRequest(nombre="  María  ", correo=" PERSONA@EXAMPLE.COM ", password="una-clave-segura", rol="ENTIDAD")
    assert request.nombre == "María"
    assert str(request.correo) == "persona@example.com"
    assert "una-clave-segura" not in repr(request)


@pytest.mark.parametrize("role", ["ADMINISTRADOR", "OTHER", ""])
def test_schema_rejects_non_public_roles(role):
    with pytest.raises(ValidationError):
        RegisterRequest(nombre="Usuario", correo="user@example.com", password="una-clave-segura", rol=role)
