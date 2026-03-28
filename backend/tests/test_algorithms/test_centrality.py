import pytest
import networkx as nx
from app.algorithms.centrality import (
    calculate_betweenness,
    calculate_closeness,
    calculate_degree,
    calculate_all
)


@pytest.fixture
def simple_graph():
    """
    Фикстура, создающая простой линейный граф.
    
    Структура: A — B — C (линия из трех узлов).
    
    Returns:
        nx.Graph: Линейный граф из трех узлов.
    """
    G = nx.Graph()
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "C", weight=1.0)
    return G


@pytest.fixture
def star_graph():
    """
    Фикстура, создающая граф-звезду.
    
    Структура: центральный узел соединен со всеми остальными.
    
    Returns:
        nx.Graph: Граф-звезда с центром и четырьмя листьями.
    """
    G = nx.Graph()
    G.add_edge("center", "A", weight=1.0)
    G.add_edge("center", "B", weight=1.0)
    G.add_edge("center", "C", weight=1.0)
    G.add_edge("center", "D", weight=1.0)
    return G


@pytest.fixture
def complete_graph():
    """
    Фикстура, создающая полный граф.
    
    Returns:
        nx.Graph: Полный граф из 4 узлов (K4).
    """
    return nx.complete_graph(4)


@pytest.fixture
def empty_graph():
    """
    Фикстура, создающая пустой граф.
    
    Returns:
        nx.Graph: Граф без узлов и ребер.
    """
    return nx.Graph()


class TestCalculateBetweenness:
    """Тесты для расчета медианной центральности (betweenness centrality)"""
    
    def test_returns_dict(self, simple_graph):
        """
        Тест возврата словаря.
        
        Проверяет, что функция возвращает словарь с результатами.
        """
        result = calculate_betweenness(simple_graph)
        assert isinstance(result, dict)

    def test_all_nodes_present(self, simple_graph):
        """
        Тест наличия всех узлов в результате.
        
        Проверяет, что в словаре результатов присутствуют
        все узлы исходного графа.
        """
        result = calculate_betweenness(simple_graph)
        assert set(result.keys()) == {"A", "B", "C"}

    def test_middle_node_highest(self, simple_graph):
        """
        Тест максимального значения для центрального узла в линейном графе.
        
        Проверяет, что в линейном графе из трех узлов
        центральный узел имеет наибольшую медианную центральность.
        """
        result = calculate_betweenness(simple_graph)
        assert result["B"] > result["A"]
        assert result["B"] > result["C"]

    def test_endpoints_zero(self, simple_graph):
        """
        Тест нулевого значения для конечных узлов в линейном графе.
        
        Проверяет, что в линейном графе конечные узлы
        имеют медианную центральность равную 0.
        """
        result = calculate_betweenness(simple_graph)
        assert result["A"] == 0.0
        assert result["C"] == 0.0

    def test_star_center_highest(self, star_graph):
        """
        Тест максимального значения для центрального узла в графе-звезде.
        
        Проверяет, что в графе-звезде центральный узел
        имеет наибольшую медианную центральность.
        """
        result = calculate_betweenness(star_graph)
        assert result["center"] == max(result.values())

    def test_complete_graph_equal(self, complete_graph):
        """
        Тест равномерного распределения в полном графе.
        
        Проверяет, что в полном графе все узлы имеют
        одинаковую медианную центральность.
        """
        result = calculate_betweenness(complete_graph)
        values = list(result.values())
        assert max(values) - min(values) < 0.01

    def test_normalized_values_in_range(self, simple_graph):
        """
        Тест нормализации значений.
        
        Проверяет, что нормализованные значения медианной
        центральности находятся в диапазоне [0, 1].
        """
        result = calculate_betweenness(simple_graph, normalized=True)
        for v in result.values():
            assert 0.0 <= v <= 1.0

    def test_single_node(self):
        """
        Тест графа с одним узлом.
        
        Проверяет корректность обработки графа,
        содержащего только один узел.
        """
        G = nx.Graph()
        G.add_node("A")
        result = calculate_betweenness(G)
        assert result == {"A": 0.0}


