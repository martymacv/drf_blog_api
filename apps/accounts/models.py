from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_comfirmed = models.BooleanField(default=False)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.email)


class Profile(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    profession = models.CharField(max_length=50)
    short_desc = models.CharField(max_length=300)
    full_desc = models.TextField()

    wallpaper = models.ImageField(upload_to='wallpapers/')
    avatar = models.ImageField(upload_to='avatar/')

    link_to_instagram = models.URLField()
    link_to_vk = models.URLField()

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
