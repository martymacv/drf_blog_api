from django.urls import path

from django.views.generic import TemplateView

from apps.profiles.views import UserProfileView
from apps.profiles.viewsets import (
    WorkFormatView, ProfilesView,
    ProfileSkillViewSet, SkillViewSet, PrivacyProfileSkillViewSet
)

urlpatterns = [
    path(
        '',
        ProfilesView.as_view({'get': 'list'}),
        name='get_all_user_profiles'
    ),
    path(
        '<int:pk>/', UserProfileView.as_view(),
        name='rw_user_profile'
    ),
    path(
        '<int:profile>/work_formats/',
        WorkFormatView.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='update_user_work_formats'
    ),
    path(
        '<int:profile>/skills/',
        ProfileSkillViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='get_profile_skills'
    ),
    path(
        '<int:profile>/skills/<int:skill>/level/',
        ProfileSkillViewSet.as_view({
            'patch': 'partial_update', 'delete': 'destroy'
        }),
        name='destroy_profile_skill'
    ),
    path(
        '<int:profile>/skills/<int:skill>/privacy/',
        PrivacyProfileSkillViewSet.as_view({
            'get': 'retrieve', 'patch': 'partial_update'
        }),
        name='update_skill_privacy_setting'
    ),
    path(
        'displays/education-levels/',
        ProfilesView.as_view({'get': 'education_levels'}),
        name='update_user_profile'
    ),
    path(
        'displays/skills/',
        SkillViewSet.as_view({'get': 'list'}),
        name='get_skill_list'
    ),
]
