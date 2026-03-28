import pytest
import networkx as nx
from app.algorithms.resilience import (
    is_connected,
    largest_component_ratio,
    average_shortest_path,
    betweenness_concentration,
    top_nodes_change,
    calculate_resilience
)


@pytest.fixture
def connected_graph():
    """
    Фикстура, создающая связный линейный граф.
    
    Структура: A — B — C — D.
    
    Returns:
        nx.Graph: Связный граф из четырех узлов.
    """
    G = nx.Graph()
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "C", weight=1.0)
    G.add_edge("C", "D", weight=1.0)
    return G


@pytest.fixture
def disconnected_graph():
    """
    Фикстура, создающая несвязный граф с двумя компонентами.
    
    Структура: A — B и C — D (два изолированных ребра).
    
    Returns:
        nx.Graph: Несвязный граф из четырех узлов.
    """
    G = nx.Graph()
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("C", "D", weight=1.0)
    return G


@pytest.fixture
def empty_graph():
    """
    Фикстура, создающая пустой граф.
    
    Returns:
        nx.Graph: Граф без узлов и ребер.
    """
    return nx.Graph()


@pytest.fixture
def single_node_graph():
    """
    Фикстура, создающая граф с одним узлом.
    
    Returns:
        nx.Graph: Граф с одним изолированным узлом.
    """
    G = nx.Graph()
    G.add_node("A")
    return G


class TestIsConnected:
    """Тесты для функции проверки связности графа"""
    
    def test_connected_graph(self, connected_graph):
        """
        Тест связного графа.
        
        Проверяет, что функция возвращает True
        для связного графа.
        """
        assert is_connected(connected_graph) is True

    def test_disconnected_graph(self, disconnected_graph):
        """
        Тест несвязного графа.
        
        Проверяет, что функция возвращает False
        для несвязного графа.
        """
        assert is_connected(disconnected_graph) is False

    def test_single_node(self, single_node_graph):
        """
        Тест графа с одним узлом.
        
        Проверяет, что граф с одним узлом
        считается связным.
        """
        assert is_connected(single_node_graph) is True


class TestLargestComponentRatio:
    """Тесты для функции расчета доли крупнейшего компонента"""
    
    def test_connected_graph_returns_one(self, connected_graph):
        """
        Тест связного графа.
        
        Проверяет, что для связного графа
        доля крупнейшего компонента равна 1.
        """
        assert largest_component_ratio(connected_graph) == 1.0

    def test_disconnected_equal_components(self, disconnected_graph):
        """
        Тест несвязного графа с равными компонентами.
        
        Проверяет, что для графа с двумя компонентами
        по 2 узла каждый доля составляет 0.5.
        """
        result = largest_component_ratio(disconnected_graph)
        assert result == 0.5

    def test_empty_graph_returns_zero(self, empty_graph):
        """
        Тест пустого графа.
        
        Проверяет, что для пустого графа
        доля крупнейшего компонента равна 0.
        """
        assert largest_component_ratio(empty_graph) == 0.0

    def test_single_node_returns_one(self, single_node_graph):
        """
        Тест графа с одним узлом.
        
        Проверяет, что для графа с одним узлом
        доля крупнейшего компонента равна 1.
        """
        assert largest_component_ratio(single_node_graph) == 1.0

    def test_range_zero_to_one(self, disconnected_graph):
        """
        Тест диапазона значений.
        
        Проверяет, что результат находится
        в диапазоне от 0 до 1.
        """
        result = largest_component_ratio(disconnected_graph)
        assert 0.0 <= result <= 1.0


class TestAverageShortestPath:
    """Тесты для функции расчета средней длины кратчайшего пути"""
    
    def test_connected_graph_returns_float(self, connected_graph):
        """
        Тест связного графа.
        
        Проверяет, что для связного графа
        возвращается положительное число.
        """
        result = average_shortest_path(connected_graph)
        assert isinstance(result, float)
        assert result > 0

    def test_disconnected_graph_uses_largest_component(self, disconnected_graph):
        """
        Тест несвязного графа.
        
        Проверяет, что для несвязного графа
        расчет выполняется по крупнейшему компоненту.
        """
        result = average_shortest_path(disconnected_graph)
        assert result is not None
        assert result > 0

    def test_empty_graph_returns_none(self, empty_graph):
        """
        Тест пустого графа.
        
        Проверяет, что для пустого графа
        возвращается None.
        """
        assert average_shortest_path(empty_graph) is None

    def test_single_edge_graph(self):
        """
        Тест графа с одним ребром.
        
        Проверяет, что средняя длина пути
        для графа из двух узлов равна 1.
        """
        G = nx.Graph()
        G.add_edge("A", "B", weight=1.0)
        result = average_shortest_path(G)
        assert result == 1.0


