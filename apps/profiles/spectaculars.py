from rest_framework import serializers
from rest_framework.exceptions import status  # type: ignore
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from drf_spectacular.utils import (
    inline_serializer, extend_schema, extend_schema_view,
    OpenApiResponse, OpenApiExample
)
from drf_spectacular.extensions import OpenApiViewExtension

from apps.profiles.serializers import (
    ProfileSerializer, UpdateProfileSerializer, SkillSerializer
)

from apps.CONSTANTS import NOT_AUTHENTICATED, PERMISSION_DENIED, NOT_FOUND
from docs.utils import read_md_section


class FixProfilesView(OpenApiViewExtension):
    """
    Фиксируется документация для ProfilesView
    """
    target_class = 'apps.profiles.viewsets.ProfilesView'

    def view_replacement(self) -> type[APIView]:

        @extend_schema_view(
            list=extend_schema(
                summary="Запрос списка профилей",
                description=read_md_section(
                    'api/profiles.md', 'GET /profiles/'
                ),
                responses={
                    status.HTTP_200_OK: ProfileSerializer,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED,
                    status.HTTP_404_NOT_FOUND: NOT_FOUND,
                },
            ),
            education_levels=extend_schema(
                summary="Список уровней образования",
                description=read_md_section(
                    'api/profiles.md', 'GET /profiles/displays/education-levels/'
                ),
                responses={
                    status.HTTP_200_OK: inline_serializer(
                        name='education_levels_response',
                        fields={
                            'level_1': serializers.CharField(),
                            'level_2': serializers.CharField(),
                            'levels...': serializers.CharField(),
                            'level_N': serializers.CharField(),
                        }
                    ),
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED
                },
            ),
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixUserProfileView(OpenApiViewExtension):
    """
    Фиксируется документация для UserProfileView
    """
    target_class = 'apps.profiles.views.UserProfileView'

    def view_replacement(self) -> type[APIView]:

        @extend_schema_view(
            
            # examples_response=[
            #     OpenApiExample(
            #         name='Базовые параметры для тела ответа',
            #         value={'user': 1, 'name': 'New User', 'email': 'new@example.com'},
            #         response_only=True, # Указываем, что это пример для ответа
            #         status_codes=['201'] # Привязываем к конкретному статус-коду
            #     )
            # ],
            get=extend_schema(
                summary="Запрос данных о пользователе",
                description=read_md_section(
                    'api/profiles.md', 'GET /profiles/{id}/'
                ),
                responses={
                    status.HTTP_200_OK: ProfileSerializer,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED,
                    status.HTTP_404_NOT_FOUND: NOT_FOUND,
                }
            ),
            post=extend_schema(
                summary="Обновление своего профиля",
                description=read_md_section(
                    'api/profiles.md', 'POST /profiles/{id}/'
                ),
                request=UpdateProfileSerializer,
                responses={
                    status.HTTP_200_OK: UpdateProfileSerializer,
                    status.HTTP_400_BAD_REQUEST: inline_serializer(
                        name='ProfileValidationError',
                        fields={
                            'errors': serializers.ListField(),
                        }
                    ),
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED
                },
                examples=[
                    OpenApiExample(
                        name='BaseRequestBodyFields',
                        value={
                            'first_name': 'Danielle',
                            'middle_name': 'Angel',
                            'last_name': 'Hill',
                            'profession': 'Environmental health practitioner',
                            'city': 'Robinsonshire',
                            'country': 'Fiji',
                            'relocation': 'Sudan, Port Lindachester',
                            'institution_name': 'Doyle Ltd',
                            'graduation_year': 2011,
                            'short_desc': 'Choice whatever from behavior benefit.',
                            'full_desc': 'Choice whatever from behavior benefit. Page southern role movie win her. Fall pick those gun court attorney product. World talk term herself law. Class great prove reduce raise author. Move each left establish. Detail food shoulder argue start source husband. Decision wall then fire. How trip learn enter east no enjoy. Investment on gun young catch management sense technology. Physical society instead as. Other life edge network wall quite. Race Mr environment political. Fall citizen about reveal. Will seven medical blood personal. Participant check several much single morning a. Major born guy world southern dream. There water beat magazine attorney. She campaign little near enter their institution. Up sense ready require human.',
                            'wallpaper': 'wallpaper.jpeg',
                            'avatar': 'avatar.jpeg',
                            'link_to_instagram': 'https://t.me/garzaanthony',
                            'link_to_telegram': 'https://t.me/garzaanthony',
                            'link_to_github': 'https://github.com/robinsonwilliam',
                            'link_to_vk': 'https://vk.com/hoffmanjennifer',
                        },
                        request_only=True,
                    )
                ]
            ),
            delete=extend_schema(
                summary="Удаление профиля пользователя",
                description=read_md_section(
                    'api/profiles.md', 'DELETE /profiles/{id}/'
                ),
                responses={
                    status.HTTP_204_NO_CONTENT: OpenApiResponse(),
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED
                }
            ),
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixSkillViewSet(OpenApiViewExtension):
    """
    Расширяется документация для SkillViewSet
    """
    target_class = 'apps.profiles.viewsets.SkillViewSet'

    def view_replacement(self) -> type[ModelViewSet]:
        @extend_schema_view(
            list=extend_schema(
                summary="Получить уровень образования",
                description=read_md_section(
                    'api/profiles.md', 'GET /profiles/displays/skills/'
                ),
                responses={
                    status.HTTP_200_OK: SkillSerializer,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED
                }
            )
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixWorkFormatView(OpenApiViewExtension):
    """
    Расширяется документация для WorkFormatView
    """
    target_class = 'apps.profiles.viewsets.WorkFormatView'

    def view_replacement(self) -> type[ModelViewSet]:
        @extend_schema_view(
            retrieve=extend_schema(
                summary="Предпочитаемые форматы работы",
                description=read_md_section(
                    'api/profiles.md', 'GET /profiles/{profile}/work_formats/'
                )
            ),
            partial_update=extend_schema(
                summary="Изменение форматов работы",
                description=read_md_section(
                    'api/profiles.md', 'PATCH /profiles/{profile}/work_formats/'
                )
            )
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixProfileSkillViewSet(OpenApiViewExtension):
    """
    Расширяется документация для ProfileSkillViewSet
    """
    target_class = 'apps.profiles.viewsets.ProfileSkillViewSet'

    def view_replacement(self) -> type[ModelViewSet]:
        @extend_schema_view(
            list=extend_schema(
                summary="Получение списка навыков",
                description=read_md_section(
                    'api/profiles.md', 'GET /profiles/{profile}/skills/'
                )
            ),
            create=extend_schema(
                summary="Добавление новых навыков",
                description=read_md_section(
                    'api/profiles.md', 'POST /profiles/{profile}/skills/'
                )
            ),
            partial_update=extend_schema(
                summary="Изменение уровня владения навыком",
                description=read_md_section(
                    'api/profiles.md',
                    'PATCH /profiles/{profile}/skills/{skill}/level/'
                )
            ),
            destroy=extend_schema(
                summary="Удаление навыка из профиля",
                description=read_md_section(
                    'api/profiles.md',
                    'DELETE /profiles/{profile}/skills/{skill}/level/'
                )
            )
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixPrivacyProfileSkillViewSet(OpenApiViewExtension):
    """
    Расширяется документация для PrivacyProfileSkillViewSet
    """
    target_class = 'apps.profiles.viewsets.PrivacyProfileSkillViewSet'

    def view_replacement(self) -> type[ModelViewSet]:
        @extend_schema_view(
            retrieve=extend_schema(
                summary="Получение настроек конфиденциальности",
                description=read_md_section(
                    'api/profiles.md',
                    'GET /profiles/{profile}/skills/{skill}/privacy/'
                )
            ),
            partial_update=extend_schema(
                summary="Изменение настроек конфиденциальности",
                description=read_md_section(
                    'api/profiles.md',
                    'PATCH /profiles/{profile}/skills/{skill}/privacy/'
                )
            ),
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed
