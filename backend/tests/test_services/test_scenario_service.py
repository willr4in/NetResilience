import pytest
from fastapi import HTTPException, status
from app.services.scenario_service import ScenarioService
from app.schemas.scenario import ScenarioCreate, ScenarioUpdate
from app.schemas.history import ActionType


class TestScenarioService:
    """Тесты для сервиса управления сценариями"""
    
    def test_save_scenario_success(self, db_session, test_user):
        """
        Тест успешного сохранения сценария.
        
        Проверяет, что сценарий сохраняется с корректными
        данными и привязывается к пользователю.
        """
        service = ScenarioService(db_session)
        scenario_data = ScenarioCreate(
            name="Save Test Scenario",
            description="Test description",
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        scenario = service.save_scenario(test_user.id, scenario_data)
        assert scenario.name == "Save Test Scenario"
        assert scenario.user_id == test_user.id
        assert scenario.district == "tverskoy"

    def test_save_scenario_invalid_district(self, db_session, test_user):
        """
        Тест сохранения сценария с несуществующим районом.
        
        Проверяет, что попытка сохранить сценарий
        с невалидным районом вызывает ошибку 404.
        """
        service = ScenarioService(db_session)
        scenario_data = ScenarioCreate(
            name="Invalid District Scenario",
            description="Test",
            district="invalid_district",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.save_scenario(test_user.id, scenario_data)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_save_scenario_creates_history_record(self, db_session, test_user):
        """
        Тест создания записи истории при сохранении сценария.
        
        Проверяет, что при сохранении сценария автоматически
        создается запись в истории с действием SAVE.
        """
        service = ScenarioService(db_session)
        scenario_data = ScenarioCreate(
            name="History Test Scenario",
            description="Test",
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        service.save_scenario(test_user.id, scenario_data)
        history, total = service.history_repository.get_history_by_user_id(test_user.id)
        
        assert total > 0
        assert any(h.action == ActionType.SAVE for h in history)

    def test_save_scenario_metrics_calculation(self, db_session, test_user):
        """
        Тест расчета метрик при сохранении сценария.
        
        Проверяет, что при сохранении сценария
        рассчитываются все метрики центральности.
        """
        service = ScenarioService(db_session)
        scenario_data = ScenarioCreate(
            name="Metrics Test",
            description="Test",
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        scenario = service.save_scenario(test_user.id, scenario_data)
        assert scenario.metrics is not None
        assert hasattr(scenario.metrics, "betweenness")
        assert hasattr(scenario.metrics, "closeness")
        assert hasattr(scenario.metrics, "degree")
        assert hasattr(scenario.metrics, "critical_nodes")
        assert scenario.metrics.betweenness is not None
        assert len(scenario.metrics.betweenness) > 0

    def test_save_scenario_duplicate_name_allowed(self, db_session, test_user, test_scenario):
        """
        Тест сохранения сценария с дублирующимся именем.
        
        Проверяет, что система разрешает создание
        сценариев с одинаковыми именами.
        """
        service = ScenarioService(db_session)
        scenario_data = ScenarioCreate(
            name=test_scenario.name,
            description="Duplicate name scenario",
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        scenario = service.save_scenario(test_user.id, scenario_data)
        assert scenario.id != test_scenario.id
        assert scenario.name == test_scenario.name

    def test_save_scenario_with_graph_modifications(self, db_session, test_user):
        """
        Тест сохранения сценария с модификациями графа.
        
        Проверяет, что сценарий с удалением реальных узлов
        корректно сохраняется.
        """
        from app.services.graph_service import load_graph
        
        _, G = load_graph("tverskoy")
        nodes = list(G.nodes())
        
        if not nodes:
            pytest.skip("Graph has no nodes")
        
        real_node = nodes[0]
        
        service = ScenarioService(db_session)
        scenario_data = ScenarioCreate(
            name="Modified Scenario",
            description="With real node removal",
            district="tverskoy",
            removed_nodes=[real_node],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        scenario = service.save_scenario(test_user.id, scenario_data)
        assert scenario.id is not None
        assert scenario.metrics is not None

    def test_save_scenario_with_nonexistent_node(self, db_session, test_user):
        """
        Тест сохранения сценария с несуществующим узлом.
        
        Проверяет, что сценарий с указанием несуществующего
        узла все равно сохраняется корректно.
        """
        service = ScenarioService(db_session)
        scenario_data = ScenarioCreate(
            name="Nonexistent Node Test",
            description="Test with node that doesn't exist",
            district="tverskoy",
            removed_nodes=["nonexistent_node_12345"],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        scenario = service.save_scenario(test_user.id, scenario_data)
        assert scenario.id is not None

    def test_get_scenario_success(self, db_session, test_user, test_scenario):
        """
        Тест успешного получения сценария.
        
        Проверяет, что сценарий корректно возвращается
        по его идентификатору.
        """
        service = ScenarioService(db_session)
        scenario = service.get_scenario(test_scenario.id, test_user.id)
        
        assert scenario.id == test_scenario.id
        assert scenario.name == test_scenario.name

    def test_get_scenario_not_found(self, db_session, test_user):
        """
        Тест получения несуществующего сценария.
        
        Проверяет, что запрос к несуществующему сценарию
        вызывает ошибку 404.
        """
        service = ScenarioService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_scenario(99999, test_user.id)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_get_scenario_increments_hits(self, db_session, test_user, test_scenario):
        """
        Тест увеличения счетчика просмотров.
        
        Проверяет, что при каждом получении сценария
        счетчик hits увеличивается на единицу.
        """
        service = ScenarioService(db_session)
        initial_hits = test_scenario.hits
        
        service.get_scenario(test_scenario.id, test_user.id)
        
        updated_scenario = service.scenario_repository.get_scenario_by_id(test_scenario.id)
        assert updated_scenario.hits == initial_hits + 1

    def test_get_scenario_creates_view_history(self, db_session, test_user, test_scenario):
        """
        Тест создания записи истории при просмотре сценария.
        
        Проверяет, что при получении сценария автоматически
        создается запись в истории с действием VIEW.
        """
        service = ScenarioService(db_session)
        service.get_scenario(test_scenario.id, test_user.id)
        
        history, total = service.history_repository.get_history_by_user_id(test_user.id)
        assert total > 0
        assert any(h.action == ActionType.VIEW for h in history)

    def test_get_user_scenarios_pagination(self, db_session, test_user):
        """
        Тест пагинации списка сценариев пользователя.
        
        Проверяет корректную работу пагинации
        при получении списка сценариев.
        """
        service = ScenarioService(db_session)
        
        for i in range(15):
            scenario_data = ScenarioCreate(
                name=f"Scenario {i}",
                description="Test",
                district="tverskoy",
                removed_nodes=[],
                removed_edges=[],
                added_nodes=[],
                added_edges=[]
            )
            service.save_scenario(test_user.id, scenario_data)
        
        result = service.get_user_scenarios(test_user.id, page=1, size=10)
        assert len(result.items) == 10
        assert result.total >= 15
        assert result.pages >= 2

    def test_get_user_scenarios_correct_page(self, db_session, test_user):
        """
        Тест получения конкретной страницы сценариев.
        
        Проверяет, что разные страницы возвращают
        разные наборы сценариев.
        """
        service = ScenarioService(db_session)
        
        for i in range(15):
            scenario_data = ScenarioCreate(
                name=f"Scenario {i}",
                description="Test",
                district="tverskoy",
                removed_nodes=[],
                removed_edges=[],
                added_nodes=[],
                added_edges=[]
            )
            service.save_scenario(test_user.id, scenario_data)
        
        page1 = service.get_user_scenarios(test_user.id, page=1, size=10)
        page2 = service.get_user_scenarios(test_user.id, page=2, size=10)
        
        assert page1.page == 1
        assert page2.page == 2
        assert page1.items[0].id != page2.items[0].id

    def test_get_user_scenarios_empty_user(self, db_session):
        """
        Тест получения сценариев для пользователя без сценариев.
        
        Проверяет, что для пользователя без сценариев
        возвращается пустой список.
        """
        from app.services.auth_service import AuthService
        from app.schemas.auth import RegisterRequest
        
        auth_service = AuthService(db_session)
        user = auth_service.register(RegisterRequest(
            name="Empty",
            surname="User",
            email="empty_scenario@test.com",
            password="password123"
        ))
        db_session.commit()
        
        service = ScenarioService(db_session)
        result = service.get_user_scenarios(user.id)
        
        assert result.total == 0
        assert len(result.items) == 0
        assert result.pages == 1

    def test_get_user_scenarios_returns_list_schema(self, db_session, test_user, test_scenario):
        """
        Тест схемы ответа списка сценариев.
        
        Проверяет, что возвращаемый объект имеет
        все необходимые поля для пагинации.
        """
        service = ScenarioService(db_session)
        result = service.get_user_scenarios(test_user.id)
        
        assert hasattr(result, "items")
        assert hasattr(result, "total")
        assert hasattr(result, "page")
        assert hasattr(result, "size")
        assert hasattr(result, "pages")

    def test_update_scenario_success(self, db_session, test_user, test_scenario):
        """
        Тест успешного обновления сценария.
        
        Проверяет, что сценарий корректно обновляется
        с новыми данными.
        """
        service = ScenarioService(db_session)
        update_data = ScenarioUpdate(
            name="Updated Scenario Name",
            description="Updated description"
        )
        
        updated = service.update_scenario(test_scenario.id, test_user.id, update_data)
        assert updated.name == "Updated Scenario Name"
        assert updated.description == "Updated description"

    def test_update_scenario_partial_update(self, db_session, test_user, test_scenario):
        """
        Тест частичного обновления сценария.
        
        Проверяет, что при обновлении только указанных полей
        остальные поля сохраняют свои значения.
        """
        service = ScenarioService(db_session)
        original_description = test_scenario.description
        update_data = ScenarioUpdate(name="New Name Only")
        
        updated = service.update_scenario(test_scenario.id, test_user.id, update_data)
        assert updated.name == "New Name Only"
        assert updated.description == original_description

    def test_update_scenario_empty_update(self, db_session, test_user, test_scenario):
        """
        Тест обновления сценария пустыми данными.
        
        Проверяет, что обновление без изменений
        не меняет данные сценария.
        """
        service = ScenarioService(db_session)
        update_data = ScenarioUpdate()
        
        updated = service.update_scenario(test_scenario.id, test_user.id, update_data)
        assert updated.name == test_scenario.name
        assert updated.description == test_scenario.description

    def test_update_scenario_not_found(self, db_session, test_user):
        """
        Тест обновления несуществующего сценария.
        
        Проверяет, что попытка обновить несуществующий
        сценарий вызывает ошибку 404.
        """
        service = ScenarioService(db_session)
        update_data = ScenarioUpdate(name="New Name")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_scenario(99999, test_user.id, update_data)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_update_scenario_permission_denied(self, db_session, test_user, test_scenario):
        """
        Тест запрета обновления чужого сценария.
        
        Проверяет, что пользователь не может обновить
        сценарий, принадлежащий другому пользователю.
        """
        from app.services.auth_service import AuthService
        from app.schemas.auth import RegisterRequest
        
        auth_service = AuthService(db_session)
        other_user = auth_service.register(RegisterRequest(
            name="Other",
            surname="User",
            email="other_update@test.com",
            password="password123"
        ))
        db_session.commit()
        
        service = ScenarioService(db_session)
        update_data = ScenarioUpdate(name="Hacked Name")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_scenario(test_scenario.id, other_user.id, update_data)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_scenario_success(self, db_session, test_user, test_scenario):
        """
        Тест успешного удаления сценария.
        
        Проверяет, что сценарий удаляется и после удаления
        его невозможно получить.
        """
        service = ScenarioService(db_session)
        scenario_id = test_scenario.id
        
        result = service.delete_scenario(scenario_id, test_user.id)
        assert result["message"] == f"Scenario '{test_scenario.name}' deleted successfully"
        
        with pytest.raises(HTTPException):
            service.get_scenario(scenario_id, test_user.id)

    def test_delete_scenario_not_found(self, db_session, test_user):
        """
        Тест удаления несуществующего сценария.
        
        Проверяет, что попытка удалить несуществующий
        сценарий вызывает ошибку 404.
        """
        service = ScenarioService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_scenario(99999, test_user.id)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_scenario_permission_denied(self, db_session, test_user, test_scenario):
        """
        Тест запрета удаления чужого сценария.
        
        Проверяет, что пользователь не может удалить
        сценарий, принадлежащий другому пользователю.
        """
        from app.services.auth_service import AuthService
        from app.schemas.auth import RegisterRequest
        
        auth_service = AuthService(db_session)
        other_user = auth_service.register(RegisterRequest(
            name="Other",
            surname="User",
            email="other_delete@test.com",
            password="password123"
        ))
        db_session.commit()
        
        service = ScenarioService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_scenario(test_scenario.id, other_user.id)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_scenario_creates_delete_history(self, db_session, test_user, test_scenario):
        """
        Тест создания записи истории при удалении сценария.
        
        Проверяет, что при удалении сценария автоматически
        создается запись в истории с действием DELETE.
        """
        service = ScenarioService(db_session)
        service.delete_scenario(test_scenario.id, test_user.id)
        
        history, total = service.history_repository.get_history_by_user_id(test_user.id)
        assert total > 0
        assert any(h.action == ActionType.DELETE for h in history)

    def test_scenario_response_includes_metrics(self, db_session, test_user):
        """
        Тест наличия метрик в ответе сценария.
        
        Проверяет, что сохраненный сценарий содержит
        все рассчитанные метрики центральности.
        """
        service = ScenarioService(db_session)
        scenario_data = ScenarioCreate(
            name="Metrics Response Test",
            description="Test",
            district="tverskoy",
            removed_nodes=[],
            removed_edges=[],
            added_nodes=[],
            added_edges=[]
        )
        
        scenario = service.save_scenario(test_user.id, scenario_data)
        assert scenario.metrics is not None
        assert hasattr(scenario.metrics, "betweenness")
        assert hasattr(scenario.metrics, "closeness")
        assert hasattr(scenario.metrics, "degree")
        assert hasattr(scenario.metrics, "critical_nodes")
        assert scenario.metrics.betweenness is not None
        assert scenario.metrics.closeness is not None
        assert scenario.metrics.degree is not None
        assert scenario.metrics.critical_nodes is not None