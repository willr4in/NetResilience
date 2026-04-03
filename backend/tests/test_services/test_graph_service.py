import pytest
import networkx as nx
from pathlib import Path
from app.services.graph_service import load_graph, apply_changes, run_analysis, analyze, district_exists, simulate_cascade, haversine
from app.schemas.graph import GraphChanges, GraphSchema, NodeSchema, EdgeSchema, GraphMetadata, CascadeRequest


@pytest.fixture
def valid_district():
    """
    Фикстура с валидным названием района.
    
    Returns:
        str: Название существующего района.
    """
    return "tverskoy"


@pytest.fixture
def invalid_district():
    """
    Фикстура с невалидным названием района.
    
    Returns:
        str: Название несуществующего района.
    """
    return "nonexistent_district"


@pytest.fixture
def graph_changes_empty():
    """
    Фикстура с пустыми изменениями графа.
    
    Returns:
        GraphChanges: Объект изменений без модификаций.
    """
    return GraphChanges(
        district="tverskoy",
        removed_nodes=[],
        removed_edges=[],
        added_nodes=[],
        added_edges=[]
    )


@pytest.fixture
def graph_changes_remove_nodes():
    """
    Фикстура с удалением узлов.
    
    Returns:
        GraphChanges: Объект изменений с удалением реальных узлов графа.
    """
    return GraphChanges(
        district="tverskoy",
        removed_nodes=["35880127", "35881070"],
        removed_edges=[],
        added_nodes=[],
        added_edges=[]
    )


@pytest.fixture
def graph_changes_remove_edges():
    """
    Фикстура с удалением ребер.
    
    Returns:
        GraphChanges: Объект изменений с удалением реальных ребер графа.
    """
    return GraphChanges(
        district="tverskoy",
        removed_nodes=[],
        removed_edges=[["35880127", "35881070"]],
        added_nodes=[],
        added_edges=[]
    )


@pytest.fixture
def graph_changes_add_nodes():
    """
    Фикстура с добавлением узлов.
    
    Returns:
        GraphChanges: Объект изменений с добавлением новых узлов.
    """
    return GraphChanges(
        district="tverskoy",
        removed_nodes=[],
        removed_edges=[],
        added_nodes=[
            {"id": "new_node1", "label": "New Node 1", "lat": 55.75, "lon": 37.62},
            {"id": "new_node2", "label": "New Node 2", "lat": 55.76, "lon": 37.63}
        ],
        added_edges=[]
    )


@pytest.fixture
def graph_changes_add_edges():
    """
    Фикстура с добавлением ребер.
    
    Returns:
        GraphChanges: Объект изменений с добавлением новых ребер.
    """
    return GraphChanges(
        district="tverskoy",
        removed_nodes=[],
        removed_edges=[],
        added_nodes=[],
        added_edges=[["35880127", "35881070"], ["35881796", "35881998"]]
    )


@pytest.fixture
def graph_changes_complex():
    """
    Фикстура со сложными изменениями графа.
    
    Returns:
        GraphChanges: Объект изменений, содержащий удаления и добавления.
    """
    return GraphChanges(
        district="tverskoy",
        removed_nodes=["35880127"],
        removed_edges=[],
        added_nodes=[{"id": "new_node", "label": "New", "lat": 55.75, "lon": 37.62}],
        added_edges=[["35881070", "new_node"]]
    )


class TestDistrictExists:
    """Тесты для функции проверки существования района"""
    
    def test_district_exists_tverskoy(self):
        """
        Тест существующего района.
        
        Проверяет, что для существующего района
        функция возвращает True.
        """
        assert district_exists("tverskoy") is True

    def test_district_not_exists(self):
        """
        Тест несуществующего района.
        
        Проверяет, что для несуществующего района
        функция возвращает False.
        """
        assert district_exists("nonexistent") is False

    def test_district_case_insensitive(self):
        """
        Тест нечувствительности к регистру.
        
        Проверяет, что проверка существования района
        не зависит от регистра символов.
        """
        assert district_exists("TVERSKOY") is True
        assert district_exists("Tverskoy") is True


