# Evidencia de HU05

## Verificaciones ejecutadas

- `python -m pytest -q`: 11 pruebas aprobadas; 15 pruebas PostgreSQL omitidas por falta de TEST_DATABASE_URL. Un aviso de Starlette sobre HTTPX.
- `python -m pip check`: sin dependencias incompatibles.
- `python -m alembic upgrade head --sql`: SQL revisado; users con UUID, correo único, roles, checks y auditoría.
- `python -m alembic downgrade 0001_create_users:base --sql`: SQL de reversión generado; no se ejecutó sobre datos.
- SQLAlchemy y Psycopg pueden crear el motor de conexión; esto no demuestra conexión real.

## Pendiente para aceptar la historia

PostgreSQL no está disponible: Docker devuelve error 500 y WSL no puede iniciar. El firmware sí tiene virtualización y Windows tiene RebootPending=true. Se requiere reiniciar Windows y arrancar Docker, aplicar la migración y ejecutar scripts/test_postgres.py y PI-01 de ReForest_App.

Las pruebas aisladas comprueban upgrade/downgrade, persistencia, los tres roles públicos, hash, duplicado y restricciones. PI-01 usa Angular y API reales; no usa respuestas simuladas.

HU05 no se considera aceptada mientras esas verificaciones estén pendientes. La publicación en GitHub no implica la aceptación de HU05; PostgreSQL y PI-01 siguen pendientes.

## Angular y navegador

- Compilación de producción Angular: aprobada (229.02 kB iniciales; ruta de registro con carga diferida).
- Angular/Vitest: 11 pruebas aprobadas.
- Playwright/Chromium, pruebas de interfaz: 2 aprobadas. Validaciones, roles, diseño móvil sin desbordamiento y mensaje de fallo de conexión.
- Esta prueba de interfaz aborta la solicitud de registro para verificar el fallo de red y no demuestra registro real. PI-01 sigue pendiente.

Las verificaciones de Angular requirieron permisos fuera del sandbox por restricciones de lectura del compilador. Node.js portátil 24.19.0 se descargó del sitio oficial y se verificó con SHA256.


## Diagnóstico de la integración

La solicitud de Angular llega a FastAPI, pero PostgreSQL no acepta conexiones. El registro producía OperationalError por tiempo de espera y una respuesta interna sin mensaje útil. Se agregó un límite de conexión de cinco segundos por intento y respuesta segura 503 con CORS. El formulario explica la indisponibilidad temporal y permite reintentar.

Verificación después del cambio: 12 pruebas de API aprobadas, 15 PostgreSQL pendientes; 12 pruebas Angular aprobadas. POST real /api/v1/auth/register comprobado: 503, código REGISTRATION_UNAVAILABLE y Access-Control-Allow-Origin=http://127.0.0.1:4200. Esto demuestra conexión HTTP con la API, pero no demuestra persistencia.

Docker informó WSL update required, aunque la versión instalada es 2.7.13; el registro muestra que su comprobación de versión falló por tiempo de espera y acceso denegado. Se reiniciaron los procesos de Docker sin eliminar volúmenes. La aceptación de HU05 sigue pendiente de PostgreSQL y PI-01.
