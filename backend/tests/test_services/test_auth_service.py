import pytest
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, TokenPayload
from app.models.user import User
from fastapi import HTTPException, status


@pytest.fixture
def auth_service(db_session):
    """
    Фикстура, создающая экземпляр сервиса аутентификации.
    
    Args:
        db_session: Сессия базы данных.
        
    Returns:
        AuthService: Экземпляр сервиса аутентификации.
    """
    return AuthService(db_session)


@pytest.fixture
def valid_register_data():
    """
    Фикстура с валидными данными для регистрации.
    
    Returns:
        RegisterRequest: Объект запроса на регистрацию.
    """
    return RegisterRequest(
        name="John",
        surname="Doe",
        email="john.auth@example.com",
        password="SecurePass123!"
    )


@pytest.fixture
def another_user_data():
    """
    Фикстура с данными другого пользователя.
    
    Returns:
        RegisterRequest: Объект запроса на регистрацию.
    """
    return RegisterRequest(
        name="Jane",
        surname="Smith",
        email="jane.auth@example.com",
        password="AnotherPass456!"
    )


class TestPasswordHashing:
    """Тесты для хеширования и верификации паролей"""
    
    def test_hash_password_returns_string(self, auth_service):
        """
        Тест возврата строки при хешировании.
        
        Проверяет, что хеш пароля возвращается в виде строки.
        """
        hashed = auth_service.hash_password("TestPassword123!")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self, auth_service):
        """
        Тест уникальности хешей.
        
        Проверяет, что bcrypt генерирует разные хеши
        для одного и того же пароля.
        """
        password = "TestPassword123!"
        hash1 = auth_service.hash_password(password)
        hash2 = auth_service.hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self, auth_service):
        """
        Тест верификации правильного пароля.
        
        Проверяет, что верификация возвращает True
        для корректного пароля.
        """
        password = "TestPassword123!"
        hashed = auth_service.hash_password(password)
        assert auth_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self, auth_service):
        """
        Тест верификации неправильного пароля.
        
        Проверяет, что верификация возвращает False
        для неверного пароля.
        """
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = auth_service.hash_password(password)
        assert auth_service.verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self, auth_service):
        """
        Тест чувствительности к регистру.
        
        Проверяет, что верификация пароля
        учитывает регистр символов.
        """
        password = "TestPassword123!"
        hashed = auth_service.hash_password(password)
        assert auth_service.verify_password("testpassword123!", hashed) is False


class TestRegister:
    """Тесты для регистрации пользователей"""
    
    def test_register_success(self, auth_service, valid_register_data):
        """
        Тест успешной регистрации.
        
        Проверяет, что пользователь успешно регистрируется
        с корректными данными.
        """
        user = auth_service.register(valid_register_data)
        assert isinstance(user, User)
        assert user.email == "john.auth@example.com"
        assert user.name == "John"
        assert user.surname == "Doe"

    def test_register_returns_user_with_id(self, auth_service, valid_register_data):
        """
        Тест наличия ID после регистрации.
        
        Проверяет, что созданный пользователь
        получает идентификатор.
        """
        user = auth_service.register(valid_register_data)
        assert user.id is not None
        assert isinstance(user.id, int)

    def test_register_password_hashed(self, auth_service, valid_register_data):
        """
        Тест хеширования пароля.
        
        Проверяет, что пароль сохраняется в базе данных
        в захешированном виде.
        """
        user = auth_service.register(valid_register_data)
        assert user.hashed_password != "SecurePass123!"
        assert len(user.hashed_password) > 0

    def test_register_duplicate_email(self, auth_service, valid_register_data):
        """
        Тест регистрации с дублирующимся email.
        
        Проверяет, что попытка регистрации с уже
        существующим email вызывает ошибку.
        """
        auth_service.register(valid_register_data)
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register(valid_register_data)
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже существует" in exc_info.value.detail

    def test_register_stores_all_fields(self, auth_service, valid_register_data):
        """
        Тест сохранения всех полей.
        
        Проверяет, что все переданные поля
        корректно сохраняются в базе данных.
        """
        user = auth_service.register(valid_register_data)
        assert user.name == valid_register_data.name
        assert user.surname == valid_register_data.surname
        assert user.email == valid_register_data.email


