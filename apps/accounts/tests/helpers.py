import logging
from faker import Faker

from django.urls import reverse

from rest_framework.test import APIClient

from apps.authentication.tokens import CustomAccessToken
from apps.accounts.models import User

from .factories import UserFactory


fake = Faker()  # Создаем экземпляр Faker
Faker.seed(42)  # Для воспроизводимости результатов

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),          # в консоль
        logging.FileHandler('pytest.log')   # в файл
    ]
)
logger = logging.getLogger(__name__)


def create_user_via_db(**overrides):
    """
    Создаёт пользователя в БД через ORM (для внутренних тестов).
    """
    return UserFactory(**overrides)

def get_url(viewname: str, **kwargs) -> str:
    return reverse(
        viewname=viewname, kwargs=kwargs
    )

def get_api_client(user: User | None = None, has_jwt: bool = True) -> APIClient:
    client = APIClient()
    refresh = None
    if user and has_jwt:
        refresh = CustomAccessToken.for_user(user)  # type: ignore
        client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh}'
        )

    logging.info(f"{id(client)=} {id(user)=}, {user=}, {refresh}, {has_jwt=}")
    return client
