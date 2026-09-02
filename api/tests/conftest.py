import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-longer-than-thirty-two-characters")
os.environ.setdefault("DATABASE_URL", "sqlite:///./unused.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.directory import Facility, Provider


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        execution_options={"schema_translate_map": {"security": None, "clinical": None}},
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def directory_data(db_session: Session) -> None:
    facility = Facility(
        facility_name="ZambeCare Dallas Clinic",
        facility_type="CLINIC",
        address_line_1="100 Synthetic Health Way",
        city="Dallas",
        state_code="TX",
        postal_code="75201",
    )
    db_session.add(facility)
    db_session.flush()
    db_session.add(
        Provider(
            facility_id=facility.facility_id,
            npi="0000000001",
            first_name="Amara",
            last_name="Testdoctor",
            specialty_code="PRIMARY_CARE",
            is_accepting_patients=True,
        )
    )
    db_session.commit()