class TestLoadGraph:
    """Тесты для функции загрузки графа"""
    
    def test_load_graph_success(self, valid_district):
        """
        Тест успешной загрузки графа.
        
        Проверяет, что граф загружается и возвращаются
        корректные объекты схемы и networkx графа.
        """
        graph_schema, G = load_graph(valid_district)
        assert isinstance(graph_schema, GraphSchema)
        assert isinstance(G, nx.Graph)

    def test_load_graph_returns_tuple(self, valid_district):
        """
        Тест возврата кортежа.
        
        Проверяет, что функция возвращает кортеж
        из двух элементов.
        """
        result = load_graph(valid_district)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_load_graph_schema_has_metadata(self, valid_district):
        """
        Тест наличия метаданных в схеме.
        
        Проверяет, что загруженная схема графа
        содержит корректные метаданные.
        """
        graph_schema, _ = load_graph(valid_district)
        assert isinstance(graph_schema.metadata, GraphMetadata)
        assert graph_schema.metadata.district == valid_district

    def test_load_graph_has_nodes(self, valid_district):
        """
        Тест наличия узлов.
        
        Проверяет, что загруженный граф содержит узлы.
        """
        graph_schema, G = load_graph(valid_district)
        assert len(graph_schema.nodes) > 0
        assert len(G.nodes()) > 0

    def test_load_graph_has_edges(self, valid_district):
        """
        Тест наличия ребер.
        
        Проверяет, что загруженный граф содержит ребра.
        """
        graph_schema, G = load_graph(valid_district)
        assert len(graph_schema.edges) > 0
        assert len(G.edges()) > 0

    def test_load_graph_nodes_match(self, valid_district):
        """
        Тест соответствия узлов.
        
        Проверяет, что узлы в схеме совпадают
        с узлами в networkx графе.
        """
        graph_schema, G = load_graph(valid_district)
        schema_node_ids = {node.id for node in graph_schema.nodes}
        graph_node_ids = set(G.nodes())
        assert schema_node_ids == graph_node_ids

    def test_load_graph_edges_match(self, valid_district):
        """
        Тест соответствия ребер.
        
        Проверяет, что количество ребер в схеме
        совпадает с количеством ребер в networkx графе.
        """
        graph_schema, G = load_graph(valid_district)
        assert len(graph_schema.edges) == len(G.edges())

    def test_load_graph_node_attributes(self, valid_district):
        """
        Тест атрибутов узлов.
        
        Проверяет, что каждый узел содержит
        все необходимые атрибуты.
        """
        graph_schema, G = load_graph(valid_district)
        for node_id in G.nodes():
            node_data = G.nodes[node_id]
            assert "label" in node_data
            assert "lat" in node_data
            assert "lon" in node_data

    def test_load_graph_edge_weights(self, valid_district):
        """
        Тест весов ребер.
        
        Проверяет, что каждое ребро имеет атрибут веса.
        """
        graph_schema, G = load_graph(valid_district)
        for source, target in G.edges():
            assert "weight" in G[source][target]

    def test_load_graph_nonexistent_district(self, invalid_district):
        """
        Тест загрузки несуществующего района.
        
        Проверяет, что попытка загрузить несуществующий
        район вызывает ошибку FileNotFoundError.
        """
        with pytest.raises(FileNotFoundError):
            load_graph(invalid_district)

    def test_load_graph_tverskoy_has_data(self):
        """
        Тест наличия данных в районе Тверской.
        
        Проверяет, что граф Тверского района
        содержит узлы и ребра.
        """
        graph_schema, G = load_graph("tverskoy")
        assert len(G.nodes()) > 0
        assert len(G.edges()) > 0


