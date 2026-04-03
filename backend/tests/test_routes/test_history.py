import pytest
from fastapi import status
from app.schemas.history import ActionType


@pytest.fixture(scope="function")
def test_scenario(db_session, test_user):
    """
    Фикстура, создающая тестовый сценарий для тестирования истории.
    
    Args:
        db_session: Сессия базы данных.
        test_user: Тестовый пользователь.
        
    Returns:
        Scenario: Созданный объект сценария.
    """
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


@pytest.fixture(scope="function")
def test_scenario_2(db_session, test_user):
    """
    Фикстура, создающая второй тестовый сценарий для тестирования истории.
    
    Args:
        db_session: Сессия базы данных.
        test_user: Тестовый пользователь.
        
    Returns:
        Scenario: Созданный объект сценария.
    """
    from app.models.scenario import Scenario
    
    scenario = Scenario(
        user_id=test_user.id,
        name="Test Scenario 2",
        description="Another Test Description",
        district="tverskoy",
        removed_nodes=["node1"],
        removed_edges=[],
        added_nodes=[],
        added_edges=[],
        hits=0
    )
    db_session.add(scenario)
    db_session.commit()
    db_session.refresh(scenario)
    return scenario


@pytest.fixture(scope="function")
def valid_scenario_data():
    """
    Фикстура с валидными данными для создания сценария.
    
    Returns:
        dict: Данные для создания тестового сценария.
    """
    return {
        "name": "New Test Scenario",
        "description": "A brand new test scenario",
        "district": "tverskoy",
        "removed_nodes": [],
        "removed_edges": [],
        "added_nodes": [],
        "added_edges": []
    }


