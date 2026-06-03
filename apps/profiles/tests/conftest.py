"""Local conftest.py"""
# pylint: disable=redefined-outer-name

import pytest
from faker import Faker
from pathlib import Path
import yaml
from openapi_pydantic import OpenAPI

from apps.accounts.models import User
from apps.utils import create_test_image
from apps.profiles.models import Profile
from apps.privacy_settings.models import ProfilePrivacySettings

from .factories import ProfileFactory


fake = Faker()  # Создаем экземпляр Faker
Faker.seed(42)  # Для воспроизводимости результатов


@pytest.fixture
def profile_data():
    """
    Фабрика профилей пользователя для apps.profiles.models.Profile
    """
    def get_profile(*, for_user: User | None = None, is_null=False, **kwargs):
        defaults = {}
        if not is_null:
            defaults.update({
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "profession": fake.job(),
                "short_desc": fake.paragraph(3),
                "full_desc": fake.paragraph(20),
                "wallpaper": create_test_image('wallpaper.jpg'),                   # noqa: E501 pylint: disable=line-too-long
                "avatar": create_test_image('avatar.jpg'),
                "link_to_instagram": f"https://instagram.com/{fake.user_name()}",  # noqa: E501 pylint: disable=line-too-long
                "link_to_telegram": f"https://t.me/{fake.user_name()}",            # noqa: E501 pylint: disable=line-too-long
                "link_to_github": f"https://github.com/{fake.user_name()}",        # noqa: E501 pylint: disable=line-too-long
                "link_to_vk": f"https://vk.com/{fake.user_name()}"                 # noqa: E501 pylint: disable=line-too-long
            })
        if for_user:
            defaults.update({"user_id": for_user.pk})
        defaults.update(kwargs)
        return defaults
    return get_profile


@pytest.fixture(scope="session")
def user_profile_view_contract():
    contract_path = Path(__file__).parent.parent / "contracts" / "user_profile_view.yml"
    with open(contract_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
