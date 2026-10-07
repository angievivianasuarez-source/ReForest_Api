from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.v1.auth import router
from app.core.config import get_settings

app = FastAPI(title="ReForest API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors_origins,
                   allow_credentials=False, allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type"])
app.include_router(router)


class HealthResponse(BaseModel):
    status: Literal["ok"]


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Indica que la API responde; no comprueba dependencias externas."""
    return HealthResponse(status="ok")


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, error: RequestValidationError):
    # Nunca devolver input ni ctx: pueden contener la contraseña enviada.
    errors = [{"field": ".".join(str(part) for part in item["loc"][1:]),
               "type": item["type"], "message": "Valor inválido."} for item in error.errors()]
    return JSONResponse(status_code=422, content={"detail": {
        "code": "VALIDATION_ERROR", "message": "Revisa los datos del formulario.", "errors": errors}})