class TestHistoryRoutes:
    """Тесты для маршрутов работы с историей"""
    
    def test_get_user_history_unauthorized(self, client):
        """
        Тест требования аутентификации для получения истории.
        
        Проверяет, что запрос к истории пользователя без токена
        возвращает ошибку авторизации.
        """
        response = client.get("/api/history")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_history_empty(self, client_with_auth):
        """
        Тест получения пустой истории пользователя.
        
        Проверяет, что для нового пользователя возвращается
        корректная структура ответа с нулевым количеством записей.
        """
        response = client_with_auth.get("/api/history")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_get_user_history_with_data(self, client_with_auth, test_user, db_session):
        """
        Тест получения истории с записями.
        
        Проверяет, что созданные записи истории корректно
        возвращаются при запросе.
        """
        from app.models.history import History
        
        for i in range(3):
            history = History(
                user_id=test_user.id,
                action=ActionType.CALCULATE,
                details={"test": f"detail_{i}"},
                calculation_time_ms=100.5 + i
            )
            db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get("/api/history")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_get_user_history_valid_schema(self, client_with_auth, test_user, db_session):
        """
        Тест валидности схемы записей истории.
        
        Проверяет, что каждая запись истории содержит
        все необходимые поля.
        """
        from app.models.history import History
        
        history = History(
            user_id=test_user.id,
            action=ActionType.SAVE,
            details={"scenario_name": "Test Scenario"},
            calculation_time_ms=50.0
        )
        db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get("/api/history")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        item = data["items"][0]
        assert "id" in item
        assert "user_id" in item
        assert "scenario_id" in item
        assert "action" in item
        assert "details" in item
        assert "created_at" in item
        assert "calculation_time_ms" in item

    def test_get_user_history_pagination(self, client_with_auth, test_user, db_session):
        """
        Тест пагинации истории пользователя.
        
        Проверяет корректную работу параметров page и size,
        а также вычисление общего количества страниц.
        """
        from app.models.history import History
        
        for i in range(15):
            history = History(
                user_id=test_user.id,
                action=ActionType.VIEW,
                details={"index": i}
            )
            db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get("/api/history?page=1&size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["pages"] == 2
        
        response = client_with_auth.get("/api/history?page=2&size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 5
        assert data["page"] == 2

    def test_get_user_history_only_own_records(
        self, 
        client_with_auth, 
        client_with_auth_user_2, 
        test_user, 
        test_user_2, 
        db_session
    ):
        """
        Тест изоляции истории между пользователями.
        
        Проверяет, что пользователь видит только свои записи истории
        и не имеет доступа к записям других пользователей.
        """
        from app.models.history import History
        
        history1 = History(
            user_id=test_user.id,
            action=ActionType.CALCULATE,
            details={"user": "user1"}
        )
        db_session.add(history1)
        
        history2 = History(
            user_id=test_user_2.id,
            action=ActionType.VIEW,
            details={"user": "user2"}
        )
        db_session.add(history2)
        db_session.commit()
        
        response1 = client_with_auth.get("/api/history")
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert data1["total"] == 1
        assert data1["items"][0]["action"] == "calculate"
        
        response2 = client_with_auth_user_2.get("/api/history")
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert data2["total"] == 1
        assert data2["items"][0]["action"] == "view"

    def test_get_user_history_various_action_types(self, client_with_auth, test_user, db_session):
        """
        Тест получения записей с различными типами действий.
        
        Проверяет, что история корректно хранит и возвращает
        записи всех типов действий.
        """
        from app.models.history import History
        
        actions = [ActionType.CALCULATE, ActionType.SAVE, ActionType.DELETE, ActionType.VIEW]
        
        for action in actions:
            history = History(
                user_id=test_user.id,
                action=action,
                details={"action": action.value}
            )
            db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get("/api/history")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 4
        retrieved_actions = [item["action"] for item in data["items"]]
        for action in actions:
            assert action.value in retrieved_actions

    def test_get_scenario_history_unauthorized(self, client, test_scenario):
        """
        Тест требования аутентификации для получения истории сценария.
        
        Проверяет, что запрос к истории сценария без токена
        возвращает ошибку авторизации.
        """
        response = client.get(f"/api/history/scenario/{test_scenario.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_scenario_history_empty(self, client_with_auth, test_scenario):
        """
        Тест получения пустой истории сценария.
        
        Проверяет, что для сценария без истории возвращается
        корректная структура ответа с нулевым количеством записей.
        """
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_get_scenario_history_with_data(self, client_with_auth, test_scenario, test_user, db_session):
        """
        Тест получения истории сценария с записями.
        
        Проверяет, что созданные записи истории для конкретного сценария
        корректно возвращаются при запросе.
        """
        from app.models.history import History
        
        for i in range(3):
            history = History(
                user_id=test_user.id,
                scenario_id=test_scenario.id,
                action=ActionType.VIEW,
                details={"view": i}
            )
            db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_get_scenario_history_valid_schema(self, client_with_auth, test_scenario, test_user, db_session):
        """
        Тест валидности схемы записей истории сценария.
        
        Проверяет, что каждая запись истории содержит
        все необходимые поля, включая привязку к сценарию.
        """
        from app.models.history import History
        
        history = History(
            user_id=test_user.id,
            scenario_id=test_scenario.id,
            action=ActionType.CALCULATE,
            details={"district": "tverskoy"},
            calculation_time_ms=125.5
        )
        db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        item = data["items"][0]
        assert item["scenario_id"] == test_scenario.id
        assert item["action"] == "calculate"
        assert item["calculation_time_ms"] == 125.5
        assert "scenario_name" in item

    def test_get_scenario_history_includes_scenario_name(self, client_with_auth, test_scenario, test_user, db_session):
        """
        Тест включения имени сценария в записи истории.
        
        Проверяет, что в ответе присутствует поле scenario_name
        для удобства отображения.
        """
        from app.models.history import History
        
        history = History(
            user_id=test_user.id,
            scenario_id=test_scenario.id,
            action=ActionType.SAVE,
            details={}
        )
        db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        item = data["items"][0]
        assert item["scenario_name"] == test_scenario.name

    def test_get_scenario_history_pagination(self, client_with_auth, test_scenario, test_user, db_session):
        """
        Тест пагинации истории сценария.
        
        Проверяет корректную работу параметров page и size
        для истории конкретного сценария.
        """
        from app.models.history import History
        
        for i in range(15):
            history = History(
                user_id=test_user.id,
                scenario_id=test_scenario.id,
                action=ActionType.VIEW,
                details={"index": i}
            )
            db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}?page=1&size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["pages"] == 2
        
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}?page=2&size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 5
        assert data["page"] == 2

    def test_get_scenario_history_only_for_scenario(
        self, 
        client_with_auth, 
        test_scenario, 
        test_scenario_2, 
        test_user, 
        db_session
    ):
        """
        Тест фильтрации истории по сценарию.
        
        Проверяет, что при запросе истории конкретного сценария
        возвращаются только записи, относящиеся к этому сценарию.
        """
        from app.models.history import History
        
        history1 = History(
            user_id=test_user.id,
            scenario_id=test_scenario.id,
            action=ActionType.VIEW,
            details={"scenario": 1}
        )
        db_session.add(history1)
        
        history2 = History(
            user_id=test_user.id,
            scenario_id=test_scenario_2.id,
            action=ActionType.VIEW,
            details={"scenario": 2}
        )
        db_session.add(history2)
        db_session.commit()
        
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 1
        assert data["items"][0]["scenario_id"] == test_scenario.id

    def test_get_scenario_history_nonexistent_scenario(self, client_with_auth):
        """
        Тест получения истории для несуществующего сценария.
        
        Проверяет, что запрос для несуществующего сценария
        возвращает пустую историю без ошибки.
        """
        response = client_with_auth.get("/api/history/scenario/99999")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_history_with_calculation_time(self, client_with_auth, test_user, db_session):
        """
        Тест сохранения времени расчета.
        
        Проверяет, что поле calculation_time_ms корректно
        сохраняется и возвращается в записях истории.
        """
        from app.models.history import History
        
        calc_time = 256.75
        history = History(
            user_id=test_user.id,
            action=ActionType.CALCULATE,
            details={"district": "tverskoy"},
            calculation_time_ms=calc_time
        )
        db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get("/api/history")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["items"][0]["calculation_time_ms"] == calc_time

    def test_history_without_calculation_time(self, client_with_auth, test_user, db_session):
        """
        Тест записей истории без времени расчета.
        
        Проверяет, что записи без указания времени расчета
        корректно обрабатываются и возвращают None.
        """
        from app.models.history import History
        
        history = History(
            user_id=test_user.id,
            action=ActionType.VIEW,
            details={"scenario": "test"}
        )
        db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get("/api/history")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["items"][0]["calculation_time_ms"] is None


class TestHistoryIntegration:
    """Интеграционные тесты для операций с историей"""
    
    def test_history_created_on_scenario_save(self, client_with_auth, valid_scenario_data, test_user, db_session):
        """
        Тест создания записи истории при сохранении сценария.
        
        Проверяет, что при создании нового сценария автоматически
        создается запись в истории с действием SAVE.
        """
        response = client_with_auth.post("/api/scenarios", json=valid_scenario_data)
        
        if response.status_code == status.HTTP_201_CREATED:
            history_response = client_with_auth.get("/api/history")
            assert history_response.status_code == status.HTTP_200_OK
            
            data = history_response.json()
            assert data["total"] > 0
            
            save_actions = [h for h in data["items"] if h["action"] == "save"]
            assert len(save_actions) > 0

    def test_history_created_on_scenario_view(
        self, client_with_auth, client_with_auth_user_2, test_scenario
    ):
        """
        Тест создания записи истории при просмотре чужого сценария.

        VIEW-запись создаётся через POST /api/scenarios/{id}/view
        только при просмотре чужого сценария другим пользователем.
        """
        response = client_with_auth_user_2.post(f"/api/scenarios/{test_scenario.id}/view")
        assert response.status_code == status.HTTP_200_OK

        history_response = client_with_auth_user_2.get("/api/history")
        assert history_response.status_code == status.HTTP_200_OK

        data = history_response.json()
        view_actions = [h for h in data["items"] if h["action"] == "view"]
        assert len(view_actions) > 0

    def test_history_created_on_scenario_delete(self, client_with_auth, test_scenario):
        """
        Тест создания записи истории при удалении сценария.
        
        Проверяет, что при удалении сценария автоматически
        создается запись в истории с действием DELETE.
        """
        scenario_id = test_scenario.id
        
        response = client_with_auth.delete(f"/api/scenarios/{scenario_id}")
        assert response.status_code == status.HTTP_200_OK
        
        history_response = client_with_auth.get("/api/history")
        assert history_response.status_code == status.HTTP_200_OK
        
        data = history_response.json()
        
        delete_actions = [h for h in data["items"] if h["action"] == "delete"]
        assert len(delete_actions) > 0

    def test_history_records_chronological_order(self, client_with_auth, test_user, db_session):
        """
        Тест хронологического порядка записей истории.
        
        Проверяет, что записи истории возвращаются в порядке
        убывания даты создания (сначала новые).
        """
        from app.models.history import History
        import time
        
        for i in range(3):
            history = History(
                user_id=test_user.id,
                action=ActionType.CALCULATE,
                details={"order": i}
            )
            db_session.add(history)
            db_session.commit()
            time.sleep(0.01)
        
        response = client_with_auth.get("/api/history")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        items = data["items"]
        
        for i in range(len(items) - 1):
            assert items[i]["created_at"] >= items[i + 1]["created_at"]

    def test_scenario_history_with_multiple_users(
        self, 
        client_with_auth, 
        client_with_auth_user_2, 
        test_user, 
        test_user_2, 
        test_scenario, 
        db_session
    ):
        """
        Тест истории сценария от нескольких пользователей.
        
        Проверяет, что история сценария содержит записи
        от всех пользователей, взаимодействовавших со сценарием.
        """
        from app.models.history import History
        
        history1 = History(
            user_id=test_user.id,
            scenario_id=test_scenario.id,
            action=ActionType.VIEW,
            details={"user": 1}
        )
        db_session.add(history1)
        
        history2 = History(
            user_id=test_user_2.id,
            scenario_id=test_scenario.id,
            action=ActionType.VIEW,
            details={"user": 2}
        )
        db_session.add(history2)
        db_session.commit()
        
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["total"] == 2
        
        user_ids = [item["user_id"] for item in data["items"]]
        assert test_user.id in user_ids
        assert test_user_2.id in user_ids

    def test_detailed_history_information(self, client_with_auth, test_scenario, test_user, db_session):
        """
        Тест сохранения детальной информации в истории.
        
        Проверяет, что произвольные данные, передаваемые в details,
        корректно сохраняются и возвращаются в записи истории.
        """
        from app.models.history import History
        
        details_data = {
            "district": "tverskoy",
            "nodes_removed": 5,
            "edges_added": 3
        }
        
        history = History(
            user_id=test_user.id,
            scenario_id=test_scenario.id,
            action=ActionType.CALCULATE,
            details=details_data,
            calculation_time_ms=512.3
        )
        db_session.add(history)
        db_session.commit()
        
        response = client_with_auth.get(f"/api/history/scenario/{test_scenario.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        item = data["items"][0]
        
        assert item["details"] == details_data
        assert item["calculation_time_ms"] == 512.3

    def test_history_list_response_structure(self, client_with_auth):
        """
        Тест структуры ответа списка истории.
        
        Проверяет, что ответ на запрос списка истории
        содержит все необходимые поля для пагинации.
        """
        response = client_with_auth.get("/api/history")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["size"], int)
        assert isinstance(data["pages"], int)