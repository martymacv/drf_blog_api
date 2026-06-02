"""
Тесты моделей приложения profiles
"""
# pylint: disable=too-few-public-methods,no-member

import os
import pytest
import allure

from rest_framework.exceptions import ValidationError

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from apps.profiles.models import Profile, user_avatar_path, user_wallpaper_path
from apps.profiles.serializers import ProfileSerializer

from .helpers import update_profile_via_db


@allure.step("Верифицировать данные")
def assert_user_profile_data(user, profile, serialized_data, is_validated: bool = False):
    # проверка структуры данных, загруженных из БД
    output = "Поле '{field}' не содержит данных или данные не того типа"
    media_path = {
        'avatar': user_avatar_path,
        'wallpaper': user_wallpaper_path
    }
    for field, value in profile.items():
        if field == 'user_id':
            assert serialized_data['user'] == value, output.format(field=field)
        elif isinstance(value, SimpleUploadedFile):
            if is_validated:
                assert serialized_data[field] == value, output.format(field=field)
            else:
                assert serialized_data[field] == os.path.join(
                    settings.MEDIA_URL, media_path[field](user.profile, value.name)
                ), output.format(field=field)
        else:
            assert serialized_data[field] == value, output.format(field=field)


@allure.feature("DRF-сериализаторы")
@allure.story("Сериализатор для профиля пользователя")
@pytest.mark.django_db
class TestProfileSerializer:
    """
    Проверяет сериализатор ProfileSerializer, который
    возвращает данные по user_id для авторизованных пользователей
    """
    serializer_class = ProfileSerializer

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Сериализация данных Profile -> JSON")
    def test_execute_profile_data_from_db(
            self, user_factory, profile_data, temp_media
    ):
        """
        Проверяется извлечение данных из БД сериализатором
        """
        user = user_factory()
        profile = profile_data()
        update_profile_via_db(user.profile, **profile)

        with allure.step("Извлечь данные из БД"):
            serializer = self.serializer_class(instance=user.profile)
            assert serializer, f"Сериализатор пуст, данные не извлечены"

        assert_user_profile_data(user, profile, serializer.data)


    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Сериализация данных JSON -> Profile")
    def test_update_profile_data_in_db(
            self, user_factory, profile_data, temp_media
    ):
        """
        Проверяется обновление данных в БД сериализатором
        """
        user = user_factory()
        profile = profile_data()

        with allure.step("Частичное обновление данных профиля в БД через ProfileSerializer"):
            # попытка полного обновления данных (user_id is UNIQUE)
            serializer = self.serializer_class(
                instance=user.profile, data=profile, partial=True
            )
            assert serializer.is_valid(), f"Ошибка сериализации данных из JSON"
            serializer.save()

        assert_user_profile_data(user, profile, serializer.validated_data, is_validated=True)
