from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Text, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(StrEnum):
    CIUDADANO = "CIUDADANO"
    VOLUNTARIO = "VOLUNTARIO"
    ENTIDAD = "ENTIDAD"
    ADMINISTRADOR = "ADMINISTRADOR"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(btrim(nombre)) > 0", name="nombre_no_vacio"),
        CheckConstraint("length(btrim(correo)) > 0", name="correo_no_vacio"),
        CheckConstraint("correo = lower(btrim(correo))", name="correo_normalizado"),
        CheckConstraint("length(btrim(password_hash)) > 0", name="hash_no_vacio"),
        CheckConstraint("rol IN ('CIUDADANO', 'VOLUNTARIO', 'ENTIDAD', 'ADMINISTRADOR')", name="rol_valido"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(120))
    correo: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    rol: Mapped[str] = mapped_column(String(13))
    activo: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
