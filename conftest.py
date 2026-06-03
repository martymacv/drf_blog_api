"""
Global conftest.py
Общие для всех уровней тестов фабрики фикстур
"""

import tempfile
import shutil
import pytest

from django.test import override_settings

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.authentication.tokens import CustomAccessToken


# собираем все conftest воедино
pytest_plugins = [
    'apps.accounts.tests.conftest',
    'apps.profiles.tests.conftest',
]


@pytest.fixture
def temp_media():
    """Создает временную MEDIA_ROOT которая автоматически удаляется"""
    temp_dir = tempfile.mkdtemp()

    with override_settings(MEDIA_ROOT=temp_dir):
        yield temp_dir

    # Удаляем временную папку после теста
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def api_client():
    def _create(user: User | None, has_jwt: bool = True):
        client = APIClient()
        access = None
        if has_jwt:
            access = CustomAccessToken.for_user(user)  # type: ignore
            client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {access}'
            )
        return client, access
    
    return _create