class TestApplyChanges:
    """Тесты для функции применения изменений к графу"""
    
    def test_apply_changes_returns_graph(self, valid_district, graph_changes_empty):
        """
        Тест возврата графа.
        
        Проверяет, что функция возвращает объект networkx графа.
        """
        _, G = load_graph(valid_district)
        G_modified = apply_changes(G, graph_changes_empty)
        assert isinstance(G_modified, nx.Graph)

    def test_apply_changes_no_modifications(self, valid_district, graph_changes_empty):
        """
        Тест без модификаций.
        
        Проверяет, что при отсутствии изменений
        граф остается неизменным.
        """
        _, G = load_graph(valid_district)
        original_nodes = len(G.nodes())
        original_edges = len(G.edges())
        
        G_modified = apply_changes(G, graph_changes_empty)
        assert len(G_modified.nodes()) == original_nodes
        assert len(G_modified.edges()) == original_edges

    def test_apply_changes_original_unchanged(self, valid_district, graph_changes_remove_nodes):
        """
        Тест неизменности исходного графа.
        
        Проверяет, что исходный граф не изменяется
        при применении изменений.
        """
        _, G = load_graph(valid_district)
        original_nodes = len(G.nodes())
        
        G_modified = apply_changes(G, graph_changes_remove_nodes)
        
        assert len(G.nodes()) == original_nodes
        assert len(G_modified.nodes()) <= len(G.nodes())

    def test_apply_changes_remove_real_nodes(self, valid_district):
        """
        Тест удаления реальных узлов.
        
        Проверяет, что узлы корректно удаляются из графа.
        """
        _, G = load_graph(valid_district)
        
        first_node = list(G.nodes())[0]
        changes = GraphChanges(
            district="tverskoy",
            removed_nodes=[first_node],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        original_count = len(G.nodes())
        G_modified = apply_changes(G, changes)
        
        assert len(G_modified.nodes()) == original_count - 1
        assert first_node not in G_modified.nodes()

    def test_apply_changes_remove_edges(self, valid_district, graph_changes_remove_edges):
        """
        Тест удаления ребер.
        
        Проверяет, что ребра корректно удаляются из графа.
        """
        _, G = load_graph(valid_district)
        original_edges = len(G.edges())
        
        G_modified = apply_changes(G, graph_changes_remove_edges)
        
        assert len(G_modified.edges()) <= original_edges

    def test_apply_changes_add_nodes(self, valid_district, graph_changes_add_nodes):
        """
        Тест добавления узлов.
        
        Проверяет, что новые узлы корректно добавляются в граф.
        """
        _, G = load_graph(valid_district)
        original_count = len(G.nodes())
        
        G_modified = apply_changes(G, graph_changes_add_nodes)
        
        assert len(G_modified.nodes()) > original_count
        assert G_modified.has_node("new_node1")
        assert G_modified.has_node("new_node2")

    def test_apply_changes_add_edges(self, valid_district, graph_changes_add_edges):
        """
        Тест добавления ребер.
        
        Проверяет, что новые ребра корректно добавляются в граф.
        """
        _, G = load_graph(valid_district)
        
        G_modified = apply_changes(G, graph_changes_add_edges)
        
        assert isinstance(G_modified, nx.Graph)
        assert len(G_modified.edges()) >= len(G.edges())

    def test_apply_changes_complex_scenario(self, valid_district, graph_changes_complex):
        """
        Тест сложного сценария изменений.
        
        Проверяет корректность применения комбинации
        удалений и добавлений.
        """
        _, G = load_graph(valid_district)
        
        G_modified = apply_changes(G, graph_changes_complex)
        
        assert G_modified is not None
        assert isinstance(G_modified, nx.Graph)
        assert G_modified.has_node("new_node")

    def test_apply_changes_preserves_graph_connectivity(self, valid_district, graph_changes_empty):
        """
        Тест сохранения связности.
        
        Проверяет, что связность графа сохраняется
        при пустых изменениях.
        """
        _, G = load_graph(valid_district)
        G_modified = apply_changes(G, graph_changes_empty)
        
        is_connected = nx.is_connected(G)
        is_modified_connected = nx.is_connected(G_modified)
        assert is_connected == is_modified_connected


class TestRunAnalysis:
    """Тесты для функции выполнения анализа графа"""
    
    def test_run_analysis_returns_dict(self, valid_district):
        """
        Тест возврата словаря.
        
        Проверяет, что функция анализа возвращает словарь.
        """
        _, G = load_graph(valid_district)
        result = run_analysis(G)
        assert isinstance(result, dict)

    def test_run_analysis_has_metrics(self, valid_district):
        """
        Тест наличия метрик.
        
        Проверяет, что результат анализа содержит метрики.
        """
        _, G = load_graph(valid_district)
        result = run_analysis(G)
        assert "metrics" in result
        assert isinstance(result["metrics"], dict)

    def test_run_analysis_has_resilience(self, valid_district):
        """
        Тест наличия показателей устойчивости.
        
        Проверяет, что результат анализа содержит
        данные об устойчивости графа.
        """
        _, G = load_graph(valid_district)
        result = run_analysis(G)
        assert "resilience" in result
        assert isinstance(result["resilience"], dict)

    def test_run_analysis_metrics_keys(self, valid_district):
        """
        Тест наличия всех метрик центральности.
        
        Проверяет, что метрики содержат все три типа
        центральности и список критических узлов.
        """
        _, G = load_graph(valid_district)
        result = run_analysis(G)
        metrics = result["metrics"]
        assert "betweenness" in metrics
        assert "closeness" in metrics
        assert "degree" in metrics
        assert "critical_nodes" in metrics

    def test_run_analysis_all_nodes_in_metrics(self, valid_district):
        """
        Тест наличия всех узлов в метриках.
        
        Проверяет, что для каждого узла графа
        рассчитаны все метрики центральности.
        """
        _, G = load_graph(valid_district)
        result = run_analysis(G)
        
        for metric_name in ["betweenness", "closeness", "degree"]:
            metric = result["metrics"][metric_name]
            for node in G.nodes():
                assert node in metric

    def test_run_analysis_critical_nodes_list(self, valid_district):
        """
        Тест формата списка критических узлов.
        
        Проверяет, что critical_nodes является списком.
        """
        _, G = load_graph(valid_district)
        result = run_analysis(G)
        assert isinstance(result["metrics"]["critical_nodes"], list)

    def test_run_analysis_with_original_graph(self, valid_district, graph_changes_remove_nodes):
        """
        Тест анализа с исходным графом.
        
        Проверяет, что при передаче исходного графа
        выполняется сравнение показателей устойчивости.
        """
        _, G_original = load_graph(valid_district)
        G_modified = apply_changes(G_original, graph_changes_remove_nodes)
        
        result = run_analysis(G_modified, G_original=G_original)
        assert "resilience" in result

    def test_run_analysis_without_original_graph(self, valid_district):
        """
        Тест анализа без исходного графа.
        
        Проверяет, что при отсутствии исходного графа
        анализ все равно выполняется корректно.
        """
        _, G = load_graph(valid_district)
        result = run_analysis(G, G_original=None)
        assert "resilience" in result

    def test_run_analysis_resilience_has_values(self, valid_district):
        """
        Тест наличия значений устойчивости.
        
        Проверяет, что показатели устойчивости содержат данные.
        """
        _, G = load_graph(valid_district)
        result = run_analysis(G)
        resilience = result["resilience"]
        assert len(resilience) > 0


class TestAnalyze:
    """Тесты для главной функции analyze"""
    
    def test_analyze_returns_response(self, graph_changes_empty):
        """
        Тест возврата ответа.
        
        Проверяет, что функция analyze возвращает
        объект GraphAnalysisResponse.
        """
        from app.schemas.graph import GraphAnalysisResponse
        response = analyze(graph_changes_empty)
        assert isinstance(response, GraphAnalysisResponse)

    def test_analyze_has_metrics(self, graph_changes_empty):
        """
        Тест наличия метрик в ответе.
        
        Проверяет, что ответ содержит метрики.
        """
        response = analyze(graph_changes_empty)
        assert response.metrics is not None
        assert response.metrics.betweenness is not None

    def test_analyze_has_resilience(self, graph_changes_empty):
        """
        Тест наличия устойчивости в ответе.
        
        Проверяет, что ответ содержит показатели устойчивости.
        """
        response = analyze(graph_changes_empty)
        assert response.resilience is not None

    def test_analyze_has_calculation_time(self, graph_changes_empty):
        """
        Тест наличия времени расчета.
        
        Проверяет, что ответ включает время выполнения расчета.
        """
        response = analyze(graph_changes_empty)
        assert response.calculation_time_ms >= 0.0

    def test_analyze_calculation_time_positive(self, graph_changes_empty):
        """
        Тест положительного времени расчета.
        
        Проверяет, что время расчета больше нуля.
        """
        response = analyze(graph_changes_empty)
        assert response.calculation_time_ms > 0.0

    def test_analyze_invalid_district(self):
        """
        Тест анализа с несуществующим районом.
        
        Проверяет, что попытка анализа несуществующего
        района вызывает ошибку.
        """
        invalid_changes = GraphChanges(
            district="nonexistent",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        with pytest.raises(FileNotFoundError):
            analyze(invalid_changes)

    def test_analyze_with_node_removal(self, graph_changes_remove_nodes):
        """
        Тест анализа с удалением узлов.
        
        Проверяет, что анализ выполняется корректно
        при удалении узлов из графа.
        """
        response = analyze(graph_changes_remove_nodes)
        assert response.metrics is not None
        assert response.resilience is not None
        assert response.calculation_time_ms > 0

    def test_analyze_with_edge_removal(self, graph_changes_remove_edges):
        """
        Тест анализа с удалением ребер.
        
        Проверяет, что анализ выполняется корректно
        при удалении ребер из графа.
        """
        response = analyze(graph_changes_remove_edges)
        assert response.metrics is not None

    def test_analyze_with_node_addition(self, graph_changes_add_nodes):
        """
        Тест анализа с добавлением узлов.
        
        Проверяет, что анализ выполняется корректно
        при добавлении новых узлов в граф.
        """
        response = analyze(graph_changes_add_nodes)
        assert response.metrics is not None

    def test_analyze_with_edge_addition(self, graph_changes_add_edges):
        """
        Тест анализа с добавлением ребер.
        
        Проверяет, что анализ выполняется корректно
        при добавлении новых ребер в граф.
        """
        response = analyze(graph_changes_add_edges)
        assert response.metrics is not None

    def test_analyze_complex_scenario(self, graph_changes_complex):
        """
        Тест анализа со сложными изменениями.
        
        Проверяет, что анализ выполняется корректно
        при комбинации удалений и добавлений.
        """
        response = analyze(graph_changes_complex)
        assert response.metrics is not None
        assert response.resilience is not None
        assert response.calculation_time_ms > 0


class TestGraphServiceIntegration:
    """Интеграционные тесты для сервиса работы с графами"""
    
    def test_load_and_analyze_tverskoy(self):
        """
        Тест загрузки и анализа района Тверской.
        
        Проверяет полный цикл загрузки графа
        и выполнения анализа.
        """
        changes = GraphChanges(
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        response = analyze(changes)
        assert response.metrics is not None
        assert len(response.metrics.betweenness) > 0

    def test_full_workflow_with_modifications(self):
        """
        Тест полного цикла с модификациями.
        
        Проверяет последовательность: загрузка, модификация, анализ.
        """
        changes = GraphChanges(
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[{"id": "test_node", "label": "Test", "lat": 55.75, "lon": 37.62}],
            added_edges=[]
        )
        response = analyze(changes)
        assert response.metrics is not None
        assert response.calculation_time_ms > 0


class TestHaversine:
    """Тесты для функции haversine"""

    def test_same_point_is_zero(self):
        """Расстояние от точки до себя равно нулю."""
        assert haversine(55.75, 37.61, 55.75, 37.61) == 0.0

    def test_known_distance_moscow(self):
        """
        Расстояние между центром Москвы и Красной площадью ~1 км.
        Допуск ±0.5 км.
        """
        dist = haversine(55.7512, 37.6184, 55.7558, 37.6173)
        assert 0.3 < dist < 1.5

    def test_result_is_positive(self):
        """Результат всегда положительный."""
        assert haversine(55.75, 37.61, 55.76, 37.62) > 0

    def test_symmetry(self):
        """Расстояние A→B равно B→A."""
        d1 = haversine(55.75, 37.61, 55.76, 37.62)
        d2 = haversine(55.76, 37.62, 55.75, 37.61)
        assert abs(d1 - d2) < 1e-9


class TestApplyChangesEdgeWeight:
    """Тесты для расчёта весов рёбер через haversine"""

    def test_added_edge_weight_uses_haversine(self):
        """
        Вес добавленного ребра рассчитывается через haversine,
        а не равен 1.0 по умолчанию.
        """
        _, G = load_graph("tverskoy")
        nodes = list(G.nodes())
        n1, n2 = nodes[0], nodes[1]

        changes = GraphChanges(
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[[n1, n2]]
        )
        G_mod = apply_changes(G, changes)
        weight = G_mod[n1][n2]["weight"]

        lat1, lon1 = G.nodes[n1]["lat"], G.nodes[n1]["lon"]
        lat2, lon2 = G.nodes[n2]["lat"], G.nodes[n2]["lon"]
        expected = haversine(lat1, lon1, lat2, lon2)

        assert abs(weight - expected) < 1e-6

    def test_added_edge_explicit_weight_preserved(self):
        """
        Если вес указан явно третьим элементом, он используется как есть.
        """
        _, G = load_graph("tverskoy")
        nodes = list(G.nodes())
        n1, n2 = nodes[0], nodes[1]

        changes = GraphChanges(
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[[n1, n2, "2.5"]]
        )
        G_mod = apply_changes(G, changes)
        assert abs(G_mod[n1][n2]["weight"] - 2.5) < 1e-6


class TestSimulateCascade:
    """Тесты для функции simulate_cascade"""

    def test_cascade_returns_response(self):
        """simulate_cascade возвращает CascadeResponse."""
        from app.schemas.graph import CascadeResponse
        req = CascadeRequest(district="tverskoy", steps=3)
        result = simulate_cascade(req)
        assert isinstance(result, CascadeResponse)

    def test_cascade_steps_count_matches(self):
        """Количество шагов совпадает с запрошенным."""
        req = CascadeRequest(district="tverskoy", steps=5)
        result = simulate_cascade(req)
        assert result.total_steps == 5
        assert len(result.steps) == 5

    def test_cascade_initial_score_positive(self):
        """initial_resilience_score > 0 для связного графа."""
        req = CascadeRequest(district="tverskoy", steps=3)
        result = simulate_cascade(req)
        assert result.initial_resilience_score > 0

    def test_cascade_with_removed_nodes_skips_them(self):
        """
        При каскаде на модифицированном графе (removed_nodes)
        удалённые узлы не появляются в шагах каскада.
        """
        _, G = load_graph("tverskoy")
        nodes = list(G.nodes())
        removed = nodes[:3]

        req = CascadeRequest(
            district="tverskoy",
            steps=5,
            removed_nodes=removed
        )
        result = simulate_cascade(req)
        cascade_removed = {step.removed_node_id for step in result.steps}
        for node in removed:
            assert node not in cascade_removed

    def test_cascade_with_modifications_fewer_nodes(self):
        """
        Каскад на графе с удалёнными узлами стартует
        с меньшим initial_resilience_score или равным (граф меньше).
        """
        _, G = load_graph("tverskoy")
        nodes = list(G.nodes())

        req_clean = CascadeRequest(district="tverskoy", steps=3)
        req_modified = CascadeRequest(
            district="tverskoy",
            steps=3,
            removed_nodes=nodes[:5]
        )

        result_clean = simulate_cascade(req_clean)
        result_modified = simulate_cascade(req_modified)

        # Модифицированный граф меньше — метрика не должна превышать оригинальную
        assert result_modified.initial_resilience_score <= result_clean.initial_resilience_score + 0.01

    def test_cascade_with_added_nodes_and_edges(self):
        """Каскад корректно работает при добавлении узлов и рёбер."""
        _, G = load_graph("tverskoy")
        nodes = list(G.nodes())

        req = CascadeRequest(
            district="tverskoy",
            steps=3,
            added_nodes=[{"id": "new_cascade_node", "label": "Test", "lat": 55.75, "lon": 37.62}],
            added_edges=[[nodes[0], "new_cascade_node"]]
        )
        result = simulate_cascade(req)
        assert result.total_steps == 3

    def test_cascade_invalid_district(self):
        """Несуществующий район вызывает FileNotFoundError."""
        req = CascadeRequest(district="nonexistent_xyz", steps=3)
        with pytest.raises(FileNotFoundError):
            simulate_cascade(req)

    def test_cascade_scores_in_valid_range(self):
        """Все resilience_score на шагах в диапазоне [0, 1]."""
        req = CascadeRequest(district="tverskoy", steps=5)
        result = simulate_cascade(req)
        for step in result.steps:
            assert 0.0 <= step.resilience_score <= 1.0
            assert 0.0 <= step.largest_component_ratio <= 1.0
            assert 0.0 <= step.betweenness_concentration <= 1.0