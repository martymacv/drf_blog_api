import factory
from factory.django import DjangoModelFactory

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

User = get_user_model()


# @factory.django.mute_signals(post_save) # Сигнал post_save будет заглушен
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        # django_get_or_create = ('email',)

    email = factory.Sequence(lambda n: f'testuser{n}@example.com')
    password = 'testpass123'
    email_verified = True