class TestCalculateCloseness:
    """Тесты для расчета центральности близости (closeness centrality)"""
    
    def test_returns_dict(self, simple_graph):
        """
        Тест возврата словаря.
        
        Проверяет, что функция возвращает словарь с результатами.
        """
        result = calculate_closeness(simple_graph)
        assert isinstance(result, dict)

    def test_all_nodes_present(self, simple_graph):
        """
        Тест наличия всех узлов в результате.
        
        Проверяет, что в словаре результатов присутствуют
        все узлы исходного графа.
        """
        result = calculate_closeness(simple_graph)
        assert set(result.keys()) == {"A", "B", "C"}

    def test_middle_node_highest(self, simple_graph):
        """
        Тест максимального значения для центрального узла в линейном графе.
        
        Проверяет, что в линейном графе из трех узлов
        центральный узел имеет наибольшую центральность близости.
        """
        result = calculate_closeness(simple_graph)
        assert result["B"] > result["A"]
        assert result["B"] > result["C"]

    def test_endpoints_equal(self, simple_graph):
        """
        Тест равенства значений для конечных узлов в линейном графе.
        
        Проверяет, что в линейном графе конечные узлы
        имеют одинаковую центральность близости.
        """
        result = calculate_closeness(simple_graph)
        assert abs(result["A"] - result["C"]) < 1e-9

    def test_complete_graph_equal(self, complete_graph):
        """
        Тест равномерного распределения в полном графе.
        
        Проверяет, что в полном графе все узлы имеют
        одинаковую центральность близости.
        """
        result = calculate_closeness(complete_graph)
        values = list(result.values())
        assert max(values) - min(values) < 0.01

    def test_values_positive(self, simple_graph):
        """
        Тест положительных значений.
        
        Проверяет, что все значения центральности близости
        положительны для связного графа.
        """
        result = calculate_closeness(simple_graph)
        for v in result.values():
            assert v > 0.0


class TestCalculateDegree:
    """Тесты для расчета центральности степени (degree centrality)"""
    
    def test_returns_dict(self, simple_graph):
        """
        Тест возврата словаря.
        
        Проверяет, что функция возвращает словарь с результатами.
        """
        result = calculate_degree(simple_graph)
        assert isinstance(result, dict)

    def test_all_nodes_present(self, simple_graph):
        """
        Тест наличия всех узлов в результате.
        
        Проверяет, что в словаре результатов присутствуют
        все узлы исходного графа.
        """
        result = calculate_degree(simple_graph)
        assert set(result.keys()) == {"A", "B", "C"}

    def test_middle_node_highest(self, simple_graph):
        """
        Тест максимального значения для центрального узла в линейном графе.
        
        Проверяет, что в линейном графе из трех узлов
        центральный узел имеет наибольшую степень.
        """
        result = calculate_degree(simple_graph)
        assert result["B"] > result["A"]
        assert result["B"] > result["C"]

    def test_normalized_values_in_range(self, simple_graph):
        """
        Тест нормализации значений.
        
        Проверяет, что нормализованные значения степени
        находятся в диапазоне [0, 1].
        """
        result = calculate_degree(simple_graph, normalized=True)
        for v in result.values():
            assert 0.0 <= v <= 1.0

    def test_star_center_degree_one(self, star_graph):
        """
        Тест нормализованной степени для центрального узла в графе-звезде.
        
        Проверяет, что нормализованная степень центрального узла
        в графе-звезде равна 1.
        """
        result = calculate_degree(star_graph, normalized=True)
        assert result["center"] == 1.0

    def test_unnormalized_returns_counts(self, simple_graph):
        """
        Тест ненормализованных значений степени.
        
        Проверяет, что ненормализованные значения
        возвращают фактические количества связей.
        """
        result = calculate_degree(simple_graph, normalized=False)
        assert result["B"] == 2
        assert result["A"] == 1
        assert result["C"] == 1


class TestCalculateAll:
    """Тесты для расчета всех метрик центральности одновременно"""
    
    def test_returns_all_metrics(self, simple_graph):
        """
        Тест возврата всех метрик.
        
        Проверяет, что функция возвращает словарь,
        содержащий все три типа центральности.
        """
        result = calculate_all(simple_graph)
        assert "betweenness" in result
        assert "closeness" in result
        assert "degree" in result

    def test_empty_graph_returns_empty(self, empty_graph):
        """
        Тест пустого графа.
        
        Проверяет корректную обработку пустого графа:
        возвращаются пустые словари для всех метрик.
        """
        result = calculate_all(empty_graph)
        assert result == {"betweenness": {}, "closeness": {}, "degree": {}}

    def test_all_nodes_in_each_metric(self, simple_graph):
        """
        Тест наличия всех узлов в каждой метрике.
        
        Проверяет, что для каждой метрики центральности
        в результате присутствуют все узлы графа.
        """
        result = calculate_all(simple_graph)
        for metric in ["betweenness", "closeness", "degree"]:
            assert set(result[metric].keys()) == {"A", "B", "C"}

    def test_consistent_with_individual_functions(self, simple_graph):
        """
        Тест согласованности с отдельными функциями.
        
        Проверяет, что результаты, полученные функцией calculate_all,
        совпадают с результатами вызова отдельных функций.
        """
        result = calculate_all(simple_graph)
        betweenness = calculate_betweenness(simple_graph)
        for node in simple_graph.nodes():
            assert abs(result["betweenness"][node] - betweenness[node]) < 1e-9