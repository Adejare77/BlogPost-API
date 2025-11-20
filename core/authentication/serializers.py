from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from typing import Dict
from django.contrib.auth.base_user import BaseUserManager
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={
        "required": "email field is required",
        "blank": "email cannot be empty",
        "invalid": "invalid email address"
    })
    password = serializers.CharField(
        write_only=True,
        error_messages={
        "required": "password field is required",
        "blank": "password cannot be empty",
    })


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(
        max_length=20,
        error_messages={
            "blank": "full_name cannot be empty",
            "required": "full_name field is required"
        }
        )
    email = serializers.EmailField(error_messages={
        "required": "email field is required",
        "blank": "email cannot be empty",
        "invalid": "invalid email address"
    })
    password = serializers.CharField(
        write_only=True,
        min_length=3,
        error_messages={
            "blank": "password cannot be empty",
            "min_length": "password must be at least 3 characters long",
            "required": "password field is required"
        }
    )

    def validate_email(self, value):
        """ normalize email """
        normalized_email = BaseUserManager().normalize_email(value)
        return normalized_email

    def create(self, validated_data: Dict[str, str]):
        raw_password = validated_data.pop('password')

        try:
            user = get_user_model().objects.create_user(
                email=validated_data['email'],
                password=raw_password,
                **{k: v for k, v in validated_data.items() if k != 'email'}
            )

        except IntegrityError as e:
            raise serializers.ValidationError({"error": "This email is already registered"})

        except DjangoValidationError as e:
            raise serializers.ValidationError({'error': e.message_dict})

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # for Parent TokenObtainPairSerializer, we must override
    # the defined fields in order to have custom errors. No other way
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'] = serializers.EmailField(
            error_messages={
                "blank": "email cannot be empty",
                "required": "email field is required",
                "invalid": "invalid email address"
            })

        self.fields['password'] = serializers.CharField(
            write_only=True,
            error_messages={
                "blank": "password cannot be empty",
                "required": "password field is required",
            }
            )

    def validate(self, attrs):
        password = attrs.get('password')

        # normalize email before authenticating
        email = BaseUserManager().normalize_email(attrs.get('email'))

        user = authenticate(
            request=self.context.get('request'),
            username=email,  # can also use email variable. But username is just unique
            password=password
            )
        if not user:
            raise AuthenticationFailed({'error': 'Invalid email or password'})

        # create token
        refresh = self.get_token(user)

        return {
            'access': str(refresh.access_token),
            # 'refresh': str(refresh),
            'user_id': user.id,
            'email': user.email
        }
