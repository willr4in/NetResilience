import pytest
from fastapi import HTTPException, status
from app.schemas.user import UserResponse
from app.services.user_service import UserService


class TestUserService:
    """Тесты для сервиса управления пользователями"""
    
    def test_get_user_by_id_success(self, db_session, test_user):
        """
        Тест успешного получения пользователя по ID.
        
        Проверяет, что пользователь корректно возвращается
        по его идентификатору.
        """
        service = UserService(db_session)
        user = service.get_user_by_id(test_user.id)
        
        assert user.id == test_user.id
        assert user.email == "test@test.com"
        assert user.name == "Test"
        assert user.surname == "User"

    def test_get_user_by_id_not_found(self, db_session):
        """
        Тест получения несуществующего пользователя по ID.
        
        Проверяет, что запрос к несуществующему пользователю
        вызывает ошибку 404 с соответствующим сообщением.
        """
        service = UserService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_user_by_id(99999)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Пользователь не найден"

    def test_get_user_by_email_success(self, db_session, test_user):
        """
        Тест успешного получения пользователя по email.
        
        Проверяет, что пользователь корректно возвращается
        по его электронной почте.
        """
        service = UserService(db_session)
        user = service.get_user_by_email("test@test.com")
        
        assert user.email == "test@test.com"
        assert user.id == test_user.id
        assert user.name == "Test"
        assert user.surname == "User"

    def test_get_user_by_email_not_found(self, db_session):
        """
        Тест получения пользователя по несуществующему email.
        
        Проверяет, что запрос с несуществующим email
        вызывает ошибку 404 с соответствующим сообщением.
        """
        service = UserService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_user_by_email("nonexistent@test.com")
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Пользователь не найден"

    def test_get_all_users(self, db_session, test_user):
        """
        Тест получения списка всех пользователей.
        
        Проверяет, что возвращаемый список содержит
        хотя бы одного пользователя и включает тестового.
        """
        service = UserService(db_session)
        users = service.get_all_users()
        
        assert isinstance(users, list)
        assert len(users) > 0
        assert any(u.id == test_user.id for u in users)

    def test_get_all_users_returns_user_responses(self, db_session, test_user):
        """
        Тест типа возвращаемых объектов.
        
        Проверяет, что все элементы списка пользователей
        являются объектами UserResponse.
        """
        service = UserService(db_session)
        users = service.get_all_users()
        
        assert all(isinstance(u, UserResponse) for u in users)

    def test_delete_user_success(self, db_session, test_user):
        """
        Тест успешного удаления пользователя.
        
        Проверяет, что пользователь удаляется и возвращается
        сообщение об успешном удалении.
        """
        service = UserService(db_session)
        result = service.delete_user(test_user.id)
        
        assert result["message"] == f"User {test_user.email} deleted successfully"

    def test_delete_nonexistent_user(self, db_session):
        """
        Тест удаления несуществующего пользователя.
        
        Проверяет, что попытка удалить несуществующего
        пользователя вызывает ошибку 404.
        """
        service = UserService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_user(99999)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Пользователь не найден"

    def test_delete_user_removes_from_db(self, db_session, test_user):
        """
        Тест физического удаления пользователя из базы данных.
        
        Проверяет, что после успешного удаления пользователь
        отсутствует в базе данных.
        """
        service = UserService(db_session)
        user_id = test_user.id
        
        service.delete_user(user_id)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_user_by_id(user_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_response_schema(self, db_session, test_user):
        """
        Тест наличия всех полей в схеме UserResponse.
        
        Проверяет, что ответ содержит все необходимые
        поля для представления пользователя.
        """
        service = UserService(db_session)
        user = service.get_user_by_id(test_user.id)
        
        assert hasattr(user, "id")
        assert hasattr(user, "name")
        assert hasattr(user, "surname")
        assert hasattr(user, "email")
        assert hasattr(user, "created_at")
        
        assert isinstance(user.id, int)
        assert isinstance(user.name, str)
        assert isinstance(user.surname, str)
        assert isinstance(user.email, str)

    def test_get_user_response_returns_correct_data(self, db_session, test_user):
        """
        Тест корректности возвращаемых данных.
        
        Проверяет, что все поля UserResponse соответствуют
        данным тестового пользователя.
        """
        service = UserService(db_session)
        user = service.get_user_by_id(test_user.id)
        
        assert user.id == test_user.id
        assert user.name == test_user.name
        assert user.surname == test_user.surname
        assert user.email == test_user.email
        assert user.created_at == test_user.created_at

    def test_get_user_by_id_returns_user_response(self, db_session, test_user):
        """
        Тест типа возвращаемого объекта при получении по ID.
        
        Проверяет, что метод get_user_by_id возвращает
        объект UserResponse.
        """
        service = UserService(db_session)
        user = service.get_user_by_id(test_user.id)
        
        assert isinstance(user, UserResponse)

    def test_get_user_by_email_returns_user_response(self, db_session, test_user):
        """
        Тест типа возвращаемого объекта при получении по email.
        
        Проверяет, что метод get_user_by_email возвращает
        объект UserResponse.
        """
        service = UserService(db_session)
        user = service.get_user_by_email("test@test.com")
        
        assert isinstance(user, UserResponse)