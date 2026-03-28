import pytest
from fastapi import HTTPException, status
from app.services.history_service import HistoryService
from app.schemas.history import ActionType, HistoryList, HistoryResponse


class TestHistoryService:
    """Тесты для сервиса истории действий"""
    
    def test_get_user_history_success(self, db_session, test_user):
        """
        Тест успешного получения истории пользователя.
        
        Проверяет, что метод возвращает объект HistoryList
        с корректной структурой.
        """
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id)
        
        assert isinstance(result, HistoryList)
        assert hasattr(result, "items")
        assert hasattr(result, "total")
        assert hasattr(result, "page")
        assert hasattr(result, "size")
        assert hasattr(result, "pages")

    def test_get_user_history_empty(self, db_session, test_user):
        """
        Тест получения истории для пользователя без записей.
        
        Проверяет, что для пользователя без истории
        возвращается пустой список.
        """
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id)
        
        assert result.total == 0
        assert len(result.items) == 0
        assert result.pages == 1

    def test_get_user_history_with_records(self, db_session, test_user, test_scenario):
        """
        Тест получения истории с существующими записями.
        
        Проверяет, что созданные записи истории
        корректно возвращаются при запросе.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.CALCULATE,
                details={"metric": "betweenness"},
                calculation_time_ms=150.5
            )
        )
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.SAVE,
                details={"scenario_name": "Test"}
            )
        )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id)
        
        assert result.total == 2
        assert len(result.items) == 2

    def test_get_user_history_pagination_first_page(self, db_session, test_user, test_scenario):
        """
        Тест пагинации - первая страница.
        
        Проверяет корректную работу пагинации
        при запросе первой страницы.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        for i in range(15):
            history_repo.create_history(
                user_id=test_user.id,
                history_data=HistoryCreate(
                    scenario_id=test_scenario.id,
                    action=ActionType.VIEW,
                    details={"item": f"Item {i}"}
                )
            )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id, page=1, size=10)
        
        assert len(result.items) == 10
        assert result.page == 1
        assert result.size == 10
        assert result.total == 15
        assert result.pages == 2

    def test_get_user_history_pagination_second_page(self, db_session, test_user, test_scenario):
        """
        Тест пагинации - вторая страница.
        
        Проверяет корректную работу пагинации
        при запросе второй страницы.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        for i in range(15):
            history_repo.create_history(
                user_id=test_user.id,
                history_data=HistoryCreate(
                    scenario_id=test_scenario.id,
                    action=ActionType.VIEW,
                    details={"item": f"Item {i}"}
                )
            )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id, page=2, size=10)
        
        assert len(result.items) == 5
        assert result.page == 2
        assert result.total == 15
        assert result.pages == 2

    def test_get_user_history_isolated_per_user(self, db_session, test_user, test_scenario):
        """
        Тест изоляции истории между пользователями.
        
        Проверяет, что каждый пользователь видит
        только свои записи истории.
        """
        from app.services.auth_service import AuthService
        from app.schemas.auth import RegisterRequest
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        auth_service = AuthService(db_session)
        user2 = auth_service.register(RegisterRequest(
            name="User",
            surname="Two",
            email="user2_history@test.com",
            password="password123"
        ))
        db_session.commit()
        
        history_repo = HistoryRepository(db_session)
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.CALCULATE,
                details={"metric": "betweenness"}
            )
        )
        history_repo.create_history(
            user_id=user2.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.SAVE,
                details={"scenario": "User2 scenario"}
            )
        )
        
        service = HistoryService(db_session)
        result1 = service.get_user_history(test_user.id)
        result2 = service.get_user_history(user2.id)
        
        assert result1.total == 1
        assert result2.total == 1
        assert result1.items[0].action == ActionType.CALCULATE
        assert result2.items[0].action == ActionType.SAVE

    def test_get_user_history_nonexistent_user(self, db_session):
        """
        Тест получения истории для несуществующего пользователя.
        
        Проверяет, что запрос для несуществующего
        пользователя возвращает пустую историю.
        """
        service = HistoryService(db_session)
        result = service.get_user_history(99999)
        
        assert result.total == 0
        assert len(result.items) == 0

    def test_get_user_history_includes_scenario_name(self, db_session, test_user, test_scenario):
        """
        Тест включения имени сценария в историю.
        
        Проверяет, что в записи истории присутствует
        имя связанного сценария.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.VIEW,
                details={}
            )
        )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id)
        
        assert result.items[0].scenario_name == test_scenario.name

    def test_get_user_history_without_scenario(self, db_session, test_user):
        """
        Тест записи истории без привязки к сценарию.
        
        Проверяет, что записи без сценария
        корректно обрабатываются.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=None,
                action=ActionType.CALCULATE,
                details={"metric": "test"}
            )
        )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id)
        
        assert result.items[0].scenario_id is None
        assert result.items[0].scenario_name is None

    def test_get_scenario_history_success(self, db_session, test_user, test_scenario):
        """
        Тест успешного получения истории сценария.
        
        Проверяет, что история конкретного сценария
        корректно возвращается.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.VIEW,
                details={}
            )
        )
        
        service = HistoryService(db_session)
        result = service.get_scenario_history(test_scenario.id)
        
        assert isinstance(result, HistoryList)
        assert result.total == 1

    def test_get_scenario_history_empty(self, db_session, test_scenario):
        """
        Тест получения истории сценария без записей.
        
        Проверяет, что для сценария без истории
        возвращается пустой список.
        """
        service = HistoryService(db_session)
        result = service.get_scenario_history(test_scenario.id)
        
        assert result.total == 0
        assert len(result.items) == 0

    def test_get_scenario_history_pagination(self, db_session, test_user, test_scenario):
        """
        Тест пагинации истории сценария.
        
        Проверяет корректную работу пагинации
        для истории конкретного сценария.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        for i in range(25):
            history_repo.create_history(
                user_id=test_user.id,
                history_data=HistoryCreate(
                    scenario_id=test_scenario.id,
                    action=ActionType.VIEW,
                    details={"item": f"Item {i}"}
                )
            )
        
        service = HistoryService(db_session)
        result1 = service.get_scenario_history(test_scenario.id, page=1, size=10)
        result2 = service.get_scenario_history(test_scenario.id, page=2, size=10)
        result3 = service.get_scenario_history(test_scenario.id, page=3, size=10)
        
        assert len(result1.items) == 10
        assert len(result2.items) == 10
        assert len(result3.items) == 5
        assert result1.total == 25

    def test_get_scenario_history_only_specific_scenario(self, db_session, test_user, test_scenario):
        """
        Тест фильтрации истории по конкретному сценарию.
        
        Проверяет, что при запросе истории сценария
        возвращаются только записи этого сценария.
        """
        from app.repositories.scenario_repository import ScenarioRepository
        from app.schemas.scenario import ScenarioCreate
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        scenario_repo = ScenarioRepository(db_session)
        scenario2 = scenario_repo.create_scenario(
            user_id=test_user.id,
            scenario_data=ScenarioCreate(
                name="Scenario 2",
                description="Test",
                district="tverskoy",
                removed_nodes=[],
                removed_edges=[],
                added_nodes=[],
                added_edges=[]
            )
        )
        
        history_repo = HistoryRepository(db_session)
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.VIEW,
                details={}
            )
        )
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=scenario2.id,
                action=ActionType.VIEW,
                details={}
            )
        )
        
        service = HistoryService(db_session)
        result = service.get_scenario_history(test_scenario.id)
        
        assert result.total == 1
        assert result.items[0].scenario_id == test_scenario.id

    def test_delete_history_record_success(self, db_session, test_user, test_scenario):
        """
        Тест успешного удаления записи истории.
        
        Проверяет, что запись истории корректно удаляется
        и возвращается сообщение об успехе.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history = history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.VIEW,
                details={}
            )
        )
        
        service = HistoryService(db_session)
        result = service.delete_history_record(history.id)
        
        assert "deleted successfully" in result["message"]

    def test_delete_history_record_not_found(self, db_session):
        """
        Тест удаления несуществующей записи.
        
        Проверяет, что попытка удалить несуществующую
        запись вызывает ошибку 404.
        """
        service = HistoryService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_history_record(99999)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail

    def test_delete_history_record_actually_removes(self, db_session, test_user, test_scenario):
        """
        Тест физического удаления записи из базы данных.
        
        Проверяет, что после удаления запись
        отсутствует в базе данных.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history = history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.VIEW,
                details={}
            )
        )
        history_id = history.id
        
        service = HistoryService(db_session)
        service.delete_history_record(history_id)
        
        result = service.get_user_history(test_user.id)
        assert result.total == 0

    def test_delete_history_record_only_deletes_one(self, db_session, test_user, test_scenario):
        """
        Тест удаления только указанной записи.
        
        Проверяет, что при удалении одной записи
        остальные записи сохраняются.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history1 = history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.VIEW,
                details={"first": True}
            )
        )
        history2 = history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.SAVE,
                details={"second": True}
            )
        )
        
        service = HistoryService(db_session)
        service.delete_history_record(history1.id)
        
        result = service.get_user_history(test_user.id)
        assert result.total == 1
        assert result.items[0].action == ActionType.SAVE

    def test_history_with_calculation_time(self, db_session, test_user):
        """
        Тест записи истории со временем расчета.
        
        Проверяет, что поле calculation_time_ms
        корректно сохраняется и возвращается.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=None,
                action=ActionType.CALCULATE,
                details={"metric": "betweenness"},
                calculation_time_ms=250.75
            )
        )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id)
        
        assert result.items[0].calculation_time_ms == 250.75

    def test_history_response_schema_validation(self, db_session, test_user, test_scenario):
        """
        Тест валидации схемы ответа истории.
        
        Проверяет, что возвращаемые объекты истории
        соответствуют схеме HistoryResponse.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        history_repo.create_history(
            user_id=test_user.id,
            history_data=HistoryCreate(
                scenario_id=test_scenario.id,
                action=ActionType.SAVE,
                details={"test": "data"},
                calculation_time_ms=100.0
            )
        )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id)
        
        history_item = result.items[0]
        assert isinstance(history_item, HistoryResponse)
        assert hasattr(history_item, "id")
        assert hasattr(history_item, "user_id")
        assert hasattr(history_item, "scenario_id")
        assert hasattr(history_item, "action")
        assert hasattr(history_item, "details")
        assert hasattr(history_item, "created_at")

    def test_history_all_action_types(self, db_session, test_user, test_scenario):
        """
        Тест всех типов действий в истории.
        
        Проверяет, что все возможные типы действий
        корректно сохраняются и возвращаются.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        
        for action_type in ActionType:
            history_repo.create_history(
                user_id=test_user.id,
                history_data=HistoryCreate(
                    scenario_id=test_scenario.id,
                    action=action_type,
                    details={"type": action_type.value}
                )
            )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id, size=20)
        
        assert result.total == 4
        actions = {item.action for item in result.items}
        assert len(actions) == 4

    def test_history_pages_calculation(self, db_session, test_user, test_scenario):
        """
        Тест корректного расчета количества страниц.
        
        Проверяет, что количество страниц вычисляется
        правильно на основе общего количества записей.
        """
        from app.repositories.history_repository import HistoryRepository
        from app.schemas.history import HistoryCreate
        
        history_repo = HistoryRepository(db_session)
        for i in range(23):
            history_repo.create_history(
                user_id=test_user.id,
                history_data=HistoryCreate(
                    scenario_id=test_scenario.id,
                    action=ActionType.VIEW,
                    details={"item": i}
                )
            )
        
        service = HistoryService(db_session)
        result = service.get_user_history(test_user.id, page=1, size=10)
        
        assert result.total == 23
        assert result.pages == 3
        assert result.size == 10
        assert result.page == 1