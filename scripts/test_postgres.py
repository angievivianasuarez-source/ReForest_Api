"""Ejecuta pruebas en un esquema temporal del PostgreSQL configurado."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.core.config import get_settings

if __name__ == "__main__":
    environment = {**os.environ, "TEST_DATABASE_URL": get_settings().database_url.get_secret_value()}
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, env=environment))
