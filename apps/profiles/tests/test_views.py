"""Тесты для представлений (View)"""
import json
import pytest
import allure

from django.urls import reverse

from .helpers import update_profile_via_db
from apps.accounts.tests.helpers import get_api_client
from apps.privacy_settings.tests.helpers import add_to_blacklist_via_db


class USER_ROLES:
    SELF = 'self'
    NONEXISTENT ='nonexistent'
    OTHER_OPEN = 'other_open'
    OTHER_BLACKLISTED = 'other_blacklisted'


@allure.feature("DRF views / viewsets endpoints")
@allure.story("Взаимодействие с профилями пользователей")
@pytest.mark.django_db
class TestUserProfileView:
    """
    Проверяется выдача информации по запросу
    авторизованного пользователя о другом пользователе
    """
    viewname = 'rw_user_profile'

    @staticmethod
    def _attach(name: str = "Dummy", data: dict = {}):
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=4),
            name=name,
            attachment_type=allure.attachment_type.JSON
        )

    def _check_field_value(self, response, field, is_null=False):
        with allure.step(f"Проверить, что поле {field} действительно обновилось"):
            actual_value = response.data.get(field, None)
            self._attach(name=field, data={
                field: actual_value
            })

            if is_null:
                actual_value = not actual_value

            assert actual_value, \
                f"Ожидалось, что значение поля {'' if is_null else 'не'} будет пустым"

    @pytest.fixture()
    def user_profile_dataset(self, request, user_factory, profile_data):
        users = [user_factory() for _ in range(3)]
        for user in users:
            update_profile_via_db(user.profile, **profile_data())

        open_user1, open_user2, close_user = users
        add_to_blacklist_via_db(
            close_user.profile.profile_privacies,
            open_user1
        )

        target_user = request.param[3]
        target_users = {
            USER_ROLES.SELF: open_user1.pk,
            USER_ROLES.NONEXISTENT: 1_000_000_000,
            USER_ROLES.OTHER_OPEN: open_user2.pk,
            USER_ROLES.OTHER_BLACKLISTED: close_user.pk,
        }

        has_jwt = request.param[4]
        api_client = get_api_client(open_user1, has_jwt=has_jwt)

        return api_client, target_users.get(target_user, None), request.param

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET-запросы профиля по User_ID")
    @pytest.mark.parametrize("user_profile_dataset", [
        ("HTTP_401_UNAUTHORIZED", 401, "Запросить любой профиль пользователя без авторизации", USER_ROLES.SELF, False, ),
        ("HTTP_404_NOT_FOUND", 404, "Запросить профиль по несуществующему UserId через авторизованного юзера", USER_ROLES.NONEXISTENT, True, ),
        ("HTTP_200_OK", 200, "Запросить свой профиль через авторизованного юзера", USER_ROLES.OTHER_OPEN, True, ),
        ("HTTP_200_OK", 200, "Запросить чужой открытый профиль через авторизованного юзера", USER_ROLES.OTHER_OPEN, True, ),
        ("HTTP_404_NOT_FOUND", 404, "Запросить чужой профиль с чёрным списком через авторизованного юзера", USER_ROLES.OTHER_BLACKLISTED, True, ),
    ], indirect=True)
    def test_get_user_profile_by_user_id(
            self, user_profile_dataset, temp_media
    ):
        """
        Тест выдачи информации пользовательских профилей
        """
        api_client, pk, params = user_profile_dataset
        http_status, status_code, title, *_ = params

        with allure.step(f"{http_status}: {title}"):
            response = api_client.get(reverse(self.viewname, kwargs={'pk': str(pk)}))
            assert response.status_code == status_code, \
                f"Ожидался статус {status_code}, получен - {response.status_code}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("POST-запросы для обновления профиля по User_ID")
    @pytest.mark.parametrize("user_profile_dataset", [
        ("HTTP_401_UNAUTHORIZED", 401, "Обновить профиль через неавторизованного юзера", USER_ROLES.SELF, False, ),
        ("HTTP_200_OK", 200, "Обновить свой профиль через авторизованного юзера", USER_ROLES.SELF, True, ),
        ("HTTP_403_FORBIDDEN", 403, "Обновить чужой профиль через авторизованного юзера", USER_ROLES.OTHER_OPEN, True, ),
        ("HTTP_403_FORBIDDEN", 403, "Обновить профиль через авторизованного юзера по несуществующему UserId", USER_ROLES.NONEXISTENT, True, ),
    ], indirect=True)
    def test_update_self_user_profile(
            self, user_profile_dataset, profile_data, temp_media
    ):
        """
        Тест обновления информации в пользовательских профилей
        """
        api_client, pk, params = user_profile_dataset
        http_status, status_code, title, *_ = params

        profile = profile_data()

        with allure.step(f"{http_status}: {title}"):
            response = api_client.post(
                reverse(self.viewname, kwargs={'pk': str(pk)}),
                profile, format='multipart')
            assert response.status_code == status_code, \
                f"Ожидался статус {status_code}, получен - {response.status_code}"
        
            if status_code == 200:
                for field in profile:
                    self._check_field_value(response, field)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("DELETE-запросы для очистки профиля по User_ID")
    @pytest.mark.parametrize("user_profile_dataset", [
        ("HTTP_401_UNAUTHORIZED", 401, "Удалить профиль через неавторизованного юзера", USER_ROLES.SELF, False, ),
        ("HTTP_204_NO_CONTENT", 204, "Удалить свой профиль через авторизованного юзера", USER_ROLES.SELF, True, ),
        ("HTTP_403_FORBIDDEN", 403, "Удалить чужой пользовательский профиль через авторизованного юзера", USER_ROLES.OTHER_OPEN, True, ),
        ("HTTP_403_FORBIDDEN", 403, "Удалить профиль через авторизованного юзера по несуществующему UserId", USER_ROLES.NONEXISTENT, True, ),
    ], indirect=True)
    def test_destroy_self_user_profile(
            self, user_profile_dataset, profile_data, temp_media
    ):
        """
        Тест мягкого удаления пользовательских профилей
        """
        api_client, pk, params = user_profile_dataset
        http_status, status_code, title, *_ = params

        profile = profile_data().keys()

        with allure.step(f"{http_status}: {title}"):
            response = api_client.delete(reverse(self.viewname, kwargs={'pk': str(pk)}))
            assert response.status_code == status_code, \
                f"Ожидался статус {status_code}, получен - {response.status_code}"

            if status_code == 204:
                response = api_client.get(reverse(self.viewname, kwargs={'pk': str(pk)}))
                for field in profile:
                    self._check_field_value(response, field, is_null=True)
