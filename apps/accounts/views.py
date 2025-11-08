from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema_view, extend_schema
from apps.accounts.models import User, Profile
from apps.accounts.serializers import (
    UserSerializer, ProfileSerializer, UserConfirmSerializer,
    MyTokenObtainPairSerializer
)


# @extend_schema_view(
#     list=extend_schema(
#         description="Получить список пользователей",
#         responses={200: UserSerializer(many=True)}
#     ),
#     create=extend_schema(
#         description="Создать нового пользователя",
#         request=UserSerializer,
#         responses={201: UserSerializer}
#     ),
#     retrieve=extend_schema(
#         description="Получить пользователя по ID",
#         responses={200: UserSerializer}
#     ),
#     update=extend_schema(
#         description="Обновить пользователя",
#         request=UserSerializer,
#         responses={200: UserSerializer}
#     ),
#     partial_update=extend_schema(
#         description="Частично обновить пользователя",
#         request=UserSerializer,
#         responses={200: UserSerializer}
#     ),
#     destroy=extend_schema(
#         description="Удалить пользователя"
#     ),
# )


class UserView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'


class UserConfirmView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserConfirmSerializer
    lookup_field = 'pk'


class ProfileView(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'pk'


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
