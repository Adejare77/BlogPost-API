from django.urls import reverse
from rest_framework import status

from api.v2.auth.views import CreateUserAPIView
from app.user.models import User


def test_register_user_returns_201(db, api_rf):
    url = reverse("v2:sign-up")
    data = {
        "full_name": "TESTING",
        "password": "testing123",
        "email": "testing@gmail.com",
    }
    request = api_rf.post(path=url, data=data, format="json")
    view = CreateUserAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1


def test_register_normalized_email_successfully(db, api_rf):
    url = reverse("v2:sign-up")
    data = {
        "full_name": "TESTING",
        "password": "testing123",
        "email": "TESTING@GMAIL.COM",
    }
    request = api_rf.post(path=url, data=data, format="json")
    view = CreateUserAPIView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get()
    assert user.email == "TESTING@gmail.com"
