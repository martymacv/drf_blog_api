"""
Тесты моделей приложения profiles
"""
# pylint: disable=too-few-public-methods,no-member

import pytest
import allure
import json

from django.db import transaction, IntegrityError

from apps.accounts.models import User
from apps.profiles.models import Profile
from apps.utils import is_django_field_empty

from .helpers import update_profile_via_db


# Общие шаги для модуля
@allure.step("Проверить, что данные профиля пользователя")
def assert_user_profile_data(profile: Profile, is_not_empty: bool = True):
    profile_fields_value = list(filter(
        lambda value: value,
        (
            getattr(profile, attr.name) for attr in Profile._meta.fields
            if not attr.auto_created and attr.name not in ('pk', 'id', 'user', 'edu_level',)
        )
    ))
    allure.attach(
        str(list(profile_fields_value)),
        name="Значения полей профиля",
        attachment_type=allure.attachment_type.TEXT
    )
    assert bool(profile_fields_value) == is_not_empty, \
        "Профиль заполнен" if is_not_empty else f"Не все поля пусты"


@allure.feature("CRUD-операции с Базой Данных")
@allure.story("Модели User и Profile")
@pytest.mark.django_db
class TestProfileModel:
    """
    Тесты для модели профиля пользователя в базе данных
    """
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Добавление записи в модель User")
    def test_create_unique_user_profile(
            self, user_factory, profile_data, temp_media):
        """
        Проверяется создание профиля для пользователя
        Один профиль для одного пользователя
        """
        with allure.step("1. Создать пользователя через модель User"):
            user = user_factory()
            assert isinstance(user, User), \
                f"Объект не является экземпляром User: {repr(user)}"

        with allure.step(
            "2. Проверить, что связанный профиль автоматически создался в модели Profile"
        ):
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                profile = None
            assert profile, f"Профиль не был создан"

        assert_user_profile_data(profile, is_not_empty=False)

        with allure.step(
            "4. Проверить, что уровень образования по умолчанию = nothing"
        ):
            edu_level = getattr(profile, 'edu_level')
            assert edu_level == 'nothing', f"Значение по умолчанию не равно nothing ({edu_level=})"

        # Для одного пользователя создать можно только один профиль
        with allure.step(
            "5. Проверить, что второй профиль через модель Profile создать нельзя"
        ):
            r_profile = profile_data(for_user=user)
            profile1 = None
            try:
                with transaction.atomic():
                    profile1 = Profile.objects.create(**r_profile)
            except IntegrityError as e:
                allure.attach(
                    str(e),
                    name="IntegrityError",
                    attachment_type=allure.attachment_type.TEXT
                )
            finally:
                assert not isinstance(profile1, Profile), f"Второй профиль не должен был быть создан!"

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Удаление пользователя из БД")
    def test_soft_delete_user_profile_from_db(
            self, user_factory, profile_data, temp_media
    ):
        """
        Проверяется удаление данных из БД
        """
        user = user_factory()
        profile = profile_data()
        with allure.step("1. Заполнить профиль случайно сгенерированными данными"):
            update_profile_via_db(user.profile, **profile)
            assert_user_profile_data(user.profile, is_not_empty=True)

        with allure.step("2. Очистить профиль через метод Profile.anonymize"):
            # очищаем профиль методом Profile.anonymize
            user.profile.anonymize()
            assert_user_profile_data(user.profile, is_not_empty=False)

        with allure.step("3. Проверить, что пользователь деактивирован"):
            # проверяем, что пользователь деактивирован
            assert user.is_active == False, \
                f"Пользователь не деактивирован"