class TestBetweennessConcentration:
    """Тесты для функции расчета концентрации медианной центральности"""
    
    def test_uniform_distribution_low_concentration(self):
        """
        Тест равномерного распределения.
        
        Проверяет, что для равномерного распределения
        концентрация равна 0.
        """
        metrics = {"A": 0.5, "B": 0.5, "C": 0.5}
        result = betweenness_concentration(metrics)
        assert result == 0.0

    def test_concentrated_distribution_high(self):
        """
        Тест концентрированного распределения.
        
        Проверяет, что для сильно концентрированного
        распределения концентрация выше 0.5.
        """
        metrics = {"A": 1.0, "B": 0.0, "C": 0.0}
        result = betweenness_concentration(metrics)
        assert result > 0.5

    def test_empty_metrics_returns_zero(self):
        """
        Тест пустого словаря метрик.
        
        Проверяет, что для пустого словаря
        возвращается 0.
        """
        assert betweenness_concentration({}) == 0.0

    def test_all_zeros_returns_zero(self):
        """
        Тест нулевых значений.
        
        Проверяет, что для всех нулевых метрик
        возвращается 0.
        """
        metrics = {"A": 0.0, "B": 0.0, "C": 0.0}
        assert betweenness_concentration(metrics) == 0.0

    def test_result_in_range(self):
        """
        Тест диапазона значений.
        
        Проверяет, что результат находится
        в диапазоне от 0 до 1.
        """
        metrics = {"A": 0.3, "B": 0.5, "C": 0.2}
        result = betweenness_concentration(metrics)
        assert 0.0 <= result <= 1.0


class TestTopNodesChange:
    """Тесты для функции определения изменений в списке критических узлов"""
    
    def test_no_change(self):
        """
        Тест отсутствия изменений.
        
        Проверяет, что при одинаковых метриках
        списки новых и утраченных узлов пусты.
        """
        metrics = {"A": 0.5, "B": 0.3, "C": 0.1}
        result = top_nodes_change(metrics, metrics, n=2)
        assert result["new_critical"] == []
        assert result["no_longer_critical"] == []

    def test_complete_change(self):
        """
        Тест полного изменения.
        
        Проверяет, что при перестановке значений
        списки изменений корректно определяются.
        """
        before = {"A": 0.9, "B": 0.1}
        after = {"A": 0.1, "B": 0.9}
        result = top_nodes_change(before, after, n=1)
        assert "B" in result["new_critical"]
        assert "A" in result["no_longer_critical"]

    def test_returns_required_keys(self):
        """
        Тест наличия всех ключей в результате.
        
        Проверяет, что возвращаемый словарь
        содержит все необходимые поля.
        """
        metrics = {"A": 0.5, "B": 0.3}
        result = top_nodes_change(metrics, metrics)
        assert "top_before" in result
        assert "top_after" in result
        assert "new_critical" in result
        assert "no_longer_critical" in result


class TestCalculateResilience:
    """Тесты для функции расчета общей устойчивости графа"""
    
    def test_connected_graph_high_score(self, connected_graph):
        """
        Тест оценки устойчивости связного графа.
        
        Проверяет, что связный граф получает
        высокий балл устойчивости (>0.5).
        """
        from app.algorithms.centrality import calculate_all
        metrics = calculate_all(connected_graph)
        result = calculate_resilience(connected_graph, metrics)
        assert result["resilience_score"] > 0.5

    def test_disconnected_graph_lower_score(self, disconnected_graph, connected_graph):
        """
        Тест сравнения устойчивости связного и несвязного графов.
        
        Проверяет, что связный граф имеет более высокий
        балл устойчивости, чем несвязный.
        """
        from app.algorithms.centrality import calculate_all
        metrics_connected = calculate_all(connected_graph)
        metrics_disconnected = calculate_all(disconnected_graph)
        score_connected = calculate_resilience(connected_graph, metrics_connected)["resilience_score"]
        score_disconnected = calculate_resilience(disconnected_graph, metrics_disconnected)["resilience_score"]
        assert score_connected > score_disconnected

    def test_returns_required_fields(self, connected_graph):
        """
        Тест наличия всех полей в результате.
        
        Проверяет, что возвращаемый словарь
        содержит все необходимые метрики устойчивости.
        """
        from app.algorithms.centrality import calculate_all
        metrics = calculate_all(connected_graph)
        result = calculate_resilience(connected_graph, metrics)
        assert "connected" in result
        assert "largest_component_ratio" in result
        assert "average_shortest_path" in result
        assert "betweenness_concentration" in result
        assert "resilience_score" in result
        assert "comparison" in result

    def test_no_comparison_without_original(self, connected_graph):
        """
        Тест отсутствия сравнения без исходного графа.
        
        Проверяет, что при отсутствии исходного графа
        поле сравнения равно None.
        """
        from app.algorithms.centrality import calculate_all
        metrics = calculate_all(connected_graph)
        result = calculate_resilience(connected_graph, metrics)
        assert result["comparison"] is None

    def test_comparison_when_original_provided(self, connected_graph):
        """
        Тест наличия сравнения с исходным графом.
        
        Проверяет, что при передаче исходного графа
        в результате появляется информация о сравнении.
        """
        from app.algorithms.centrality import calculate_all
        G_modified = connected_graph.copy()
        G_modified.remove_node("D")
        metrics_original = calculate_all(connected_graph)
        metrics_modified = calculate_all(G_modified)
        result = calculate_resilience(
            G_modified, metrics_modified,
            G_original=connected_graph,
            metrics_original=metrics_original
        )
        assert result["comparison"] is not None
        assert "resilience_delta" in result["comparison"]

    def test_score_range(self, connected_graph):
        """
        Тест диапазона балла устойчивости.
        
        Проверяет, что балл устойчивости находится
        в диапазоне от 0 до 1.
        """
        from app.algorithms.centrality import calculate_all
        metrics = calculate_all(connected_graph)
        result = calculate_resilience(connected_graph, metrics)
        assert 0.0 <= result["resilience_score"] <= 1.0