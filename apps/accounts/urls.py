from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)
from apps.accounts.views import (
    UserView, UserConfirmView, ProfileView, MyTokenObtainPairView
)


urlpatterns = [
    path(
        'user/', UserView.as_view({'get': 'list', 'post': 'create'}),
        name='user_registration'
    ),
    path(
        'user/<pk>', UserView.as_view({'get': 'retrieve', 'put': 'update'}),
        name='user_credantional'
    ),
    path(
        'user/<pk>/confirm', UserConfirmView.as_view({'put': 'update'}),
        name='user_confirm'
    ),
    path(
        'user/token/', MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'user/token/refresh/', TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'user/token/verify/', TokenVerifyView.as_view(),
        name='token_verify'
    ),
    path(
        'profile/', ProfileView.as_view({'get': 'list'}),
        name='profiles'
    ),
    path(
        'profile/<pk>/', ProfileView.as_view({'get': 'list'}),
        name='user_profile'
    ),
]
