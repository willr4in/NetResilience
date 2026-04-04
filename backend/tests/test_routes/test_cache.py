import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.services import cache_service
from app.services.graph_service import load_graph
import app.cache as cache_module


@pytest.fixture(scope="function")
def client_with_redis(redis_setup, db_session):
    """Client с реальным Redis из testcontainers."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestGraphCacheIntegration:
    """Интеграционные тесты кеширования графовых эндпоинтов"""

    def test_graph_cached_on_second_request(self, client_with_redis):
        """
        Второй запрос GET /graph/{district} возвращает данные из кеша.
        Структура ответа идентична первому запросу.
        """
        r1 = client_with_redis.get("/api/graph/tverskoy")
        assert r1.status_code == 200

        r2 = client_with_redis.get("/api/graph/tverskoy")
        assert r2.status_code == 200

        assert r1.json()["metadata"] == r2.json()["metadata"]
        assert len(r1.json()["nodes"]) == len(r2.json()["nodes"])

    def test_calculate_cached_on_second_request(self, client_with_redis):
        """
        После первого запроса ключ появляется в Redis.
        Второй запрос возвращает calculation_time_ms < 100 мс (из кеша).
        """
        changes = {
            "district": "tverskoy",
            "removed_nodes": [], "removed_edges": [],
            "added_nodes": [], "added_edges": []
        }

        r1 = client_with_redis.post("/api/graph/calculate", json=changes)
        assert r1.status_code == 200

        # Убеждаемся что ключ появился в Redis
        key = cache_service.make_analysis_key(changes)
        assert cache_module._client.exists(key) == 1

        r2 = client_with_redis.post("/api/graph/calculate", json=changes)
        assert r2.status_code == 200
        assert r2.json()["calculation_time_ms"] < 100

    def test_calculate_cache_hit_returns_same_metrics(self, client_with_redis):
        """
        Метрики при cache hit идентичны оригинальному расчёту.
        """
        changes = {
            "district": "tverskoy",
            "removed_nodes": [], "removed_edges": [],
            "added_nodes": [], "added_edges": []
        }

        r1 = client_with_redis.post("/api/graph/calculate", json=changes)
        r2 = client_with_redis.post("/api/graph/calculate", json=changes)

        assert r1.json()["metrics"]["critical_nodes"] == r2.json()["metrics"]["critical_nodes"]
        assert r1.json()["resilience"] == r2.json()["resilience"]

    def test_different_changes_different_cache_keys(self, client_with_redis):
        """
        Разные наборы изменений кешируются независимо.
        """
        _, G = load_graph("tverskoy")
        nodes = list(G.nodes())

        changes_a = {
            "district": "tverskoy",
            "removed_nodes": [nodes[0]],
            "removed_edges": [], "added_nodes": [], "added_edges": []
        }
        changes_b = {
            "district": "tverskoy",
            "removed_nodes": [nodes[1]],
            "removed_edges": [], "added_nodes": [], "added_edges": []
        }

        r_a = client_with_redis.post("/api/graph/calculate", json=changes_a)
        r_b = client_with_redis.post("/api/graph/calculate", json=changes_b)

        assert r_a.status_code == 200
        assert r_b.status_code == 200
        assert r_a.json()["metrics"]["betweenness"] != r_b.json()["metrics"]["betweenness"]

    def test_cascade_cached_on_second_request(self, client_with_redis):
        """
        После первого запроса ключ появляется в Redis.
        Второй запрос возвращает calculation_time_ms < 100 мс (из кеша).
        """
        req = {
            "district": "tverskoy",
            "steps": 5,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }

        r1 = client_with_redis.post("/api/graph/simulate-cascade", json=req)
        assert r1.status_code == 200

        # Убеждаемся что ключ появился в Redis
        key = cache_service.make_cascade_key(req)
        assert cache_module._client.exists(key) == 1

        r2 = client_with_redis.post("/api/graph/simulate-cascade", json=req)
        assert r2.status_code == 200
        assert r2.json()["calculation_time_ms"] < 100

    def test_cascade_cache_hit_returns_same_steps(self, client_with_redis):
        """
        Шаги каскада при cache hit идентичны оригинальному расчёту.
        """
        req = {
            "district": "tverskoy",
            "steps": 3,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }

        r1 = client_with_redis.post("/api/graph/simulate-cascade", json=req)
        r2 = client_with_redis.post("/api/graph/simulate-cascade", json=req)

        steps1 = [(s["step"], s["removed_node_id"]) for s in r1.json()["steps"]]
        steps2 = [(s["step"], s["removed_node_id"]) for s in r2.json()["steps"]]
        assert steps1 == steps2

    def test_cache_works_without_redis(self, db_session):
        """
        При недоступном Redis приложение работает нормально (graceful fallback).
        """
        cache_module._client = None
        original_url = cache_module.settings.REDIS_URL
        cache_module.settings.REDIS_URL = "redis://localhost:19999/0"  # несуществующий порт

        def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as client:
            response = client.post("/api/graph/calculate", json={
                "district": "tverskoy",
                "removed_nodes": [], "removed_edges": [],
                "added_nodes": [], "added_edges": []
            })
            assert response.status_code == 200

        cache_module._client = None
        cache_module.settings.REDIS_URL = original_url
        app.dependency_overrides.clear()
