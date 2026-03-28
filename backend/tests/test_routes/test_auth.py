import pytest
import uuid
from fastapi import status


class TestAuthRoutes:
    """Тесты для маршрутов аутентификации"""

    def test_register_success(self, client):
        """
        Тест успешной регистрации пользователя.

        Проверяет создание нового пользователя с корректными данными,
        возврат статуса 201 и правильных полей в ответе.
        """
        unique_email = f"john_{uuid.uuid4().hex[:8]}@example.com"
        response = client.post(
            "/api/auth/register",
            json={
                "name": "John",
                "surname": "Doe",
                "email": unique_email,
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "John"
        assert data["surname"] == "Doe"
        assert data["email"] == unique_email

    def test_register_duplicate_email(self, client, test_user):
        """
        Тест регистрации с существующим email.

        Проверяет, что система возвращает ошибку при попытке
        зарегистрировать пользователя с уже используемым email.
        """
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Duplicate",
                "surname": "User",
                "email": test_user.email,
                "password": "Password123!"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, client):
        """
        Тест регистрации с некорректным email.

        Проверяет валидацию формата email при регистрации.
        """
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test",
                "surname": "User",
                "email": "invalid-email",
                "password": "Password123!"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_register_weak_password(self, client):
        """
        Тест регистрации со слабым паролем.

        Проверяет, что система отклоняет пароли,
        не соответствующие требованиям безопасности.
        """
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test",
                "surname": "User",
                "email": "test@example.com",
                "password": "123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_register_returns_user_object(self, client):
        """
        Тест структуры ответа при регистрации.

        Проверяет, что ответ содержит все необходимые поля
        и не возвращает конфиденциальную информацию.
        """
        unique_email = f"complete_{uuid.uuid4().hex[:8]}@example.com"
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Complete",
                "surname": "User",
                "email": unique_email,
                "password": "Password123!"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "surname" in data
        assert "email" in data
        assert "created_at" in data

    def test_register_name_too_long(self, client):
        """
        Тест регистрации со слишком длинным именем.

        Проверяет ограничение на максимальную длину поля name.
        """
        response = client.post(
            "/api/auth/register",
            json={
                "name": "A" * 101,
                "surname": "User",
                "email": "toolong@example.com",
                "password": "Password123!"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_login_success(self, client, test_user):
        """
        Тест успешного входа в систему.

        Проверяет аутентификацию пользователя с правильными
        учетными данными и возврат access_token.
        """
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client, test_user):
        """
        Тест входа с неверным паролем.

        Проверяет, что система отклоняет попытку входа
        с неправильным паролем.
        """
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """
        Тест входа с несуществующим пользователем.

        Проверяет обработку попытки входа с email,
        не зарегистрированным в системе.
        """
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_returns_token_type(self, client, test_user):
        """
        Тест типа возвращаемого токена.

        Проверяет, что при успешном входе возвращается
        токен типа bearer.
        """
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["token_type"] == "bearer"

    def test_refresh_success(self, client, db_session, test_user):
        """
        Тест успешного обновления токена.

        Проверяет возможность получения нового access_token
        с использованием валидного refresh_token.
        """
        from app.services.auth_service import AuthService
        auth_service = AuthService(db_session)
        refresh_token = auth_service.create_refresh_token(test_user.id)
        client.cookies.set("refresh_token", refresh_token)
        response = client.post("/api/auth/refresh")
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    def test_refresh_no_token(self, client):
        """
        Тест обновления токена без refresh_token.

        Проверяет, что запрос без токена обновления
        возвращает ошибку авторизации.
        """
        response = client.post("/api/auth/refresh")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_invalid_token(self, client):
        """
        Тест обновления с неверным токеном.

        Проверяет обработку невалидного refresh_token.
        """
        client.cookies.set("refresh_token", "invalid_token")
        response = client.post("/api/auth/refresh")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_revoked_token(self, client, db_session, test_user):
        """
        Тест обновления с отозванным токеном.

        Проверяет, что система не позволяет использовать
        refresh_token после выхода пользователя из системы.
        """
        from app.services.auth_service import AuthService
        auth_service = AuthService(db_session)
        refresh_token = auth_service.create_refresh_token(test_user.id)
        auth_service.logout(refresh_token)
        client.cookies.set("refresh_token", refresh_token)
        response = client.post("/api/auth/refresh")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_success(self, client, db_session, test_user):
        """
        Тест успешного выхода из системы.

        Проверяет, что выход из системы выполняется корректно.
        """
        from app.services.auth_service import AuthService
        auth_service = AuthService(db_session)
        refresh_token = auth_service.create_refresh_token(test_user.id)
        client.cookies.set("refresh_token", refresh_token)
        response = client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_200_OK

    def test_logout_without_token(self, client):
        """
        Тест выхода из системы без токена.

        Проверяет, что запрос на выход без refresh_token
        также выполняется успешно (идемпотентность).
        """
        response = client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_200_OK

    def test_logout_revokes_token(self, client, db_session, test_user):
        """
        Тест отзыва токена при выходе.

        Проверяет, что после выхода из системы refresh_token
        становится недействительным и не может быть использован.
        """
        from app.services.auth_service import AuthService
        auth_service = AuthService(db_session)
        refresh_token = auth_service.create_refresh_token(test_user.id)
        client.cookies.set("refresh_token", refresh_token)
        client.post("/api/auth/logout")
        response = client.post("/api/auth/refresh")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthIntegration:
    """Интеграционные тесты для полного цикла аутентификации"""

    def test_cannot_login_before_register(self, client):
        """
        Тест: невозможность входа до регистрации.

        Проверяет, что пользователь не может войти в систему,
        предварительно не зарегистрировавшись.
        """
        response = client.post(
            "/api/auth/login",
            json={
                "email": "never_registered@example.com",
                "password": "SomePassword123!"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_creates_valid_user(self, client):
        """
        Тест: регистрация создает валидного пользователя.

        Проверяет полный цикл создания пользователя:
        - успешная регистрация
        - корректная структура ответа
        - отсутствие пароля в ответе
        """
        unique_email = f"valid_{uuid.uuid4().hex[:8]}@example.com"
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Valid",
                "surname": "User",
                "email": unique_email,
                "password": "Password123!"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        user = response.json()
        assert user["id"] is not None
        assert user["name"] == "Valid"
        assert user["surname"] == "User"
        assert "created_at" in user
        assert "password" not in user