from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator

from app.models.user import UserRole


class PublicUserRole(StrEnum):
    CIUDADANO = "CIUDADANO"
    VOLUNTARIO = "VOLUNTARIO"
    ENTIDAD = "ENTIDAD"


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str = Field(min_length=1, max_length=120)
    correo: EmailStr = Field(max_length=254)
    password: SecretStr = Field(min_length=8, max_length=128)
    rol: PublicUserRole

    @field_validator("nombre", mode="before")
    @classmethod
    def trim_name(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("correo", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def reject_blank_password(cls, value):
        if not value.get_secret_value().strip():
            raise ValueError("La contraseña no puede contener solo espacios")
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str
    correo: EmailStr
    rol: UserRole


class ValidationIssue(BaseModel):
    field: str
    type: str
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    errors: list[ValidationIssue] | None = None


class ApiErrorResponse(BaseModel):
    detail: ErrorDetail
