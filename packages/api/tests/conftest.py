"""Run API tests in disposable PostgreSQL schemas, never application tables."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("Set TEST_DATABASE_URL to a disposable PostgreSQL/pgvector test database.")
if make_url(TEST_DATABASE_URL).get_backend_name() != "postgresql":
    raise RuntimeError("TEST_DATABASE_URL must use PostgreSQL; these models require JSONB and pgvector.")

# Settings are initialized during application import. Always use the test database
# and disable optional providers, including values inherited from a local .env.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "votepack_local_test_secret_at_least_32_chars"
for provider in (
    "GEMINI_API_KEY", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET",
    "BREVO_API_KEY", "REDIS_URL", "SENTRY_DSN",
):
    os.environ[provider] = ""

from .. import auth, database  # noqa: E402
from ..dependencies import get_db  # noqa: E402
from ..main import app  # noqa: E402
from ..models import Base, User  # noqa: E402


@pytest.fixture
def db_session(monkeypatch):
    schema = f"votepack_test_{uuid.uuid4().hex}"
    admin_engine = create_engine(TEST_DATABASE_URL)
    with admin_engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"options": f"-csearch_path={schema},public"},
        # Qualify ORM tables and enum DDL explicitly. search_path alone lets
        # create_all(checkfirst=True) reuse an existing public table. Keep
        # public in the path only so PostgreSQL can resolve pgvector's type.
        execution_options={"schema_translate_map": {None: schema}},
    )
    monkeypatch.setattr(database, "engine", engine)
    try:
        Base.metadata.create_all(bind=engine)
        with sessionmaker(bind=engine, autocommit=False, autoflush=False)() as session:
            yield session
    finally:
        engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin_engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password=auth.get_password_hash("testpassword123"),
        name="Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = auth.create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
