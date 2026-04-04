import json
import pytest
from unittest.mock import MagicMock, patch
from app.services import cache_service


@pytest.fixture
def mock_redis():
    """Мок Redis-клиента."""
    with patch("app.services.cache_service.get_redis") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


@pytest.fixture
def no_redis():
    """Redis недоступен — get_redis возвращает None."""
    with patch("app.services.cache_service.get_redis") as mock_get:
        mock_get.return_value = None
        yield


class TestCacheKeys:
    """Тесты генерации ключей кеша"""

    def test_make_graph_key(self):
        """Ключ графа содержит district."""
        key = cache_service.make_graph_key("tverskoy")
        assert key == "graph:tverskoy"

    def test_make_analysis_key_contains_district(self):
        """Ключ анализа содержит district."""
        changes = {"district": "tverskoy", "removed_nodes": [], "removed_edges": [],
                   "added_nodes": [], "added_edges": []}
        key = cache_service.make_analysis_key(changes)
        assert key.startswith("analysis:tverskoy:")

    def test_make_cascade_key_contains_district(self):
        """Ключ каскада содержит district."""
        req = {"district": "tverskoy", "steps": 5, "removed_nodes": [],
               "removed_edges": [], "added_nodes": [], "added_edges": []}
        key = cache_service.make_cascade_key(req)
        assert key.startswith("cascade:tverskoy:")

    def test_analysis_key_same_input_same_key(self):
        """Одинаковые изменения → одинаковый ключ."""
        changes = {"district": "tverskoy", "removed_nodes": ["a"], "removed_edges": [],
                   "added_nodes": [], "added_edges": []}
        assert cache_service.make_analysis_key(changes) == cache_service.make_analysis_key(changes)

    def test_analysis_key_different_input_different_key(self):
        """Разные изменения → разные ключи."""
        c1 = {"district": "tverskoy", "removed_nodes": ["a"], "removed_edges": [],
              "added_nodes": [], "added_edges": []}
        c2 = {"district": "tverskoy", "removed_nodes": ["b"], "removed_edges": [],
              "added_nodes": [], "added_edges": []}
        assert cache_service.make_analysis_key(c1) != cache_service.make_analysis_key(c2)

    def test_analysis_key_order_insensitive(self):
        """Порядок ключей в словаре не влияет на ключ кеша."""
        c1 = {"district": "tverskoy", "removed_nodes": ["a", "b"], "removed_edges": [],
              "added_nodes": [], "added_edges": []}
        c2 = {"removed_nodes": ["a", "b"], "district": "tverskoy", "removed_edges": [],
              "added_edges": [], "added_nodes": []}
        assert cache_service.make_analysis_key(c1) == cache_service.make_analysis_key(c2)


class TestCacheGet:
    """Тесты метода get"""

    def test_get_returns_none_on_miss(self, mock_redis):
        """Cache miss → None."""
        mock_redis.get.return_value = None
        assert cache_service.get("missing_key") is None

    def test_get_returns_deserialized_value(self, mock_redis):
        """Cache hit → десериализованный объект."""
        mock_redis.get.return_value = json.dumps({"resilience": 0.85})
        result = cache_service.get("some_key")
        assert result == {"resilience": 0.85}

    def test_get_returns_none_when_redis_unavailable(self, no_redis):
        """Redis недоступен → None без исключения."""
        assert cache_service.get("any_key") is None

    def test_get_returns_none_on_redis_error(self, mock_redis):
        """Ошибка Redis → None без исключения."""
        mock_redis.get.side_effect = Exception("connection lost")
        assert cache_service.get("any_key") is None

    def test_get_calls_redis_with_correct_key(self, mock_redis):
        """get вызывает Redis с переданным ключом."""
        mock_redis.get.return_value = None
        cache_service.get("graph:tverskoy")
        mock_redis.get.assert_called_once_with("graph:tverskoy")


class TestCacheSet:
    """Тесты метода set"""

    def test_set_calls_setex(self, mock_redis):
        """set вызывает Redis setex с ключом, TTL и сериализованным значением."""
        cache_service.set("graph:tverskoy", {"nodes": []}, 3600)
        mock_redis.setex.assert_called_once_with(
            "graph:tverskoy",
            3600,
            json.dumps({"nodes": []}, default=str)
        )

    def test_set_does_nothing_when_redis_unavailable(self, no_redis):
        """Redis недоступен → set не падает."""
        cache_service.set("key", {"data": 1}, 300)  # не должно вызывать исключение

    def test_set_does_nothing_on_redis_error(self, mock_redis):
        """Ошибка Redis при записи → не падает."""
        mock_redis.setex.side_effect = Exception("write error")
        cache_service.set("key", {"data": 1}, 300)  # не должно вызывать исключение

    def test_set_serializes_value(self, mock_redis):
        """Значение сериализуется в JSON перед записью."""
        value = {"calculation_time_ms": 1234.5, "metrics": {"betweenness": {}}}
        cache_service.set("analysis:tverskoy:abc", value, 300)
        call_args = mock_redis.setex.call_args
        stored = json.loads(call_args[0][2])
        assert stored == value


class TestCacheGetSet:
    """Интеграционные тесты get + set через мок"""

    def test_set_then_get_returns_same_value(self, mock_redis):
        """После set → get возвращает то же значение."""
        value = {"resilience_score": 0.78, "steps": []}
        serialized = json.dumps(value, default=str)

        mock_redis.setex.return_value = True
        mock_redis.get.return_value = serialized

        cache_service.set("cascade:tverskoy:xyz", value, 300)
        result = cache_service.get("cascade:tverskoy:xyz")

        assert result == value
