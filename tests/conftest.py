import os
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="module")
def postgres_engine():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Configura TEST_DATABASE_URL para pruebas PostgreSQL aisladas")
    schema = "hu05_test_" + uuid4().hex
    admin = create_engine(url)
    with admin.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema} -ctimezone=UTC"})
    try:
        config = Config("alembic.ini")
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
            command.downgrade(config, "base")
            assert connection.execute(text("SELECT to_regclass('users')")).scalar() is None
            command.upgrade(config, "head")
        yield engine
    finally:
        engine.dispose()
        # El esquema es generado por esta fixture, nunca procede de entrada externa.
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


@pytest.fixture
def db(postgres_engine):
    with postgres_engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session
        transaction.rollback()


@pytest.fixture
def client(db):
    def override_db():
        yield db
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
