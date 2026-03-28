import pytest
from fastapi import status


@pytest.fixture(scope="function")
def graph_edge_data():
    """
    Фикстура с реальными ребрами из графа Тверского района.
    
    Returns:
        list: Список ребер графа с source, target и весом.
    """
    return [
        {"source": "35903409", "target": "54615001", "weight": 1.5},
        {"source": "54615001", "target": "54615002", "weight": 2.0},
        {"source": "54615002", "target": "54615236", "weight": 1.8}
    ]


@pytest.fixture(scope="function")
def valid_district():
    """
    Фикстура с валидным названием района, имеющим загруженный граф.
    
    Returns:
        str: Название района.
    """
    return "tverskoy"


@pytest.fixture(scope="function")
def graph_node_ids(valid_district):
    """
    Фикстура, возвращающая реальные ID узлов из графа района.
    
    Args:
        valid_district: Название района из фикстуры.
        
    Returns:
        dict: Словарь с идентификаторами узлов графа.
    """
    from app.services.graph_service import load_graph
    
    _, G = load_graph(valid_district)
    nodes = list(G.nodes())
    
    return {
        "node1": nodes[0] if len(nodes) > 0 else None,
        "node2": nodes[1] if len(nodes) > 1 else None,
        "node3": nodes[2] if len(nodes) > 2 else None,
        "node4": nodes[3] if len(nodes) > 3 else None,
    }


