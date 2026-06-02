"""Сериализаторы для профилей пользователей"""
# pylint: disable=too-few-public-methods,no-member
from requests import delete
from rest_framework import serializers
from apps.profiles.models import Profile, ProfileSkill, Skill, WorkFormat

from apps.privacy_settings.models import ProfilePrivacySettings


class BaseModelSerializer(serializers.ModelSerializer):
    """Базовый сериализатор"""

    class Meta:
        abstract = True

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation.pop('profile', None)
    #     # Также удаляем другие связанные поля, если нужно
    #     representation.pop('work_experience', None)
    #     return representation
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if getattr(instance, 'work_experience', None):
                if request.user.pk == instance.work_experience.profile.user.pk:
                    return representation
            elif request.user.pk == instance.profile.user.pk:
                return representation
        if representation.get('privacy', None) == 'nobody':
            return {}
        return representation


class WorkFormatSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выдачи и установки предпочитаемых
    форматов работы (офис, удаленно, гибрид)
    """

    class Meta:
        model = WorkFormat
        # fields = '__all__'
        exclude = ['profile']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выдачи профиля пользователя
    по запросу авторизованного пользователя
    """
    work_formats = WorkFormatSerializer(partial=True, read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        """
        Маскуются поля в зависимости от настроек приватности
        при отображении (GET запросы)
        """
        representation = super().to_representation(instance)

        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return representation

        request_user = request.user
        instance_user = instance.user

        if request and request_user.id != instance_user.id:
            try:
                privacy_settings = (
                    ProfilePrivacySettings.objects
                    .get(profile=instance)
                )
            except ProfilePrivacySettings.DoesNotExist:
                return representation

            blacklist = getattr(privacy_settings, 'blacklist', [])
            whitelist = getattr(privacy_settings, 'whitelist', [])

            blacklist = list(blacklist.values_list('id', flat=True))
            whitelist = list(whitelist.values_list('id', flat=True))

            for field_name in list(representation.keys()):
                if field_name in ('id', 'user'):
                    continue

                access_level = getattr(privacy_settings, field_name, 'all')

                if access_level == 'all':
                    continue

                if access_level == 'not_all':
                    if all((
                        request_user.is_authenticated,
                        request_user.id not in blacklist
                    )):
                        continue
                    representation.pop(field_name)
                    continue

                if access_level == 'no_one_except':
                    if all((
                        request_user.is_authenticated,
                        request_user.id in whitelist,
                        request_user.id not in blacklist
                    )):
                        continue
                    representation.pop(field_name)
                    continue

                representation.pop(field_name)

                # mask_value = '' if field_name in ('avatar', 'wallpaper') else '*****'

                # if access_level != 'all' and not request.user.is_authenticated:
                #     representation[field_name] = mask_value
                # elif access_level == 'nobody' and request.user.is_authenticated:
                #     representation[field_name] = mask_value

            return representation

        return representation


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления профиля пользователя
    (модели Profile) в контексте авторизованного пользователя
    """
    class Meta:
        model = Profile
        exclude = ['user']


class ProfileImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления всего медиа-контента
    в контексте авторизованного пользователя (НА БУДУЩЕЕ)
    """
    avatar_url = serializers.ImageField(source="avatar", read_only=True)
    wallpaper_url = serializers.ImageField(source="wallpaper", read_only=True)

    class Meta:
        model = Profile
        fields = ['avatar_url', 'wallpaper_url']


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = '__all__'


class ProfileSkillSerializer(serializers.ModelSerializer):
    skill_info = SkillSerializer(source='skill', read_only=True)
    skill_name = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = ProfileSkill
        exclude = ['skill', 'profile']

    def create(self, validated_data):
        skill_name = validated_data.pop('skill_name', None)

        if not skill_name:
            raise serializers.ValidationError({
                "detail": "No skill name!"
            })

        skill, _ = Skill.objects.get_or_create(name=skill_name)

        profile_id = self.context['request'].user.id
        profile = Profile.objects.get(pk=profile_id)

        if ProfileSkill.objects.filter(skill=skill, profile=profile).exists():
            raise serializers.ValidationError({
                "detail": (
                    f"Skill name '{skill.name.upper()}' already exists "
                    f"for profile: {profile.pk}"
                )
            })

        validated_data['profile'] = profile
        validated_data['skill'] = skill
        return super().create(validated_data)


class UpdateProfileSkillSerializer(BaseModelSerializer):

    class Meta:
        model = ProfileSkill
        fields = ['level']


class DeleteProfileSkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileSkill
        exclude = ['skill', 'profile']


class PrivacyProfileSkillSerializer(BaseModelSerializer):

    class Meta:
        model = ProfileSkill
        fields = ['privacy']
