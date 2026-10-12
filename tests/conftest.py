import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User, RevokedToken

@pytest.fixture
def client():
    test_database_url = os.getenv("TEST_DATABASE_URL")

    if not test_database_url:
        pytest.fail("A variável de ambiente 'TEST_DATABASE_URL' não está definida.")

    test_engine = create_engine(test_database_url)

    TestingSessionLocal = sessionmaker(
        bind = test_engine,
        autoflush = False,
        autocommit = False
    )

    Base.metadata.create_all(bind = test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind = test_engine)
    test_engine.dispose()