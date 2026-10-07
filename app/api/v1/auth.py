from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from app.schemas.user import ApiErrorResponse, RegisterRequest, UserResponse
from app.services.user_service import EmailAlreadyRegistered, register_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             responses={409: {"model": ApiErrorResponse, "description": "Correo ya registrado"},
                        422: {"model": ApiErrorResponse, "description": "Datos inválidos"},
                        503: {"model": ApiErrorResponse, "description": "Registro temporalmente no disponible"}})
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return register_user(db, request)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail={"code": "EMAIL_ALREADY_REGISTERED", "message": "El correo ya está registrado."}) from None

    except OperationalError:
        db.rollback()
        raise HTTPException(status_code=503, detail={"code": "REGISTRATION_UNAVAILABLE", "message": "El servicio de registro no está disponible temporalmente. Inténtalo de nuevo en unos minutos."}) from None