class TestGraphRoutes:
    """Тесты для маршрутов работы с графами"""
    
    def test_get_graph_tverskoy_success(self, client, valid_district):
        """
        Тест успешного получения графа Тверского района.
        
        Проверяет, что эндпоинт возвращает данные графа
        для существующего района.
        """
        response = client.get(f"/api/graph/{valid_district}")
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_graph_returns_valid_schema(self, client, valid_district):
        """
        Тест валидности схемы ответа при получении графа.
        
        Проверяет наличие обязательных полей в ответе:
        метаданные, узлы и ребра.
        """
        response = client.get(f"/api/graph/{valid_district}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "metadata" in data
        assert "nodes" in data
        assert "edges" in data

    def test_get_graph_metadata_valid(self, client, valid_district):
        """
        Тест валидности метаданных графа.
        
        Проверяет, что метаданные содержат все необходимые поля
        и соответствуют запрошенному району.
        """
        response = client.get(f"/api/graph/{valid_district}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        metadata = data["metadata"]
        
        assert "name" in metadata
        assert "city" in metadata
        assert "district" in metadata
        assert metadata["district"] == valid_district

    def test_get_graph_nodes_valid_structure(self, client, valid_district):
        """
        Тест структуры узлов графа.
        
        Проверяет, что каждый узел содержит обязательные поля
        и корректные координаты.
        """
        response = client.get(f"/api/graph/{valid_district}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        nodes = data["nodes"]
        
        assert isinstance(nodes, list)
        assert len(nodes) > 0
        
        node = nodes[0]
        assert "id" in node
        assert "label" in node
        assert "lat" in node
        assert "lon" in node
        
        assert isinstance(node["lat"], (int, float))
        assert isinstance(node["lon"], (int, float))
        assert -90 <= node["lat"] <= 90
        assert -180 <= node["lon"] <= 180

    def test_get_graph_edges_valid_structure(self, client, valid_district):
        """
        Тест структуры ребер графа.
        
        Проверяет, что каждое ребро содержит обязательные поля
        и имеет корректный вес.
        """
        response = client.get(f"/api/graph/{valid_district}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        edges = data["edges"]
        
        assert isinstance(edges, list)
        assert len(edges) > 0
        
        edge = edges[0]
        assert "source" in edge
        assert "target" in edge
        assert "weight" in edge
        
        assert isinstance(edge["weight"], (int, float))
        assert edge["weight"] > 0

    def test_get_graph_nodes_count_reasonable(self, client, valid_district):
        """
        Тест разумного количества узлов в графе.
        
        Проверяет, что граф содержит минимальное количество узлов,
        характерное для городского района.
        """
        response = client.get(f"/api/graph/{valid_district}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        nodes = data["nodes"]
        
        assert len(nodes) >= 100

    def test_get_graph_edges_count_reasonable(self, client, valid_district):
        """
        Тест разумного количества ребер в графе.
        
        Проверяет, что количество ребер соответствует
        минимальным требованиям связности графа.
        """
        response = client.get(f"/api/graph/{valid_district}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        edges = data["edges"]
        
        assert len(edges) >= len(data["nodes"]) / 2

    def test_get_graph_not_found(self, client):
        """
        Тест получения несуществующего графа.
        
        Проверяет, что запрос к несуществующему району
        возвращает статус 404.
        """
        response = client.get("/api/graph/nonexistent_xyz_district")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_graph_not_found_error_message(self, client):
        """
        Тест сообщения об ошибке при отсутствии графа.
        
        Проверяет, что ответ содержит корректное сообщение
        об ошибке с указанием причины.
        """
        response = client.get("/api/graph/invalid_district")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_calculate_no_changes(self, client, valid_district):
        """
        Тест расчета метрик без изменений графа.
        
        Проверяет, что запрос без модификаций графа
        возвращает корректные метрики.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_200_OK

    def test_calculate_response_structure(self, client, valid_district):
        """
        Тест структуры ответа при расчете метрик.
        
        Проверяет наличие всех обязательных полей в ответе:
        метрики, показатели устойчивости и время расчета.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "metrics" in data
        assert "resilience" in data
        assert "calculation_time_ms" in data

    def test_calculate_metrics_structure(self, client, valid_district):
        """
        Тест структуры метрик графа.
        
        Проверяет, что метрики содержат все необходимые показатели
        центральности и список критических узлов.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        metrics = data["metrics"]
        
        assert "betweenness" in metrics
        assert "closeness" in metrics
        assert "degree" in metrics
        assert "critical_nodes" in metrics
        
        assert isinstance(metrics["betweenness"], dict)
        assert isinstance(metrics["closeness"], dict)
        assert isinstance(metrics["degree"], dict)
        assert isinstance(metrics["critical_nodes"], list)

    def test_calculate_resilience_present(self, client, valid_district):
        """
        Тест наличия показателей устойчивости.
        
        Проверяет, что в ответе присутствуют метрики
        устойчивости графа к изменениям.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "resilience" in data
        assert isinstance(data["resilience"], dict)
        assert len(data["resilience"]) > 0

    def test_calculate_calculation_time_positive(self, client, valid_district):
        """
        Тест положительного времени расчета.
        
        Проверяет, что время расчета метрик является
        неотрицательным числом.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["calculation_time_ms"] >= 0

    def test_calculate_district_not_found(self, client):
        """
        Тест расчета для несуществующего района.
        
        Проверяет, что запрос к несуществующему району
        возвращает статус 404.
        """
        changes = {
            "district": "nonexistent_xyz",
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_calculate_missing_district_field(self, client):
        """
        Тест расчета без указания района.
        
        Проверяет, что запрос без обязательного поля district
        возвращает ошибку валидации.
        """
        changes = {
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_calculate_with_removed_nodes(self, client, valid_district, graph_node_ids):
        """
        Тест расчета с удаленными узлами.
        
        Проверяет корректность обработки запроса
        на удаление существующих узлов графа.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [graph_node_ids["node1"]],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "metrics" in data
        assert "resilience" in data

    def test_calculate_with_removed_edges(self, client, valid_district, graph_node_ids):
        """
        Тест расчета с удаленными ребрами.
        
        Проверяет корректность обработки запроса
        на удаление существующих ребер графа.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [[graph_node_ids["node1"], graph_node_ids["node2"]]],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_200_OK

    def test_calculate_with_added_nodes(self, client, valid_district):
        """
        Тест расчета с добавленными узлами.
        
        Проверяет корректность обработки запроса
        на добавление новых узлов в граф.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [
                {"id": "new_node_1", "label": "New Node", "lat": 55.75, "lon": 37.61}
            ],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_200_OK

    def test_calculate_with_added_edges(self, client, valid_district, graph_node_ids):
        """
        Тест расчета с добавленными ребрами.
        
        Проверяет корректность обработки запроса
        на добавление новых ребер в граф.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": [
                [graph_node_ids["node1"], graph_node_ids["node2"]]  
            ]
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_200_OK

    def test_calculate_with_nonexistent_nodes(self, client, valid_district):
        """
        Тест расчета с несуществующими узлами.
        
        Проверяет, что система корректно обрабатывает запросы
        с удалением несуществующих узлов.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": ["nonexistent_node_xyz"],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_200_OK

    def test_calculate_critical_nodes_not_empty(self, client, valid_district):
        """
        Тест обнаружения критических узлов.
        
        Проверяет, что в графе находятся хотя бы
        несколько критических узлов.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        critical_nodes = data["metrics"]["critical_nodes"]
        
        assert len(critical_nodes) > 0


class TestGraphIntegration:
    """Интеграционные тесты для операций с графами"""
    
    def test_get_then_calculate(self, client, valid_district):
        """
        Тест последовательности: получение графа, затем расчет.
        
        Проверяет корректность работы эндпоинтов в связке:
        сначала получение данных графа, затем расчет с использованием
        реальных идентификаторов узлов.
        """
        get_response = client.get(f"/api/graph/{valid_district}")
        assert get_response.status_code == status.HTTP_200_OK
        
        graph_data = get_response.json()
        
        node_ids = [node["id"] for node in graph_data["nodes"][:3]]
        
        changes = {
            "district": valid_district,
            "removed_nodes": [node_ids[0]] if node_ids else [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        calc_response = client.post("/api/graph/calculate", json=changes)
        assert calc_response.status_code == status.HTTP_200_OK

    def test_calculate_before_after_comparison(self, client, valid_district, graph_node_ids):
        """
        Тест сравнения метрик до и после изменений.
        
        Проверяет, что расчет метрик для исходного и модифицированного
        графа возвращает корректные результаты для сравнения.
        """
        changes_no_modification = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response_baseline = client.post("/api/graph/calculate", json=changes_no_modification)
        assert response_baseline.status_code == status.HTTP_200_OK
        data_baseline = response_baseline.json()
        
        changes_with_removal = {
            "district": valid_district,
            "removed_nodes": [graph_node_ids["node1"]],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response_modified = client.post("/api/graph/calculate", json=changes_with_removal)
        assert response_modified.status_code == status.HTTP_200_OK
        data_modified = response_modified.json()
        
        assert "metrics" in data_baseline
        assert "metrics" in data_modified
        assert "resilience" in data_baseline
        assert "resilience" in data_modified

    def test_multiple_changes_combined(self, client, valid_district, graph_node_ids):
        """
        Тест расчета с комбинацией различных изменений.
        
        Проверяет корректность обработки запроса,
        содержащего одновременно удаления и добавления
        узлов и ребер.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [graph_node_ids["node1"]],
            "removed_edges": [[graph_node_ids["node2"], graph_node_ids["node3"]]],
            "added_nodes": [
                {"id": "new_node_1", "label": "New", "lat": 55.75, "lon": 37.61},
                {"id": "new_node_2", "label": "New 2", "lat": 55.76, "lon": 37.62}
            ],
            "added_edges": [
                [graph_node_ids["node4"], "new_node_1"]
            ]
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_200_OK

    def test_graph_structure_consistency(self, client, valid_district):
        """
        Тест согласованности структуры графа.
        
        Проверяет, что все узлы, используемые в ребрах,
        действительно существуют в графе.
        """
        response = client.get(f"/api/graph/{valid_district}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        nodes = {node["id"]: node for node in data["nodes"]}
        edges = data["edges"]
        
        for edge in edges:
            assert edge["source"] in nodes
            assert edge["target"] in nodes

    def test_centrality_metrics_existence(self, client, valid_district):
        """
        Тест расчета всех типов центральности.
        
        Проверяет, что для графа рассчитываются все три
        типа метрик центральности: посредничество, близость и степень.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client.post("/api/graph/calculate", json=changes)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        metrics = data["metrics"]
        
        assert len(metrics["betweenness"]) > 0
        assert len(metrics["closeness"]) > 0
        assert len(metrics["degree"]) > 0

    def test_calculation_reproducibility(self, client, valid_district):
        """
        Тест воспроизводимости результатов.
        
        Проверяет, что повторный расчет с одинаковыми входными данными
        дает идентичные результаты.
        """
        changes = {
            "district": valid_district,
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response1 = client.post("/api/graph/calculate", json=changes)
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        
        response2 = client.post("/api/graph/calculate", json=changes)
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        
        assert data1["metrics"]["critical_nodes"] == data2["metrics"]["critical_nodes"]