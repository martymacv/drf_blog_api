from datetime import date
from typing import Iterable
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from django.db.models.base import ModelBase
from requests import delete
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.accounts.models import User


WORK_FORMATS = [
    ('office', 'офис'),
    ('hybrid', 'гибрид'),
    ('remote', 'удаленно'),
    ('any', 'любой')
]

PRIVACIES = [
    ('all', 'видно всем'),
    ('not_all', 'всем, кроме...'),
    ('nobody', 'никому')
]


def user_avatar_path(instance, filename):
    """Персонализируется путь к аватару пользователя"""
    return f"avatars/user_{instance.user.id}/{filename}"


def user_wallpaper_path(instance, filename):
    """Персонализируется путь к обоям пользователя"""
    return f"wallpapers/user_{instance.user.id}/{filename}"


class Skill(models.Model):
    """Модель для хранения уникальных навыков"""
    name = models.CharField(
        'Название навыка',
        max_length=50, unique=True, db_index=True
    )
    description = models.TextField(
        'Описание',
        blank=True, default=''
    )

    # Для отслеживания
    created_at = models.DateTimeField(
        'Дата создания', auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления', auto_now=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return str(self.name)


# class SkillCluster(models.Model):
#     """Модель для хранения уникальных кластеров навыков"""
#     cluster_name = models.CharField(max_length=20, unique=True)
#     order = models.PositiveSmallIntegerField(default=0, blank=True)

#     # Навыки
#     skills = models.ManyToManyField(
#         Skill, related_name='skill_clusters', blank=True
#     )
#     privacy = models.CharField(
#         verbose_name='Настройка видимости кластера навыков',
#         max_length=10, choices=PRIVACIES, default='all', blank=True
#     )

#     class Meta:
#         ordering = ['order', 'cluster_name']
#         verbose_name = 'Кластер навыков'
#         verbose_name_plural = 'Кластеры навыков'

#     def __str__(self):
#         return str(self.cluster_name)


class Profile(models.Model):
    """
    Модель для профиля пользователя
    """
    EDUCATION_CHOICES = [
        ('nothing', 'не указано'),
        ('school_9', '9 классов'),
        ('school_11', '11 классов'),
        ('ptu', 'ПТУ / Профессиональное училище'),
        ('technical_school', 'Техникум'),
        ('college', 'Колледж'),
        ('unfinished_higher', 'Неоконченное высшее'),
        ('bachelor', 'Бакалавр'),
        ('specialist', 'Специалист'),
        ('master', 'Магистр'),
        ('phd', 'Кандидат наук'),
        ('doctor', 'Доктор наук'),
        ('mba', 'MBA'),
    ]

    # Персональные данные
    first_name = models.CharField(max_length=20, default='', blank=True)
    middle_name = models.CharField(max_length=50, default='', blank=True)
    last_name = models.CharField(max_length=20, default='', blank=True)
    profession = models.CharField(
        verbose_name='Senior Product Manager | Growth & Monetization',
        max_length=100, default='', blank=True
    )

    # Локация
    city = models.CharField(max_length=100, default='', blank=True)
    country = models.CharField(max_length=100, default='', blank=True)
    relocation = models.CharField(max_length=200, default='', blank=True)

    # Образование
    edu_level = models.CharField(
        max_length=30, choices=EDUCATION_CHOICES, default='nothing', blank=True
    )
    institution_name = models.CharField(max_length=200, default='', blank=True)
    graduation_year = models.SmallIntegerField(null=True, blank=True)

    short_desc = models.CharField(max_length=1000, default='', blank=True)
    full_desc = models.TextField(default='', blank=True)

    wallpaper = models.ImageField(
        upload_to=user_wallpaper_path, null=True, blank=True
    )
    avatar = models.ImageField(
        upload_to=user_avatar_path, null=True, blank=True
    )

    link_to_instagram = models.URLField(default='', blank=True)
    link_to_telegram = models.URLField(default='', blank=True)
    link_to_github = models.URLField(default='', blank=True)
    link_to_vk = models.URLField(default='', blank=True)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __iter__(self):
        for field in self._meta.fields:  # pylint: disable=no-member
            if not field.auto_created:
                yield field.name, getattr(self, field.name)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @classmethod
    def get_profile(cls, user_id):
        """Получаем профиль по user_id"""
        try:
            profile = cls.objects.get(user_id=user_id)
        except cls.DoesNotExist:
            profile = None

        if profile is None:
            raise NotFound(
                detail="Profile not found"
            )

        return profile

    def delete(self, using=None, keep_parents=False):
        # user = User.objects.get(pk=self.user)
        pass

    def anonymize(self):
        """Очищает персональные данные, но сохраняет запись"""
        default_profile = Profile()
        for field in self._meta.fields:
            if field.name != 'id' and field.name != 'user':
                setattr(self, field.name, getattr(default_profile, field.name))
        self.save()
        self.user.is_active = False
        self.user.save()

    @property
    def full_name(self):
        return str(self)

    @property
    def email(self):
        return self.user.primary_email

    @property
    def total_experience_years(self):
        # Расчет общего опыта работы
        experiences = self.experiences.all()
        if not experiences:
            return 0

        total_days = 0
        for exp in experiences:
            if exp.end_date:
                total_days += (exp.end_date - exp.start_date).days
            else:
                total_days += (date.today() - exp.start_date).days

        return round(total_days / 365.25, 1)


class WorkFormat(models.Model):
    """
    Модель для хранения форматов работы
    """
    office = models.BooleanField(default=False, blank=True)
    hybrid = models.BooleanField(default=False, blank=True)
    remote = models.BooleanField(default=False, blank=True)

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='work_formats'
    )

    class Meta:
        verbose_name = 'Форматы работы'
        verbose_name_plural = 'Форматы работы'


class ProfileSkill(models.Model):
    """Модель для хранения навыков пользователя"""
    level = models.PositiveSmallIntegerField(
        'Уровень владения',
        choices=[(i, f"{i}/10") for i in range(1, 11)],
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=1,
        blank=True
    )
    is_current = models.BooleanField(
        'Используется ли сейчас', default=True,
    )
    privacy = models.CharField(
        verbose_name='Настройка видимости конкретного навыка',
        max_length=10, choices=PRIVACIES, default='all', blank=True
    )

    # Связь с профилем (у одного профиля может быть множество скилов)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='profile_skills',
        verbose_name='Профиль'
    )
    # Связь с таблицей уникальных навыков
    # (у записи о навыке может быть множество вариантов)
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='profile_skills',
        verbose_name='Навык'
    )

    # Для отслеживания
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        ordering = ['-level', 'skill']
        unique_together = ['profile', 'skill']
        verbose_name = 'Навык пользователя'
        verbose_name_plural = 'Навыки пользователя'
        indexes = [
            models.Index(fields=['profile', 'level']),
            models.Index(fields=['profile', 'is_current']),
        ]

    def __str__(self):
        return str(self.skill)
