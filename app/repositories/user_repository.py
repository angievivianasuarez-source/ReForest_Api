from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def find_by_email(db: Session, correo: str) -> User | None:
    return db.scalar(select(User).where(User.correo == correo))


def add_user(db: Session, user: User) -> None:
    db.add(user)
    db.flush()
