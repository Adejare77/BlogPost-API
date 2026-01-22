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
    assert user.email == "testing@gmail.com"


def test_duplicate_emails_the_same_domain_case_returns_400(db, api_rf):
    url = reverse("v2:sign-up")
    data = {
        "full_name": "TESTING",
        "password": "testing123",
        "email": "TESTING@GMAIL.COM",
    }
    view = CreateUserAPIView.as_view()

    request1 = api_rf.post(path=url, data=data, format="json")
    # create first email
    response = view(request1)
    assert response.status_code == status.HTTP_201_CREATED

    request2 = api_rf.post(path=url, data=data, format="json")
    # duplicate email
    response = view(request2)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data["email"][0]


def test_duplicate_email_diff_domain_case_returns_400(db, api_rf):
    url = reverse("v2:sign-up")
    data = {
        "full_name": "TESTING",
        "password": "testing123",
        "email": "testing@gmail.com",
    }
    view = CreateUserAPIView.as_view()

    request1 = api_rf.post(path=url, data=data, format="json")
    # create first email
    response = view(request1)
    assert response.status_code == status.HTTP_201_CREATED

    data = {
        "full_name": "TESTING",
        "password": "testing123",
        "email": "Testing@GMAIL.COM",
    }
    request2 = api_rf.post(path=url, data=data, format="json")
    # duplicate email
    response = view(request2)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data["email"][0]
