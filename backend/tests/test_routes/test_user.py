import pytest
from fastapi import status


class TestUserRoutes:
    """Тесты для маршрутов работы с пользователями"""
    
    def test_get_all_users_success(self, client, test_user):
        """
        Тест успешного получения списка всех пользователей.
        
        Проверяет, что эндпоинт возвращает список пользователей
        и содержит хотя бы одного пользователя.
        """
        response = client.get("/api/users")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_all_users_contains_test_user(self, client, test_user):
        """
        Тест наличия тестового пользователя в списке.
        
        Проверяет, что созданный тестовый пользователь
        присутствует в общем списке пользователей.
        """
        response = client.get("/api/users")
        
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        
        user_ids = [u["id"] for u in users]
        assert test_user.id in user_ids

    def test_get_all_users_valid_schema(self, client, test_user):
        """
        Тест валидности схемы ответа списка пользователей.
        
        Проверяет, что каждый пользователь в списке
        содержит все необходимые поля.
        """
        response = client.get("/api/users")
        
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        
        assert len(users) > 0
        user = users[0]
        
        assert "id" in user
        assert "name" in user
        assert "surname" in user
        assert "email" in user
        assert "created_at" in user

    def test_get_all_users_no_password(self, client, test_user):
        """
        Тест отсутствия пароля в ответе.
        
        Проверяет, что конфиденциальная информация (пароль)
        не возвращается в ответе при получении списка пользователей.
        """
        response = client.get("/api/users")
        
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        
        for user in users:
            assert "password" not in user
            assert "hashed_password" not in user

    def test_get_current_user_unauthorized(self, client):
        """
        Тест требования аутентификации для получения текущего пользователя.
        
        Проверяет, что запрос к эндпоинту /me без токена
        возвращает ошибку авторизации.
        """
        response = client.get("/api/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_success(self, client_with_auth, test_user):
        """
        Тест успешного получения текущего аутентифицированного пользователя.
        
        Проверяет, что эндпоинт возвращает корректные данные
        пользователя, выполнившего запрос.
        """
        response = client_with_auth.get("/api/users/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["name"] == test_user.name
        assert data["surname"] == test_user.surname
        assert data["email"] == test_user.email

    def test_get_current_user_valid_schema(self, client_with_auth, test_user):
        """
        Тест валидности схемы ответа текущего пользователя.
        
        Проверяет, что ответ содержит все необходимые поля.
        """
        response = client_with_auth.get("/api/users/me")
        
        assert response.status_code == status.HTTP_200_OK
        user = response.json()
        
        assert "id" in user
        assert "name" in user
        assert "surname" in user
        assert "email" in user
        assert "created_at" in user

    def test_get_current_user_no_password(self, client_with_auth):
        """
        Тест отсутствия пароля в ответе текущего пользователя.
        
        Проверяет, что конфиденциальная информация (пароль)
        не возвращается в ответе.
        """
        response = client_with_auth.get("/api/users/me")
        
        assert response.status_code == status.HTTP_200_OK
        user = response.json()
        
        assert "password" not in user
        assert "hashed_password" not in user

    def test_get_user_by_id_success(self, client, test_user):
        """
        Тест успешного получения пользователя по ID.
        
        Проверяет, что пользователь корректно возвращается
        по его идентификатору.
        """
        response = client.get(f"/api/users/{test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["name"] == test_user.name
        assert data["email"] == test_user.email

    def test_get_user_by_id_valid_schema(self, client, test_user):
        """
        Тест валидности схемы ответа пользователя по ID.
        
        Проверяет, что ответ содержит все необходимые поля.
        """
        response = client.get(f"/api/users/{test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        user = response.json()
        
        assert "id" in user
        assert "name" in user
        assert "surname" in user
        assert "email" in user
        assert "created_at" in user

    def test_get_user_by_id_no_password(self, client, test_user):
        """
        Тест отсутствия пароля в ответе пользователя по ID.
        
        Проверяет, что конфиденциальная информация (пароль)
        не возвращается в ответе.
        """
        response = client.get(f"/api/users/{test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        user = response.json()
        
        assert "password" not in user
        assert "hashed_password" not in user

    def test_get_user_by_id_not_found(self, client):
        """
        Тест получения несуществующего пользователя.
        
        Проверяет, что запрос к несуществующему пользователю
        возвращает статус 404.
        """
        response = client.get("/api/users/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_by_id_invalid_id_format(self, client):
        """
        Тест получения пользователя с некорректным форматом ID.
        
        Проверяет валидацию формата идентификатора пользователя.
        """
        response = client.get("/api/users/invalid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_delete_user_success(self, client, test_user_2, db_session):
        """
        Тест успешного удаления пользователя.
        
        Проверяет, что пользователь удаляется и возвращается
        сообщение об успешном удалении.
        """
        user_id = test_user_2.id
        
        response = client.delete(f"/api/users/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()

    def test_delete_user_not_found(self, client):
        """
        Тест удаления несуществующего пользователя.
        
        Проверяет, что запрос на удаление несуществующего
        пользователя возвращает статус 404.
        """
        response = client.delete("/api/users/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_invalid_id_format(self, client):
        """
        Тест удаления пользователя с некорректным форматом ID.
        
        Проверяет валидацию формата идентификатора при удалении.
        """
        response = client.delete("/api/users/invalid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_delete_user_removes_from_database(self, client, test_user_2, db_session):
        """
        Тест физического удаления пользователя из базы данных.
        
        Проверяет, что после успешного удаления пользователь
        отсутствует в базе данных.
        """
        user_id = test_user_2.id
        
        delete_response = client.delete(f"/api/users/{user_id}")
        assert delete_response.status_code == status.HTTP_200_OK
        
        get_response = client.get(f"/api/users/{user_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestUserIntegration:
    """Интеграционные тесты для операций с пользователями"""
    
    def test_get_all_users_then_get_specific(self, client, test_user):
        """
        Тест последовательности: получение всех пользователей,
        затем получение конкретного.
        
        Проверяет корректность работы эндпоинтов в связке:
        сначала получение списка, затем получение пользователя
        из этого списка по ID.
        """
        list_response = client.get("/api/users")
        assert list_response.status_code == status.HTTP_200_OK
        
        users = list_response.json()
        assert len(users) > 0
        
        first_user = users[0]
        get_response = client.get(f"/api/users/{first_user['id']}")
        
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["id"] == first_user["id"]

    def test_current_user_matches_get_by_id(self, client_with_auth, test_user):
        """
        Тест соответствия данных текущего пользователя
        данным при получении по ID.
        
        Проверяет, что эндпоинты /me и /users/{id} возвращают
        одинаковые данные для одного пользователя.
        """
        me_response = client_with_auth.get("/api/users/me")
        assert me_response.status_code == status.HTTP_200_OK
        me_data = me_response.json()
        
        by_id_response = client_with_auth.get(f"/api/users/{me_data['id']}")
        assert by_id_response.status_code == status.HTTP_200_OK
        by_id_data = by_id_response.json()
        
        assert me_data["id"] == by_id_data["id"]
        assert me_data["email"] == by_id_data["email"]
        assert me_data["name"] == by_id_data["name"]
        assert me_data["surname"] == by_id_data["surname"]

    def test_multiple_users_in_list(self, client, test_user, test_user_2):
        """
        Тест наличия нескольких пользователей в списке.
        
        Проверяет, что оба созданных тестовых пользователя
        присутствуют в общем списке.
        """
        response = client.get("/api/users")
        
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        
        user_ids = [u["id"] for u in users]
        assert test_user.id in user_ids
        assert test_user_2.id in user_ids

    def test_user_data_consistency(self, client, test_user):
        """
        Тест согласованности данных пользователя.
        
        Проверяет, что данные пользователя, полученные из списка,
        совпадают с данными, полученными по ID.
        """
        list_response = client.get("/api/users")
        users = list_response.json()
        user_from_list = next(u for u in users if u["id"] == test_user.id)
        
        by_id_response = client.get(f"/api/users/{test_user.id}")
        user_by_id = by_id_response.json()
        
        assert user_from_list["id"] == user_by_id["id"]
        assert user_from_list["email"] == user_by_id["email"]
        assert user_from_list["name"] == user_by_id["name"]
        assert user_from_list["surname"] == user_by_id["surname"]

    def test_authenticated_user_is_in_system(self, client_with_auth, test_user):
        """
        Тест присутствия аутентифицированного пользователя в системе.
        
        Проверяет, что пользователь, выполнивший аутентификацию,
        присутствует в общем списке пользователей.
        """
        me_response = client_with_auth.get("/api/users/me")
        assert me_response.status_code == status.HTTP_200_OK
        
        all_users_response = client_with_auth.get("/api/users")
        assert all_users_response.status_code == status.HTTP_200_OK
        
        all_users = all_users_response.json()
        user_ids = [u["id"] for u in all_users]
        assert test_user.id in user_ids

    def test_delete_and_verify_removal(self, client, test_user_2):
        """
        Тест полного цикла удаления пользователя.
        
        Проверяет последовательность:
        - существование пользователя до удаления
        - успешное удаление
        - отсутствие пользователя после удаления
        """
        user_id = test_user_2.id
        
        get_before = client.get(f"/api/users/{user_id}")
        assert get_before.status_code == status.HTTP_200_OK
        
        delete_response = client.delete(f"/api/users/{user_id}")
        assert delete_response.status_code == status.HTTP_200_OK
        
        get_after = client.get(f"/api/users/{user_id}")
        assert get_after.status_code == status.HTTP_404_NOT_FOUND