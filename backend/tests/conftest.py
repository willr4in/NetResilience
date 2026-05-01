# tests/conftest.py
import json
import os
import uuid
from pathlib import Path

import pytest
import redis as redis_lib
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.main import app
from app.database import Base, get_db
import app.cache as cache_module


_DATA_DIR = Path(__file__).parent.parent / "app" / "data" / "districts"


def _make_synthetic_graph() -> dict:
    """4×4 grid graph near Tverskoy district for testing."""
    lats = [55.770, 55.772, 55.774, 55.776]
    lons = [37.600, 37.604, 37.608, 37.612]
    h_weight = round(0.004 * 62.4, 3)  # ~0.250 km per lon step at 55.77°N
    v_weight = round(0.002 * 111.0, 3)  # ~0.222 km per lat step

    nodes = []
    for r, lat in enumerate(lats):
        for c, lon in enumerate(lons):
            nodes.append({"id": f"n{r}{c}", "label": f"Node {r}{c}", "lat": lat, "lon": lon})

    edges = []
    for r in range(4):
        for c in range(3):
            edges.append({"source": f"n{r}{c}", "target": f"n{r}{c+1}", "weight": h_weight})
    for r in range(3):
        for c in range(4):
            edges.append({"source": f"n{r}{c}", "target": f"n{r+1}{c}", "weight": v_weight})

    return {
        "metadata": {"name": "Tverskoy", "city": "Moscow", "district": "tverskoy"},
        "nodes": nodes,
        "edges": edges,
    }


@pytest.fixture(scope="session", autouse=True)
def synthetic_graph_data():
    """Creates a minimal synthetic tverskoy.json if the real file is absent."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    target = _DATA_DIR / "tverskoy.json"
    created = not target.exists()
    if created:
        target.write_text(json.dumps(_make_synthetic_graph()))
    yield
    if created:
        target.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(scope="function")
def redis_setup(redis_container):
    """Подключает тестовый Redis (testcontainers) через синглтон кеша."""
    client = redis_lib.Redis(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        decode_responses=True,
    )
    client.flushall()
    cache_module._client = client
    yield
    cache_module._client = None


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_user(db_session):
    from app.services.auth_service import AuthService
    from app.schemas.auth import RegisterRequest

    auth_service = AuthService(db_session)
    user = auth_service.register(RegisterRequest(
        name="Test",
        surname="User",
        email="test@test.com",
        password="password123"
    ))
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_user_2(db_session):
    from app.services.auth_service import AuthService
    from app.schemas.auth import RegisterRequest

    auth_service = AuthService(db_session)
    user = auth_service.register(RegisterRequest(
        name="Test2",
        surname="User2",
        email=f"test2_{uuid.uuid4().hex[:8]}@test.com",
        password="password123"
    ))
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def client(db_session, redis_setup):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def access_token(db_session, test_user):
    from app.services.auth_service import AuthService

    auth_service = AuthService(db_session)
    return auth_service.create_access_token(test_user.id)


@pytest.fixture(scope="function")
def access_token_user_2(db_session, test_user_2):
    from app.services.auth_service import AuthService

    auth_service = AuthService(db_session)
    return auth_service.create_access_token(test_user_2.id)


@pytest.fixture(scope="function")
def client_with_auth(db_session, test_user, redis_setup):
    from app.services.auth_service import AuthService

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    auth_service = AuthService(db_session)
    access_token = auth_service.create_access_token(test_user.id)

    with TestClient(app) as test_client:
        test_client.cookies.set("access_token", access_token)
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_with_auth_user_2(db_session, test_user_2, redis_setup):
    from app.services.auth_service import AuthService

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    auth_service = AuthService(db_session)
    access_token = auth_service.create_access_token(test_user_2.id)

    with TestClient(app) as test_client:
        test_client.cookies.set("access_token", access_token)
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_scenario(db_session, test_user):
    from app.models.scenario import Scenario

    scenario = Scenario(
        user_id=test_user.id,
        name="Test Scenario",
        description="Test Description",
        district="tverskoy",
        removed_nodes=[],
        removed_edges=[],
        added_nodes=[],
        added_edges=[],
        hits=0
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)
    return scenario
