# ReForest_Api

API de ReForest. La infraestructura local usa PostgreSQL 17 con Docker Compose.

## Requisitos

Windows con Docker Desktop iniciado y el motor WSL 2 habilitado. La instalación de WSL puede requerir reiniciar Windows.

## Configuración local

Desde esta carpeta, copia `.env.example` a `.env` si no existe y sustituye la contraseña de ejemplo. Actualiza también la contraseña en `DATABASE_URL`. El archivo `.env` es privado y está excluido de Git.

Durante la preparación inicial se generó un `.env` local con una contraseña aleatoria; no es necesario sustituirlo para iniciar esta base.

## PostgreSQL

```powershell
docker compose up -d --wait
docker compose ps
docker compose exec db sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();"'
```

La base `reforest` está disponible en `localhost:5432`. Sus datos persisten en el volumen `postgres_data`. El puerto se expone únicamente en el equipo local.

```powershell
docker compose logs db
docker compose stop
docker compose down
```

No uses `docker compose down -v` durante el trabajo normal: elimina el volumen y sus datos.

La API ofrece GET /health y POST /api/v1/auth/register. La tabla users se crea mediante Alembic; no se crean tablas automáticamente al iniciar.

## API local (HU05-T01-API)

Requiere Python 3.12 o superior. Ejecuta los comandos desde ReForest_Api:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Estos comandos usan el intérprete del entorno directamente, sin activar scripts de PowerShell. Para usar Python 3.12 instalado en su ruta habitual, puedes sustituir el primer comando por:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
```

- GET http://127.0.0.1:8000/health devuelve 200 y `{"status":"ok"}` sin autenticación.
- Swagger: http://127.0.0.1:8000/docs.
- Contrato OpenAPI: http://127.0.0.1:8000/openapi.json.

/health comprueba que la API responde; no verifica PostgreSQL. En esta tarea la API no carga .env ni crea tablas. El registro de usuarios se implementará en tareas posteriores de HU05.

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pip check
```

Estructura inicial: app/main.py contiene la aplicación y el contrato de salud; tests/test_health.py comprueba su respuesta HTTP. requirements.txt define dependencias de ejecución y requirements-dev.txt añade herramientas de prueba.


## Registro de usuarios (HU05)

Después de instalar requirements-dev.txt y configurar .env:

```powershell
docker compose up -d --wait
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

La configuración usa DATABASE_URL del .env (nunca se imprime ni se versiona). CORS local permite Angular en localhost:4200 y 127.0.0.1:4200. Puedes establecer CORS_ORIGINS como lista JSON. Consulta docs/contrato-registro.md para entradas y respuestas 201/409/422.

La migración 0001_create_users implementa el modelo y restricciones del diccionario. Para revisar el SQL sin aplicarlo:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head --sql
```

## Pruebas PostgreSQL

Establece TEST_DATABASE_URL apuntando a una base PostgreSQL de pruebas con permiso para crear esquemas. No muestres su valor. Las fixtures generan un esquema hu05_test_<uuid>, ejecutan upgrade/downgrade/upgrade y eliminan únicamente ese esquema al finalizar. No modifican las tablas de public. Si TEST_DATABASE_URL falta, las pruebas PostgreSQL se omiten explícitamente.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
```

La suite verifica registro por los tres roles, hash y persistencia, correo duplicado, validaciones, rol ADMINISTRADOR prohibido, restricciones de base y CORS. PI-01 con navegador está en ReForest_App/e2e y requiere ambos servidores y PostgreSQL.

Si el Control de aplicaciones de Windows bloquea las extensiones nativas de SQLAlchemy, su distribución oficial admite instalación Python pura:

```powershell
$env:DISABLE_SQLALCHEMY_CEXT = '1'
.\.venv\Scripts\python.exe -m pip install --force-reinstall --no-deps --no-binary sqlalchemy sqlalchemy==2.1.1
```

Si WSL informa que la virtualización no está habilitada, verifica VirtualMachinePlatform y la virtualización del firmware y reinicia Windows antes de arrancar Docker. La app puede compilarse sin PostgreSQL, pero la historia no está validada de extremo a extremo hasta completar PI-01.


Para probar en un esquema temporal dentro del PostgreSQL local configurado en .env, sin copiar la URL ni revelar credenciales:

```powershell
.\.venv\Scripts\python.exe scripts/test_postgres.py
```

requirements-lock.txt fija también dependencias transitivas de la instalación comprobada en Python 3.12/Windows.