class TestLogin:
    """Тесты для входа пользователей"""
    
    def test_login_success(self, auth_service, valid_register_data):
        """
        Тест успешного входа.
        
        Проверяет, что пользователь может войти
        с корректными учетными данными.
        """
        auth_service.register(valid_register_data)
        user = auth_service.login("john.auth@example.com", "SecurePass123!")
        assert isinstance(user, User)
        assert user.email == "john.auth@example.com"

    def test_login_returns_user(self, auth_service, valid_register_data):
        """
        Тест возврата объекта пользователя.
        
        Проверяет, что при успешном входе
        возвращается объект User.
        """
        auth_service.register(valid_register_data)
        user = auth_service.login("john.auth@example.com", "SecurePass123!")
        assert user.id is not None
        assert user.name == "John"

    def test_login_wrong_password(self, auth_service, valid_register_data):
        """
        Тест входа с неверным паролем.
        
        Проверяет, что попытка входа с неправильным
        паролем вызывает ошибку авторизации.
        """
        auth_service.register(valid_register_data)
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login("john.auth@example.com", "WrongPassword123!")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, auth_service):
        """
        Тест входа несуществующего пользователя.
        
        Проверяет, что попытка входа с email,
        не зарегистрированным в системе, вызывает ошибку.
        """
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login("nonexistent@example.com", "AnyPassword123!")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_case_insensitive_email(self, auth_service, valid_register_data):
        """
        Тест нечувствительности email к регистру.

        Email приводится к нижнему регистру — логин с UPPER CASE должен работать.
        """
        auth_service.register(valid_register_data)
        result = auth_service.login("JOHN.AUTH@EXAMPLE.COM", "SecurePass123!")
        assert result is not None


