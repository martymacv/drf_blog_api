from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.accounts.models import User, Profile


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'pk', 'email', 'password', 'is_comfirmed'
        ]
        # read_only_fields = [
        #     'pk', 'email', 'is_comfirmed'
        # ]

    def create(self, validated_data):
        # validated_data.pop('password2')
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


class UserConfirmSerializer(serializers.Serializer):
    email = serializers.CharField(read_only=True)
    confirm_code = serializers.CharField(write_only=True)

    def validate_confirm_code(self, confirm_code):
        if confirm_code != 'TESTCODE':
            raise serializers.ValidationError(
                "Неверный код подтверждения"
            )
        return confirm_code

    def update(self, instance, validated_data):
        instance.is_comfirmed = True
        instance.save()
        return instance

    def create(self, validated_data):
        pass


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # if user.is_staff:
        #     token['group'] = 'admin'
        # else:
        #     token['group'] = 'user'
        #     token['role'] = user.account_type

        return token

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
