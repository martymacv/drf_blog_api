import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from apps.profiles.models import Profile


User = get_user_model()


class ProfileFactory(DjangoModelFactory):

    class Meta:
        model = Profile

    