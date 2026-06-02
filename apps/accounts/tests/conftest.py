"""Local conftest.py"""
# pylint: disable=no-member

import pytest
from faker import Faker

from django.urls import reverse

from apps.accounts.models import User
from apps.profiles.models import Profile
from apps.privacy_settings.models import ProfilePrivacySettings

from apps.authentication.tokens import CustomAccessToken

from .factories import UserFactory


fake = Faker()  # Создаем экземпляр Faker
Faker.seed(42)  # Для воспроизводимости результатов


@pytest.fixture
def user_factory():
    """
    Фабрика по производству юзеров с пустыми профилями
    """
    return UserFactory
