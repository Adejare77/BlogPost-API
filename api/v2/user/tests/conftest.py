import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory


@pytest.fixture
def users(db):
    user_1 = get_user_model().objects.create_user(
        full_name="Testing1", password="HashTesting", email="Testing1@gmail.com"
    )
    user_2 = get_user_model().objects.create_user(
        full_name="Testing2", password="HashTesting", email="Testing2@gmail.com"
    )
    admin = get_user_model().objects.create_superuser(
        full_name="Admin", password="HashTestingAdmin", email="admin@gmail.com"
    )

    return {
        "user_1": user_1,
        "user_2": user_2,
        "admin": admin,
    }


@pytest.fixture
def api_rf(db):
    return APIRequestFactory()
