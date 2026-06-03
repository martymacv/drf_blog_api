"""Тесты для представлений (View)"""
import json

from typing import Any

import pytest
import allure

from schemathesis.transport.wsgi import WSGITransport
import jsonschema

from django.urls import reverse
from django.core.validators import validate_email, URLValidator
from django.core.exceptions import ValidationError

from apps.accounts.models import User

# from .helpers import update_profile_via_db
# from apps.accounts.tests.helpers import get_api_client
# from apps.privacy_settings.tests.helpers import add_to_blacklist_via_db

from apps.utils import create_test_image

from pathlib import Path


def validate_url(url):
    try:
        URLValidator(url)
        return True
    except ValidationError:
        return False


CONTRACT_TYPES = {
    'string': str,
    'integer': int,
}
CONTRACT_FORMATS = {
    'uri': validate_url,
    'email': validators.email,
}


def resolve_contracts_ref(ref: str, openapi_dict: dict) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"Поддерживаются только локальные $ref: {ref}")
    parts = ref[2:].split("/")  # отрезаем "#/" и разбиваем
    current = openapi_dict
    for part in parts:
        current = current[part]
    return current


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

    @pytest.fixture
    def updated_test_user(self, user_profile_view_contract, db):
        def _update_user_profile(user: User):
            url_path = list(user_profile_view_contract['paths'].keys())[0]
            request_body = user_profile_view_contract['paths'][url_path]['post']['requestBody']['content']['application/json']['examples']['BaseRequestBodyFields']['value']
            # self._attach('test', request_body)
            request_body['avatar'] = create_test_image('avatar.jpg')
            request_body['wallpaper'] = create_test_image('wallpaper.jpg')
            # print(request_body)
            for field, value in request_body.items():
                print(f"{field=} {value=}")
                setattr(user.profile, field, value)

            user.profile.save()
            return user
        return _update_user_profile

    @pytest.fixture
    def base_test_user(self, user_factory, updated_test_user, transactional_db):
        def _create_user(**kwargs):
            user = user_factory(**kwargs)
            return updated_test_user(user)
        return _create_user

    @pytest.fixture
    def blacklisted_test_user(self, user_factory, updated_test_user, transactional_db):
        def _create_user(user_self: User, **kwargs: Any):
            user = user_factory(**kwargs)
            user = updated_test_user(user)
            user.profile.profile_privacies.blacklist.add(user_self)
            return user
        return _create_user

    @pytest.fixture
    def user_dataset(self, base_test_user, blacklisted_test_user, transactional_db):
        def _create_dataset(*args: list[str]) -> dict[str, Any]:
            """
            :*args - должны обозначать роль пользователя
                |-- base_user: дефолтный пользователь
                |-- blacklisted_user: пользователь с чёрным списком

            returns
                |-- users: спиок из объектов User (или int для "nonexistent_user")
            """
            class NonexistentUser:
                def __init__(self, pk) -> None:
                    self.pk = pk

            users = {}
            for role in args:
                match role:
                    case 'user_self':
                        users[role] = base_test_user()
                    case 'base_user':
                        users[role] = base_test_user()
                    case 'blacklisted_user':
                        users[role] = blacklisted_test_user(users['user_self'])
                    case 'nonexistent_user':
                        users[role] = NonexistentUser(100_000)
            return users
        return _create_dataset

    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("expected_status, schema_type, required, py_type, id, param_in_query", [
        pytest.param(
            404, "null", True, None, None, None, marks=pytest.mark.negative
        ),
        pytest.param(
            404, "string", True, str, 'asdf', None, marks=pytest.mark.negative
        ),
        pytest.param(
            404, "number", True, float, 200.002, None, marks=pytest.mark.negative
        ),
        pytest.param(
            404, "null", False, int, "", None, marks=pytest.mark.negative
        ),
        pytest.param(
            200, "integer", True, int, "{value}", None, marks=pytest.mark.positive
        ),
        pytest.param(
            200, "integer", True, int, "{value}", "?pam=param&param=pam,pam", marks=pytest.mark.positive
        ),
        pytest.param(
            404, "integer", True, int, -1, None, marks=[pytest.mark.negative, pytest.mark.edge]
        ),
        pytest.param(
            404, "integer", True, int, 0, None, marks=[pytest.mark.negative, pytest.mark.boundary]
        ),
        pytest.param(
            404, "integer", True, int, 100_000, None, marks=[pytest.mark.negative, pytest.mark.boundary]
        ),
        pytest.param(
            404, "boolean", True, bool, True, None, marks=pytest.mark.negative
        ),
        pytest.param(
            404, "array", True, list, ['as', 'df'], None, marks=pytest.mark.negative
        ),
        pytest.param(
            404, "object", True, dict, {'as': 'df'}, None, marks=pytest.mark.negative
        ),
    ])
    def test_user_profile_view_url_parameters(
            self, request, user_profile_view_contract, api_client, user_dataset, expected_status, schema_type, required, py_type, id, param_in_query
    ):
        test_tags = [m.name for m in request.node.iter_markers()]
        users = user_dataset("user_self")
        api_client, _ = api_client(users["user_self"], True)

        path_key, *_ = user_profile_view_contract['paths']
        url_path = path_key.format(
            id=id.format(value=users["user_self"].pk) if "positive" in test_tags else id
        )
        if param_in_query:
            url_path += param_in_query

        allure.dynamic.title(f"Testing GET {url_path}")

        with allure.step(f"Запросить данные ендпоинта и проверить статус код в ответе"):

            response = api_client.get(url_path)
            assert response.status_code == expected_status, \
                f"Ожидался статус {expected_status}, получен {response.status_code}"

            if expected_status != 200:
                with allure.step(f"Проверить заголовок Content-Type в ответе"):
                    errors = response.headers['Content-Type']
                    expected_content_type = 'application/json' if 'boundary' in test_tags else 'text/html; charset=utf-8'
                    assert errors == expected_content_type, \
                        f"Ожидался тип контента {expected_content_type}, получен {errors}"

                if 'boundary' in test_tags:
                    with allure.step(f"Проверить сообщение об ошибке ({expected_status})"):
                        errors = response.json()
                        self._attach('errors', errors)
                        assert errors.get('detail', None), \
                            f"Отсутствует описание ошибки в ответе"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET-запросы профиля по User_ID")
    @pytest.mark.parametrize("expected_status, status_code, title, roles, user_pk, has_jwt", [
        ("HTTP_401_UNAUTHORIZED", 401, "Запросить любой профиль пользователя без авторизации", ("user_self",), "user_self", False, ),
        ("HTTP_404_NOT_FOUND", 404, "Запросить профиль по несуществующему UserId через авторизованного юзера", ("user_self", "nonexistent_user"), "nonexistent_user", True, ),
        ("HTTP_200_OK", 200, "Запросить свой профиль через авторизованного юзера", ("user_self",), "user_self", True, ),
        ("HTTP_200_OK", 200, "Запросить чужой открытый профиль через авторизованного юзера", ("user_self", "base_user"), "base_user", True, ),
        ("HTTP_404_NOT_FOUND", 404, "Запросить чужой профиль с чёрным списком через авторизованного юзера", ("user_self", "blacklisted_user"), "blacklisted_user", True, ),
    ])
    def test_get_user_profile_by_user_id(
            self, user_profile_view_contract, api_client, user_dataset, expected_status, status_code, title, roles, user_pk, has_jwt, temp_media
    ):
        """
        Тест выдачи информации пользовательских профилей
        """
        users = user_dataset(*roles)
        url_path = list(user_profile_view_contract['paths'].keys())[0]
        operation = user_profile_view_contract['paths'][url_path]['get']
        parameters_in_path = list(filter(lambda param: param['in'] == 'path', operation['parameters']))
        param_names = list(filter(lambda param: param['name'] == 'id', parameters_in_path))

        assert param_names, \
            "Контракт был изменён, в тесте используется параметр пути {id}"

        cleaned_params = {
            param['name']: users[user_pk].pk for param in param_names
        }

        with allure.step(f"{expected_status}: {title}"):
            api_client, _ = api_client(users['user_self'], has_jwt)

            response = api_client.get(url_path.format(**cleaned_params))
            api_data_fields = response.json()
            self._attach('api_data_fields', api_data_fields)

            if status_code == 200:
                ref = resolve_contracts_ref(
                    operation['responses']['200']['content']['application/json']['schema']['$ref'], user_profile_view_contract
                )
                cleaned_ref = dict(
                    filter(
                        lambda property: 'allOf' not in property[1].keys(), filter(
                        lambda property: 'oneOf' not in property[1].keys(), ref['properties'].items()
                    ))
                )
                contarct_fields = cleaned_ref
                with allure.step("Проверить полное пересечение полей с контрактом"):
                    self._attach('contract_fields', contarct_fields)
                    assert set(api_data_fields.keys()).issuperset(contarct_fields.keys()), \
                        f"Не все контрактные поля есть в ответе"

                for field, field_value in api_data_fields.items():
                    field_requirements = contarct_fields.get(field, None)
                    if field_requirements is None:
                        continue

                    nullable = field_requirements.pop('nullable', True)

                    with allure.step(f"Проверить поле {field} на пустоту"):
                        if not nullable:
                            assert field_value is None, \
                                f"Поле не может быть пустым, это запрещено контрактом!"
                        elif field_value is None:
                            continue
                        elif field_value == '':
                            continue

                        for req, req_value in field_requirements.items():
                            with allure.step(f"Валидировать поле {field} по контракту - {req}: {req_value}"):
                                match req:
                                    case 'type':
                                        assert isinstance(field_value, CONTRACT_TYPES[req_value])
                                    case 'format':
                                        assert CONTRACT_FORMATS[req_value](field_value), \
                                            f"Неверный формат {req_value}, поле содержит {field_value}"
                                    case 'maxLength':
                                        assert len(field_value) <= req_value
                                    case 'maximum':
                                        assert field_value <= req_value
                                    case 'minimum':
                                        assert field_value >= req_value
                                    case 'allOf':
                                        pass
                                    case 'oneOf':
                                        pass
                                    case 'title':
                                        pass
                                    case _: 
                                        assert False, \
                                            f"В тесте нет проверки по требованию контракта: {req}"

            else:
                ref = resolve_contracts_ref(
                    operation['responses'][str(status_code)]['content']['application/json']['schema']['$ref'], user_profile_view_contract
                )
                contarct_fields = ref['properties']
                with allure.step(f"Проверить описание ошибки {status_code}"):
                    self._attach('contract_fields', contarct_fields)
                    assert api_data_fields['detail'] == contarct_fields['detail']['default'], \
                        f"Описание ошибки не совпадает с контрактом"

            # parameters_in_path = filter(lambda param: param['in'] == 'path', operation['parameters'])
            # for param in parameters_in_path:
            #     param_name = param['name']
            #     schema_type = param['schema']['type']
            #     required = param['required']

            #     # Позитивный тест
            #     assert isinstance(users[user_pk].pk, int), \
            #         f"Ожидалася {schema_type}, получили {type(users[user_pk].pk)}"

            # expected_responses = {int(status) for status in operation.responses.keys()}

            

    #         # Проверяем, что статус разрешён контрактом
    #         assert response.status_code in expected_responses, \
    #             f"Статус {response.status_code} не описан в контракте, ожидались: {expected_responses}"

    #         # Проверяем точное совпадение статуса
    #         assert response.status_code == status_code, \
    #             f"Ожидался статус {status_code}, получен - {response.status_code}"

    #         if status_code == 200:
    #             response_200 = operation.responses[str(status_code)]

    #             # Проверяем обязательные заголовки
    #             assert response_200.content.get('application/json', None), \
    #                 f"Не получен заголовок 'Content-Type': 'application/jston'"

    #             content = response_200.content['application/json']
    #             user_schema = content.schema()
    #             # Валидируем тело ответа в соответствии с автогенерируемым контрактом
    #             self._attach('user_schema', user_schema)

                # из того, что нужно по заданию, здесь проверяется
                # список обязательных полей, структуру и типы данных, допустимость незаконтрактованных полей.
                # jsonschema.validate(instance=response.json(), schema=user_schema)

    # @allure.severity(allure.severity_level.NORMAL)
    # @user_profile_view_contract.parametrize()
    # def test_user_profile_view_contracts(self, case, api_client, base_test_user, transactional_db):
    #     user = base_test_user()
    #     _, access = api_client(user, True)
    #     allure.dynamic.parameter("method", case.method)
    #     allure.dynamic.parameter("path", case.path)
    #     allure.dynamic.title(f"Testing {case.method} {case.path}")
    #     if case.path_parameters and "id" in case.path_parameters:
    #         case.path_parameters["id"] = user.pk
    #     response = case.call(
    #         # wsgi_app=application,
    #         headers={
    #             'Authorization': f"Bearer {access}"
    #         }
    #     )
    #     case.validate_response(response)

        # with allure.step(f"Testing {case.method} {case.path}"):
        #     allure.attach("Additional debug info", name="Debug Note", attachment_type=allure.attachment_type.TEXT)
        #     response = case.call(base_url="http://localhost:8000")
        #     case.validate_response(response)

    # @allure.severity(allure.severity_level.NORMAL)
    # @allure.title("POST-запросы для обновления профиля по User_ID")
    # @pytest.mark.parametrize("user_profile_dataset", [
    #     ("HTTP_401_UNAUTHORIZED", 401, "Обновить профиль через неавторизованного юзера", USER_ROLES.SELF, False, ),
    #     ("HTTP_200_OK", 200, "Обновить свой профиль через авторизованного юзера", USER_ROLES.SELF, True, ),
    #     ("HTTP_403_FORBIDDEN", 403, "Обновить чужой профиль через авторизованного юзера", USER_ROLES.OTHER_OPEN, True, ),
    #     ("HTTP_403_FORBIDDEN", 403, "Обновить профиль через авторизованного юзера по несуществующему UserId", USER_ROLES.NONEXISTENT, True, ),
    # ], indirect=True)
    # def test_update_self_user_profile(
    #         self, user_profile_dataset, profile_data, temp_media
    # ):
    #     """
    #     Тест обновления информации в пользовательских профилей
    #     """
    #     api_client, pk, params = user_profile_dataset
    #     http_status, status_code, title, *_ = params

    #     profile = profile_data()

    #     with allure.step(f"{http_status}: {title}"):
    #         response = api_client.post(
    #             reverse(self.viewname, kwargs={'pk': str(pk)}),
    #             profile, format='multipart')
    #         assert response.status_code == status_code, \
    #             f"Ожидался статус {status_code}, получен - {response.status_code}"
        
    #         if status_code == 200:
    #             for field in profile:
    #                 self._check_field_value(response, field)

    # @allure.severity(allure.severity_level.NORMAL)
    # @allure.title("DELETE-запросы для очистки профиля по User_ID")
    # @pytest.mark.parametrize("user_profile_dataset", [
    #     ("HTTP_401_UNAUTHORIZED", 401, "Удалить профиль через неавторизованного юзера", USER_ROLES.SELF, False, ),
    #     ("HTTP_204_NO_CONTENT", 204, "Удалить свой профиль через авторизованного юзера", USER_ROLES.SELF, True, ),
    #     ("HTTP_403_FORBIDDEN", 403, "Удалить чужой пользовательский профиль через авторизованного юзера", USER_ROLES.OTHER_OPEN, True, ),
    #     ("HTTP_403_FORBIDDEN", 403, "Удалить профиль через авторизованного юзера по несуществующему UserId", USER_ROLES.NONEXISTENT, True, ),
    # ], indirect=True)
    # def test_destroy_self_user_profile(
    #         self, user_profile_dataset, profile_data, temp_media
    # ):
    #     """
    #     Тест мягкого удаления пользовательских профилей
    #     """
    #     api_client, pk, params = user_profile_dataset
    #     http_status, status_code, title, *_ = params

    #     profile = profile_data().keys()

    #     with allure.step(f"{http_status}: {title}"):
    #         response = api_client.delete(reverse(self.viewname, kwargs={'pk': str(pk)}))
    #         assert response.status_code == status_code, \
    #             f"Ожидался статус {status_code}, получен - {response.status_code}"

    #         if status_code == 204:
    #             response = api_client.get(reverse(self.viewname, kwargs={'pk': str(pk)}))
    #             for field in profile:
    #                 self._check_field_value(response, field, is_null=True)
