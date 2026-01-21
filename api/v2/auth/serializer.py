from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotAuthenticated
from rest_framework import serializers
from django.contrib.auth import get_user_model
from app.user.models import User
from django.db import IntegrityError


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'] = serializers.EmailField(
            error_messages={
                'required': 'email field is required',
                'blank': 'email cannot be empty',
                'invalid': 'invalid email address'
            }
        )

        self.fields['password'] = serializers.CharField(
            error_messages={
                'required': 'password field is required',
                'blank': 'password cannot be empty',
            }
        )

    def validate(self, attrs):
        password = attrs.get("password")
        email = BaseUserManager().normalize_email(email=attrs.get('email'))

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            raise NotAuthenticated({"detail": "Invalid email or password"})

        refresh = self.get_token(user)

        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'email': user.email
        }

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(error_messages={
        'required': 'email field is required',
        'blank': 'email cannot be empty',
        'invalid': 'invalid email address'
    })
    password = serializers.CharField(
        error_messages={
        'required': 'password field is required',
        'blank': 'password cannot be empty',
        }
    )

    full_name = serializers.CharField(error_messages={
        'required': 'full_name field is required',
        'blank': "full_name cannot be empty",
        'max_length': 'full_name cannot be more than 100 characters'
    })

    class Meta:
        model = get_user_model()
        # model = User
        fields = ['email', 'password', 'full_name']

    def create(self, validated_data):
        try:
            return get_user_model().objects.create_user(**validated_data)
        except IntegrityError as err:
            raise serializers.ValidationError({
                "detail": "This email is already registered"
            }) from err
