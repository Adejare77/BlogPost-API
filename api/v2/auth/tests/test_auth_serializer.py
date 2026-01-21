from django.urls import reverse
from api.v2.auth.serializer import RegisterSerializer
import pytest
from rest_framework import serializers

def test_valid_data_validates_successfully():
    data = {
        'full_name': "TESTING",
        'password': 'testing123',
        'email': 'testing@gmail.com'
    }
    serializer = RegisterSerializer(data=data)
    assert serializer.is_valid() is True

def test_register_with_empty_email_fails():
    data = {
        'full_name': "TESTING",
        'password': 'testing123',
        'email': '',
    }

    serializer = RegisterSerializer(data=data)

    with pytest.raises(serializers.ValidationError) as err:
        serializer.is_valid(raise_exception=True)

    assert "email cannot be empty" in err.value.detail['email'][0]

def test_register_with_invalid_email_fails():
    data = {
        'full_name': "TESTING",
        'password': 'testing123',
        'email': 'invalid_email',
    }
    serializer = RegisterSerializer(data=data)

    with pytest.raises(serializers.ValidationError) as err:
        serializer.is_valid(raise_exception=True)

    assert "invalid email address" in err.value.detail['email'][0]

def test_register_with_missing_email_fails():
    data = {
        'full_name': "TESTING",
        'password': 'testing123',
    }
    serializer = RegisterSerializer(data=data)

    with pytest.raises(serializers.ValidationError) as err:
        serializer.is_valid(raise_exception=True)

    assert "email field is required" in err.value.detail['email'][0]

def test_register_with_empty_full_name_fails():
    data = {
        'full_name': "",
        'password': 'testing123',
        'email': 'testing@gmail.com',
    }

    serializer = RegisterSerializer(data=data)

    with pytest.raises(serializers.ValidationError) as err:
        serializer.is_valid(raise_exception=True)

    assert "full_name cannot be empty" in err.value.detail['full_name'][0]


def test_register_with_missing_full_name_fails():
    data = {
        'password': 'testing123',
        'email': 'testing@gmail.com'
    }
    serializer = RegisterSerializer(data=data)

    with pytest.raises(serializers.ValidationError) as err:
        serializer.is_valid(raise_exception=True)

    assert "full_name field is required" in err.value.detail['full_name'][0]

def test_register_with_empty_password_fails():
    data = {
        'full_name': "TESTING",
        'password': '',
        'email': 'testing@gmail.com',
    }

    serializer = RegisterSerializer(data=data)

    with pytest.raises(serializers.ValidationError) as err:
        serializer.is_valid(raise_exception=True)

    assert "password cannot be empty" in err.value.detail['password'][0]


def test_register_with_missing_password_fails():
    data = {
        'full_name': "TESTING",
        'email': 'testing@gmail.com'
    }
    serializer = RegisterSerializer(data=data)

    with pytest.raises(serializers.ValidationError) as err:
        serializer.is_valid(raise_exception=True)

    assert "password field is required" in err.value.detail['password'][0]
