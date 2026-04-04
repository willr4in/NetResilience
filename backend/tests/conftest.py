# tests/conftest.py
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.main import app
from app.database import Base, get_db
import app.cache as cache_module


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
    """Подключает тестовый Redis напрямую через синглтон."""
    cache_module._client = redis_container.get_client(decode_responses=True)
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
    """Второй тестовый пользователь"""
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
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def access_token(db_session, test_user):
    """Создаёт access token для test_user"""
    from app.services.auth_service import AuthService
    
    auth_service = AuthService(db_session)
    token = auth_service.create_access_token(test_user.id)
    return token


@pytest.fixture(scope="function")
def access_token_user_2(db_session, test_user_2):
    """Создаёт access token для test_user_2"""
    from app.services.auth_service import AuthService
    
    auth_service = AuthService(db_session)
    token = auth_service.create_access_token(test_user_2.id)
    return token


@pytest.fixture(scope="function")
def client_with_auth(db_session, test_user):
    """Client with authenticated test_user"""
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
def client_with_auth_user_2(db_session, test_user_2):
    """Client with authenticated test_user_2"""
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

