from apps.privacy_settings.models import ProfilePrivacySettings
from apps.accounts.models import User


def add_to_blacklist_via_db(obj: ProfilePrivacySettings, *args) -> None:
    """
    :*args - исключительно для моделей User
    """
    for user in args:
        obj.blacklist.add(user)

def add_to_whitelist_via_db(obj: ProfilePrivacySettings, *args) -> None:
    """
    :*args - исключительно для моделей User
    """
    for user in args:
        obj.whitelist.add(user)
