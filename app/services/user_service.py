from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import add_user, find_by_email
from app.schemas.user import RegisterRequest


class EmailAlreadyRegistered(Exception):
    pass


def register_user(db: Session, request: RegisterRequest) -> User:
    if find_by_email(db, str(request.correo)) is not None:
        raise EmailAlreadyRegistered
    user = User(nombre=request.nombre, correo=str(request.correo),
                password_hash=hash_password(request.password.get_secret_value()),
                rol=request.rol.value)
    try:
        add_user(db, user)
        db.commit()
        db.refresh(user)
    except IntegrityError as error:
        db.rollback()
        # PostgreSQL protege también los registros concurrentes del mismo correo.
        if getattr(getattr(error.orig, "diag", None), "constraint_name", None) == "uq_users_correo":
            raise EmailAlreadyRegistered from None
        raise
    return user
