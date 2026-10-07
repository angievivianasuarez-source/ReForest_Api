# HU05 — Contrato de registro

POST /api/v1/auth/register, público. Content-Type: application/json.

```json
{"nombre":"María Niño","correo":"persona@example.com","password":"una-clave-segura","rol":"VOLUNTARIO"}
```

nombre: obligatorio, recorte de extremos, 1–120 caracteres. correo: válido, recorte y minúsculas, máximo 254. password: 8–128 caracteres, sin recorte; solo espacios no permitido. rol: CIUDADANO, VOLUNTARIO o ENTIDAD. Campos adicionales prohibidos.

201: id UUID como cadena, nombre, correo y rol. La respuesta nunca incluye password ni password_hash. No crea sesión.

409: `{"detail":{"code":"EMAIL_ALREADY_REGISTERED","message":"El correo ya está registrado."}}`.

422: `{"detail":{"code":"VALIDATION_ERROR","message":"Revisa los datos del formulario.","errors":[{"field":"rol","type":"enum","message":"Valor inválido."}]}}`.

Los errores excluyen la entrada original y el contexto interno de Pydantic para evitar exponer contraseñas. OpenAPI en /openapi.json define los esquemas de entrada y salida. Angular debe reflejar sus campos y roles.

Persistencia: users, según diccionario-datos.md, con UUID, correo único y normalizado, hash Argon2id, activo=true y fechas UTC. Una comprobación previa permite responder rápido a duplicados; UNIQUE(correo) protege además registros simultáneos.

CORS local: http://localhost:4200 y http://127.0.0.1:4200. CORS_ORIGINS puede configurarse con una lista JSON en el entorno de FastAPI.

503: `{"detail":{"code":"REGISTRATION_UNAVAILABLE","message":"El servicio de registro no está disponible temporalmente. Inténtalo de nuevo en unos minutos."}}`. Se devuelve cuando PostgreSQL no acepta conexiones; la transacción se revierte y se conservan los encabezados CORS.
