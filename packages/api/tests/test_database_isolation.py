"""Prove the API fixtures cannot reuse tables outside their own schema."""

import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from ..models import User
from . import conftest


@pytest.fixture
def database_with_public_user(monkeypatch):
    # All public-schema objects below belong to a database created only for this
    # regression. Never plant a sentinel in the configured test database.
    database_name = f"votepack_isolation_{uuid.uuid4().hex}"
    admin_engine = create_engine(conftest.TEST_DATABASE_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    test_url = make_url(conftest.TEST_DATABASE_URL).set(database=database_name)
    public_engine = create_engine(test_url)
    try:
        User.__table__.create(bind=public_engine)
        with public_engine.begin() as connection:
            connection.execute(User.__table__.insert().values(
                email="public-sentinel@example.com",
                hashed_password="test-only-sentinel",
                name="Untouched public user",
            ))
        monkeypatch.setattr(conftest, "TEST_DATABASE_URL", test_url)
        yield public_engine
    finally:
        public_engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(text(f'DROP DATABASE "{database_name}" WITH (FORCE)'))
        admin_engine.dispose()


def test_api_fixture_preserves_existing_public_tables(database_with_public_user, request):
    session = request.getfixturevalue("db_session")
    schema = session.execute(text("SELECT current_schema()")).scalar_one()
    # Force application lifespan to recreate this table too. Its engine must
    # carry the same schema mapping as the fixture's session engine.
    session.execute(text(f'DROP TABLE IF EXISTS "{schema}".users'))
    session.commit()

    client = request.getfixturevalue("client")
    response = client.post("/api/v1/auth/register", json={
        "email": "isolated-user@example.com",
        "password": "isolated-password-123",
        "name": "Isolated User",
    })
    assert response.status_code == 201

    with database_with_public_user.connect() as connection:
        public_users = connection.execute(text(
            "SELECT email, name FROM public.users ORDER BY email"
        )).all()
        public_tables = connection.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )).scalars().all()
    assert public_users == [("public-sentinel@example.com", "Untouched public user")]
    assert public_tables == ["users"]
    assert session.execute(text(f'SELECT email FROM "{schema}".users')).scalars().all() == [
        "isolated-user@example.com"
    ]