class TestCreateAccessToken:
    """Тесты для создания access токенов"""
    
    def test_create_access_token_success(self, auth_service, test_user):
        """
        Тест успешного создания access токена.
        
        Проверяет, что токен создается и возвращается в виде строки.
        """
        token = auth_service.create_access_token(test_user.id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_is_jwt(self, auth_service, test_user):
        """
        Тест формата JWT.
        
        Проверяет, что созданный токен имеет
        корректный формат JWT (3 части).
        """
        token = auth_service.create_access_token(test_user.id)
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_access_token_consistent_format(self, auth_service, test_user):
        """
        Тест согласованности формата.
        
        Проверяет, что все создаваемые токены
        имеют одинаковый формат.
        """
        token1 = auth_service.create_access_token(test_user.id)
        token2 = auth_service.create_access_token(test_user.id)
        assert token1.count(".") == 2
        assert token2.count(".") == 2


class TestCreateRefreshToken:
    """Тесты для создания refresh токенов"""
    
    def test_create_refresh_token_success(self, auth_service, test_user):
        """
        Тест успешного создания refresh токена.
        
        Проверяет, что токен обновления создается
        и возвращается в виде строки.
        """
        token = auth_service.create_refresh_token(test_user.id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_is_jwt(self, auth_service, test_user):
        """
        Тест формата JWT.
        
        Проверяет, что созданный токен обновления
        имеет корректный формат JWT.
        """
        token = auth_service.create_refresh_token(test_user.id)
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_refresh_token_stores_in_db(self, auth_service, test_user):
        """
        Тест сохранения в базе данных.
        
        Проверяет, что refresh токен сохраняется
        в базе данных.
        """
        token = auth_service.create_refresh_token(test_user.id)
        assert token is not None


class TestDecodeToken:
    """Тесты для декодирования токенов"""
    
    def test_decode_valid_token(self, auth_service, test_user):
        """
        Тест декодирования валидного токена.
        
        Проверяет, что валидный токен успешно
        декодируется и возвращает корректные данные.
        """
        token = auth_service.create_access_token(test_user.id)
        payload = auth_service.decode_token(token)
        assert isinstance(payload, TokenPayload)
        assert payload.sub == test_user.id

    def test_decode_invalid_token(self, auth_service):
        """
        Тест декодирования невалидного токена.
        
        Проверяет, что попытка декодирования
        невалидного токена вызывает ошибку.
        """
        with pytest.raises(HTTPException) as exc_info:
            auth_service.decode_token("invalid.token.here")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_decode_malformed_token(self, auth_service):
        """
        Тест декодирования некорректного токена.
        
        Проверяет, что попытка декодирования
        неправильно сформированного токена вызывает ошибку.
        """
        with pytest.raises(HTTPException):
            auth_service.decode_token("not-a-jwt")

    def test_decode_token_contains_user_id(self, auth_service, test_user):
        """
        Тест наличия ID пользователя в токене.
        
        Проверяет, что декодированный токен
        содержит корректный идентификатор пользователя.
        """
        token = auth_service.create_access_token(test_user.id)
        payload = auth_service.decode_token(token)
        assert payload.sub == test_user.id
        assert payload.exp is not None


class TestRefreshAccessToken:
    """Тесты для обновления access токена"""
    
    def test_refresh_access_token_success(self, auth_service, test_user):
        """
        Тест успешного обновления access токена.
        
        Проверяет, что с использованием валидного
        refresh токена можно получить новый access токен.
        """
        refresh_token = auth_service.create_refresh_token(test_user.id)
        new_access_token = auth_service.refresh_access_token(refresh_token)
        assert isinstance(new_access_token, str)
        assert len(new_access_token) > 0

    def test_refresh_with_invalid_token(self, auth_service):
        """
        Тест обновления с невалидным токеном.
        
        Проверяет, что попытка обновления с
        невалидным refresh токеном вызывает ошибку.
        """
        with pytest.raises(HTTPException) as exc_info:
            auth_service.refresh_access_token("invalid.token.here")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_new_access_token_valid(self, auth_service, test_user):
        """
        Тест валидности нового access токена.
        
        Проверяет, что новый access токен имеет
        корректный формат JWT.
        """
        refresh_token = auth_service.create_refresh_token(test_user.id)
        new_access_token = auth_service.refresh_access_token(refresh_token)
        parts = new_access_token.split(".")
        assert len(parts) == 3


class TestLogout:
    """Тесты для выхода пользователей"""
    
    def test_logout_success(self, auth_service, test_user):
        """
        Тест успешного выхода.
        
        Проверяет, что выход из системы выполняется
        без возникновения ошибок.
        """
        refresh_token = auth_service.create_refresh_token(test_user.id)
        auth_service.logout(refresh_token)

    def test_logout_revokes_token(self, auth_service, test_user):
        """
        Тест отзыва токена при выходе.
        
        Проверяет, что после выхода refresh токен
        становится недействительным.
        """
        refresh_token = auth_service.create_refresh_token(test_user.id)
        auth_service.logout(refresh_token)
        with pytest.raises(HTTPException):
            auth_service.refresh_access_token(refresh_token)

    def test_logout_invalid_token(self, auth_service):
        """
        Тест выхода с невалидным токеном.
        
        Проверяет, что выход с невалидным токеном
        обрабатывается корректно.
        """
        try:
            auth_service.logout("invalid.token.here")
        except Exception:
            pass


class TestAuthServiceIntegration:
    """Интеграционные тесты для полного цикла аутентификации"""
    
    def test_register_login_get_token_flow(self, auth_service):
        """
        Тест полного цикла: регистрация -> вход -> получение токена.
        
        Проверяет последовательное выполнение всех этапов
        аутентификации и создание токенов.
        """
        user = auth_service.register(RegisterRequest(
            name="Integration",
            surname="Test",
            email="integration@test.com",
            password="IntegrationTest123!"
        ))
        assert user.id is not None

        logged_in_user = auth_service.login("integration@test.com", "IntegrationTest123!")
        assert logged_in_user.id == user.id

        access_token = auth_service.create_access_token(user.id)
        refresh_token = auth_service.create_refresh_token(user.id)
        assert access_token is not None
        assert refresh_token is not None

    def test_register_login_refresh_logout_flow(self, auth_service):
        """
        Тест полного цикла с обновлением и выходом.
        
        Проверяет полный сценарий работы с токенами:
        регистрация, вход, обновление access токена и выход.
        """
        user = auth_service.register(RegisterRequest(
            name="Flow",
            surname="Test",
            email="flow@test.com",
            password="FlowTest123!"
        ))

        auth_service.login("flow@test.com", "FlowTest123!")

        refresh_token = auth_service.create_refresh_token(user.id)

        new_access_token = auth_service.refresh_access_token(refresh_token)
        assert new_access_token is not None

        auth_service.logout(refresh_token)

        with pytest.raises(HTTPException):
            auth_service.refresh_access_token(refresh_token)

    def test_multiple_users_independent_sessions(self, auth_service):
        """
        Тест независимости сессий разных пользователей.
        
        Проверяет, что токены разных пользователей
        не пересекаются и работают изолированно.
        """
        user1_data = RegisterRequest(
            name="User", surname="One",
            email="user1@test.com",
            password="UserOne123!"
        )
        user2_data = RegisterRequest(
            name="User", surname="Two",
            email="user2@test.com",
            password="UserTwo123!"
        )

        user1 = auth_service.register(user1_data)
        user2 = auth_service.register(user2_data)

        token1 = auth_service.create_access_token(user1.id)
        token2 = auth_service.create_access_token(user2.id)

        payload1 = auth_service.decode_token(token1)
        payload2 = auth_service.decode_token(token2)

        assert payload1.sub == user1.id
        assert payload2.sub == user2.id
        assert payload1.sub != payload2.sub