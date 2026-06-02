import logging

from django.urls import reverse

from apps.profiles.models import Profile


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


def update_profile_via_db(obj: Profile, **overrides):
    for attr, value in overrides.items():
        setattr(obj, attr, value)
    obj.save(update_fields=overrides.keys())

def reverse_url(viewname: str, **kwargs) -> str:
    logging.info(f"{kwargs=}")
    return reverse(viewname=viewname, kwargs=kwargs)
