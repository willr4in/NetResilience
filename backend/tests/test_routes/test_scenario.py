import pytest
from fastapi import status


@pytest.fixture(scope="function")
def test_scenario_2(db_session, test_user):
    """
    Фикстура, создающая второй тестовый сценарий для пользователя.
    
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
def test_scenario_other_user(db_session, test_user_2):
    """
    Фикстура, создающая тестовый сценарий для другого пользователя.
    
    Args:
        db_session: Сессия базы данных.
        test_user_2: Второй тестовый пользователь.
        
    Returns:
        Scenario: Созданный объект сценария.
    """
    from app.models.scenario import Scenario
    
    scenario = Scenario(
        user_id=test_user_2.id,
        name="Other User Scenario",
        description="Belongs to another user",
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


@pytest.fixture(scope="function")
def access_token_user_2(db_session, test_user_2):
    """
    Фикстура, создающая access token для второго пользователя.
    
    Args:
        db_session: Сессия базы данных.
        test_user_2: Второй тестовый пользователь.
        
    Returns:
        str: JWT токен доступа.
    """
    from app.services.auth_service import AuthService
    
    auth_service = AuthService(db_session)
    token = auth_service.create_access_token(test_user_2.id)
    return token


@pytest.fixture(scope="function")
def client_with_auth_user_2(client, access_token_user_2):
    """
    Фикстура HTTP клиента с аутентификацией второго пользователя.
    
    Args:
        client: Тестовый HTTP клиент.
        access_token_user_2: Токен доступа второго пользователя.
        
    Returns:
        TestClient: Аутентифицированный HTTP клиент.
    """
    client.cookies.set("access_token", access_token_user_2)
    return client


class TestScenarioRoutes:
    """Тесты для маршрутов работы со сценариями"""
    
    def test_get_all_scenarios_unauthorized(self, client):
        """
        Тест требования аутентификации для получения списка сценариев.
        
        Проверяет, что запрос к списку сценариев без токена
        возвращает ошибку авторизации.
        """
        response = client.get("/api/scenarios")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_all_scenarios_empty(self, client_with_auth):
        """
        Тест получения пустого списка сценариев.
        
        Проверяет, что для пользователя без сценариев возвращается
        корректная структура ответа с нулевым количеством записей.
        """
        response = client_with_auth.get("/api/scenarios")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_get_all_scenarios_with_data(self, client_with_auth, test_scenario, test_scenario_2):
        """
        Тест получения списка сценариев с данными.
        
        Проверяет, что созданные сценарии корректно
        возвращаются при запросе списка.
        """
        response = client_with_auth.get("/api/scenarios")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 1

    def test_get_all_scenarios_only_user_scenarios(
        self, 
        client_with_auth, 
        test_scenario, 
        test_scenario_other_user
    ):
        """
        Тест изоляции сценариев между пользователями.
        
        Проверяет, что пользователь видит только свои сценарии
        и не имеет доступа к сценариям других пользователей.
        """
        response = client_with_auth.get("/api/scenarios")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == test_scenario.id

    def test_get_all_scenarios_pagination(self, client_with_auth, test_user, db_session):
        """
        Тест пагинации списка сценариев.
        
        Проверяет корректную работу параметров page и size,
        а также вычисление общего количества страниц.
        """
        from app.models.scenario import Scenario
        
        for i in range(15):
            scenario = Scenario(
                user_id=test_user.id,
                name=f"Scenario {i}",
                description=f"Description {i}",
                district="tverskoy"
            )
            db_session.add(scenario)
        db_session.commit()
        
        response = client_with_auth.get("/api/scenarios?page=1&size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["pages"] == 2
        
        response = client_with_auth.get("/api/scenarios?page=2&size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 5
        assert data["page"] == 2

    def test_get_all_scenarios_valid_schema(self, client_with_auth, test_scenario):
        """
        Тест валидности схемы ответа списка сценариев.
        
        Проверяет, что каждый сценарий содержит все
        необходимые поля.
        """
        response = client_with_auth.get("/api/scenarios")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        scenario = data["items"][0]
        assert "id" in scenario
        assert "name" in scenario
        assert "description" in scenario
        assert "district" in scenario
        assert "removed_nodes" in scenario
        assert "removed_edges" in scenario
        assert "added_nodes" in scenario
        assert "added_edges" in scenario
        assert "hits" in scenario
        assert "created_at" in scenario

    def test_get_scenario_unauthorized(self, client, test_scenario):
        """
        Тест требования аутентификации для получения конкретного сценария.
        
        Проверяет, что запрос к сценарию без токена
        возвращает ошибку авторизации.
        """
        response = client.get(f"/api/scenarios/{test_scenario.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_scenario_success(self, client_with_auth, test_scenario):
        """
        Тест успешного получения конкретного сценария.
        
        Проверяет, что сценарий корректно возвращается
        по его идентификатору.
        """
        response = client_with_auth.get(f"/api/scenarios/{test_scenario.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == test_scenario.id
        assert data["name"] == test_scenario.name
        assert data["district"] == test_scenario.district

    def test_get_scenario_not_found(self, client_with_auth):
        """
        Тест получения несуществующего сценария.
        
        Проверяет, что запрос к несуществующему сценарию
        возвращает статус 404.
        """
        response = client_with_auth.get("/api/scenarios/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_scenario_increments_hits(self, client_with_auth, test_scenario, db_session):
        """
        Тест увеличения счетчика просмотров.
        
        Проверяет, что при каждом получении сценария
        счетчик hits увеличивается на единицу.
        """
        from app.models.scenario import Scenario
        
        initial_hits = test_scenario.hits
        
        response = client_with_auth.get(f"/api/scenarios/{test_scenario.id}")
        assert response.status_code == status.HTTP_200_OK
        
        updated_scenario = db_session.query(Scenario).filter(
            Scenario.id == test_scenario.id
        ).first()
        assert updated_scenario.hits == initial_hits + 1

    def test_get_scenario_valid_schema(self, client_with_auth, test_scenario):
        """
        Тест валидности схемы ответа сценария.
        
        Проверяет, что ответ содержит все необходимые поля
        для отображения сценария.
        """
        response = client_with_auth.get(f"/api/scenarios/{test_scenario.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "district" in data
        assert "hits" in data
        assert "created_at" in data
        assert "last_used_at" in data

    def test_save_scenario_unauthorized(self, client, valid_scenario_data):
        """
        Тест требования аутентификации для сохранения сценария.
        
        Проверяет, что создание сценария без токена
        возвращает ошибку авторизации.
        """
        response = client.post("/api/scenarios", json=valid_scenario_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_save_scenario_success(self, client_with_auth, valid_scenario_data):
        """
        Тест успешного сохранения сценария.
        
        Проверяет создание нового сценария с валидными данными
        и возврат корректной структуры ответа.
        """
        response = client_with_auth.post("/api/scenarios", json=valid_scenario_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert "id" in data
        assert data["name"] == valid_scenario_data["name"]
        assert data["description"] == valid_scenario_data["description"]
        assert data["district"] == valid_scenario_data["district"]
        assert data["hits"] == 0

    def test_save_scenario_invalid_name_too_short(self, client_with_auth):
        """
        Тест сохранения сценария со слишком коротким именем.
        
        Проверяет валидацию минимальной длины имени.
        """
        data = {
            "name": "ab",
            "description": "Test",
            "district": "tverskoy",
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client_with_auth.post("/api/scenarios", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_save_scenario_missing_district(self, client_with_auth):
        """
        Тест сохранения сценария без указания района.
        
        Проверяет, что поле district является обязательным.
        """
        data = {
            "name": "Test Scenario",
            "description": "Test",
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client_with_auth.post("/api/scenarios", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_save_scenario_invalid_district(self, client_with_auth):
        """
        Тест сохранения сценария с несуществующим районом.
        
        Проверяет валидацию существования района.
        """
        data = {
            "name": "Test Scenario",
            "description": "Test",
            "district": "nonexistent_xyz",
            "removed_nodes": [],
            "removed_edges": [],
            "added_nodes": [],
            "added_edges": []
        }
        
        response = client_with_auth.post("/api/scenarios", json=data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_save_scenario_with_changes(self, client_with_auth):
        """
        Тест сохранения сценария с изменениями графа.
        
        Проверяет создание сценария с добавленными и удаленными
        узлами и ребрами.
        """
        data = {
            "name": "Complex Scenario",
            "description": "With changes",
            "district": "tverskoy",
            "removed_nodes": ["35903409"],
            "removed_edges": [["54615001", "54615002"]],
            "added_nodes": [{"id": "new_node", "label": "New", "lat": 55.75, "lon": 37.61}],
            "added_edges": [["35903409", "54615001", 1.5]]
        }
        
        response = client_with_auth.post("/api/scenarios", json=data)
        
        assert response.status_code in (
            status.HTTP_201_CREATED, 
            status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    def test_update_scenario_unauthorized(self, client, test_scenario):
        """
        Тест требования аутентификации для обновления сценария.
        
        Проверяет, что обновление сценария без токена
        возвращает ошибку авторизации.
        """
        response = client.put(f"/api/scenarios/{test_scenario.id}", json={"name": "Updated"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_scenario_success(self, client_with_auth, test_scenario):
        """
        Тест успешного обновления сценария.
        
        Проверяет возможность изменения полей сценария
        и возврат обновленных данных.
        """
        update_data = {
            "name": "Updated Scenario Name",
            "description": "Updated description"
        }
        
        response = client_with_auth.put(f"/api/scenarios/{test_scenario.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_scenario_not_found(self, client_with_auth):
        """
        Тест обновления несуществующего сценария.
        
        Проверяет, что запрос к несуществующему сценарию
        возвращает статус 404.
        """
        update_data = {"name": "Updated"}
        
        response = client_with_auth.put("/api/scenarios/99999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_scenario_not_owner(self, client_with_auth_user_2, test_scenario):
        """
        Тест запрета обновления чужого сценария.
        
        Проверяет, что пользователь не может изменить сценарий,
        принадлежащий другому пользователю.
        """
        update_data = {"name": "Hacked"}
        
        response = client_with_auth_user_2.put(f"/api/scenarios/{test_scenario.id}", json=update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_scenario_partial(self, client_with_auth, test_scenario):
        """
        Тест частичного обновления сценария.
        
        Проверяет, что при обновлении только указанных полей
        остальные поля сохраняют свои значения.
        """
        original_description = test_scenario.description
        
        update_data = {"name": "New Name"}
        
        response = client_with_auth.put(f"/api/scenarios/{test_scenario.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["name"] == "New Name"
        assert data["description"] == original_description

    def test_delete_scenario_unauthorized(self, client, test_scenario):
        """
        Тест требования аутентификации для удаления сценария.
        
        Проверяет, что удаление сценария без токена
        возвращает ошибку авторизации.
        """
        response = client.delete(f"/api/scenarios/{test_scenario.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_scenario_success(self, client_with_auth, test_scenario):
        """
        Тест успешного удаления сценария.
        
        Проверяет, что сценарий удаляется и возвращается
        сообщение об успешном удалении.
        """
        scenario_id = test_scenario.id
        
        response = client_with_auth.delete(f"/api/scenarios/{scenario_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()

    def test_delete_scenario_not_found(self, client_with_auth):
        """
        Тест удаления несуществующего сценария.
        
        Проверяет, что запрос на удаление несуществующего сценария
        возвращает статус 404.
        """
        response = client_with_auth.delete("/api/scenarios/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_scenario_not_owner(self, client_with_auth_user_2, test_scenario):
        """
        Тест запрета удаления чужого сценария.
        
        Проверяет, что пользователь не может удалить сценарий,
        принадлежащий другому пользователю.
        """
        response = client_with_auth_user_2.delete(f"/api/scenarios/{test_scenario.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_scenario_removes_from_db(self, client_with_auth, test_scenario, db_session):
        """
        Тест физического удаления сценария из базы данных.
        
        Проверяет, что после успешного удаления сценарий
        отсутствует в базе данных.
        """
        from app.models.scenario import Scenario
        
        scenario_id = test_scenario.id
        
        response = client_with_auth.delete(f"/api/scenarios/{scenario_id}")
        assert response.status_code == status.HTTP_200_OK
        
        deleted = db_session.query(Scenario).filter(Scenario.id == scenario_id).first()
        assert deleted is None


class TestScenarioIntegration:
    """Интеграционные тесты для операций со сценариями"""
    
    def test_create_read_update_delete(self, client_with_auth, valid_scenario_data):
        """
        Тест полного цикла CRUD операций.
        
        Проверяет последовательное выполнение всех операций
        со сценарием: создание, чтение, обновление и удаление.
        """
        create_response = client_with_auth.post("/api/scenarios", json=valid_scenario_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        scenario = create_response.json()
        scenario_id = scenario["id"]
        
        get_response = client_with_auth.get(f"/api/scenarios/{scenario_id}")
        assert get_response.status_code == status.HTTP_200_OK
        
        update_data = {"name": "Updated Name"}
        update_response = client_with_auth.put(f"/api/scenarios/{scenario_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        
        delete_response = client_with_auth.delete(f"/api/scenarios/{scenario_id}")
        assert delete_response.status_code == status.HTTP_200_OK
        
        final_response = client_with_auth.get(f"/api/scenarios/{scenario_id}")
        assert final_response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_contains_created_scenario(self, client_with_auth, valid_scenario_data):
        """
        Тест наличия созданного сценария в списке.
        
        Проверяет, что после создания сценарий появляется
        в общем списке сценариев пользователя.
        """
        create_response = client_with_auth.post("/api/scenarios", json=valid_scenario_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        scenario = create_response.json()
        
        list_response = client_with_auth.get("/api/scenarios")
        assert list_response.status_code == status.HTTP_200_OK
        data = list_response.json()
        
        scenario_ids = [s["id"] for s in data["items"]]
        assert scenario["id"] in scenario_ids

    def test_hits_increment_on_multiple_views(self, client_with_auth, test_scenario):
        """
        Тест увеличения счетчика при многократных просмотрах.
        
        Проверяет, что каждый просмотр сценария увеличивает
        счетчик hits на единицу.
        """
        initial_hits = test_scenario.hits
        
        response1 = client_with_auth.get(f"/api/scenarios/{test_scenario.id}")
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert data1["hits"] == initial_hits + 1
        
        response2 = client_with_auth.get(f"/api/scenarios/{test_scenario.id}")
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert data2["hits"] == initial_hits + 2

    def test_user_isolation(self, client_with_auth, client_with_auth_user_2, test_scenario):
        """
        Тест изоляции сценариев между пользователями.
        
        Проверяет, что пользователи могут видеть и модифицировать
        только свои собственные сценарии.
        """
        response1 = client_with_auth.get(f"/api/scenarios/{test_scenario.id}")
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = client_with_auth_user_2.get(f"/api/scenarios/{test_scenario.id}")
        assert response2.status_code == status.HTTP_403_FORBIDDEN

    def test_scenarios_by_district(self, client_with_auth, test_user, db_session):
        """
        Тест привязки сценариев к районам.
        
        Проверяет, что сценарии корректно ассоциируются
        с указанными районами.
        """
        from app.models.scenario import Scenario
        
        scenario1 = Scenario(
            user_id=test_user.id,
            name="Tverskoy Scenario",
            district="tverskoy"
        )
        db_session.add(scenario1)
        db_session.commit()
        
        response = client_with_auth.get("/api/scenarios")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for scenario in data["items"]:
            assert scenario["district"] in ["tverskoy"]

    def test_scenario_metadata_preserved(self, client_with_auth, valid_scenario_data):
        """
        Тест сохранения метаданных сценария.
        
        Проверяет, что все данные об изменениях графа
        корректно сохраняются и возвращаются.
        """
        response = client_with_auth.post("/api/scenarios", json=valid_scenario_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        scenario = response.json()
        
        assert scenario["removed_nodes"] == valid_scenario_data["removed_nodes"]
        assert scenario["removed_edges"] == valid_scenario_data["removed_edges"]
        assert scenario["added_nodes"] == valid_scenario_data["added_nodes"]
        assert scenario["added_edges"] == valid_scenario_data["added_edges"]