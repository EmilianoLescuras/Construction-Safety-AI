"""Shared test fixtures.

We swap the backend's engine for an in-memory SQLite (per-test) and override
the FastAPI ``get_db`` dependency to point at it. This keeps tests fast and
hermetic — no shared filesystem state between tests.
"""
from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.backend.app import app
from src.backend.db import Base, get_db


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Fresh in-memory SQLite per test, schema created from ORM metadata."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """FastAPI TestClient with get_db pointed at the test session."""
    def _override() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = _override
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)
