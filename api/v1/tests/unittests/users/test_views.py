from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from api.v1.user import views

User = get_user_model()


class UserViewTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.user1 = User.objects.create_user(
            **{
                "email": "user1account@gmail.com",
                "password": "user123",
                "full_name": "john doe",
            }
        )
        self.user2 = User.objects.create_user(
            **{
                "email": "user2account@gmail.com",
                "password": "user123",
                "full_name": "Son",
            }
        )
        self.admin1 = User.objects.create_superuser(
            **{
                "email": "adminaccount1@gmail.com",
                "password": "admin123",
                "full_name": "Administrator",
            }
        )
        self.admin2 = User.objects.create_superuser(
            **{
                "email": "adminaccount2@gmail.com",
                "password": "admin123",
                "full_name": "Administrator",
            }
        )

    def test_user_can_get_own_profile(self):
        """Get user's profile"""
        url = reverse("v1:user-profile", kwargs={"user_id": self.user1.id})
        request = self.factory.get(url)  # gets the request of this url
        force_authenticate(
            request=request, user=self.user1
        )  # authenticate and attach user
        resp = views.get_user_by_id(request, user_id=self.user1.id)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_user_cannot_get_other_user_profile(self):
        url = reverse("v1:user-profile", kwargs={"user_id": self.user1.id})
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user1)
        response = views.get_user_by_id(request, user_id=self.user2.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_get_regular_users_profile(self):
        url = reverse("v1:user-profile", kwargs={"user_id": self.admin1.id})
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.admin1)

        resp = views.get_user_by_id(request, user_id=self.user1.id)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = views.get_user_by_id(request, user_id=self.user2.id)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_admin_can_get_own_profile(self):
        url = reverse("v1:user-profile", kwargs={"user_id": self.admin1.id})
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.admin1)

        resp = views.get_user_by_id(request, user_id=self.admin1.id)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_admin_cannot_get_other_admin_profile(self):
        url = reverse("v1:user-profile", kwargs={"user_id": self.admin1.id})
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.admin1)
        response = views.get_user_by_id(request, user_id=self.admin2.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "You do not have permission to perform this action",
            response.data.get("detail"),
        )

    def test_user_cannot_disable_any_account(self):
        url = reverse("v1:disable-account", kwargs={"user_id": self.user1.id})
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user1)

        # deleting owner's account
        response = views.disable_user_account(request, user_id=self.user1.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # deleting other client's account
        response = views.disable_user_account(request, user_id=self.user2.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # deleting admin account
        response = views.disable_user_account(request, user_id=self.admin1.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_disable_user_account(self):
        url = reverse("v1:disable-account", kwargs={"user_id": self.user1.id})
        request = self.factory.post(url)
        force_authenticate(request=request, user=self.admin1)

        resp = views.disable_user_account(request, user_id=self.user1.id)
        self.assertAlmostEqual(resp.status_code, status.HTTP_200_OK)

    def test_admin_cannot_disable_other_admin_account(self):
        url = reverse("v1:disable-account", kwargs={"user_id": self.admin1.id})
        request = self.factory.post(url)
        force_authenticate(request=request, user=self.admin1)
        response = views.disable_user_account(request, user_id=self.admin2.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_enable_any_account(self):
        url = reverse("v1:enable-account", kwargs={"user_id": self.user1.id})
        request = self.factory.get(url)
        force_authenticate(request=request, user=self.user1)

        response = views.disable_user_account(request, user=self.user1.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = views.disable_user_account(request, user=self.user2.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = views.disable_user_account(request, user=self.admin1.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_enable_user_account(self):
        url = reverse("v1:enable-account", kwargs={"user_id": self.user1.id})
        request = self.factory.post(url)
        force_authenticate(request=request, user=self.admin1)
        response = views.enable_user_account(request, user_id=self.user1.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_cannot_enable_admin_account(self):
        url = reverse("v1:enable-account", kwargs={"user_id": self.admin1.id})
        request = self.factory.post(url)
        force_authenticate(request=request, user=self.admin1)
        resp = views.enable_user_account(request, user_id=self.admin2.id)

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
