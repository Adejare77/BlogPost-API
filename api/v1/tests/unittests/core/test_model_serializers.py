from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APITestCase

from app.core.authentication.serializers import (
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    RegisterSerializer,
)

User = get_user_model()


class CoreLoginSerializerTests(APITestCase):
    def test_login_serializer(self):
        """Test login serializer"""
        data = {"email": "test@gmail.com", "password": "testing"}
        serializer = LoginSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_login_without_email(self):
        """Test without email field"""
        data = {"password": "testing"}
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual("email field is required", serializer.errors.get("email")[0])

    def test_login_with_empty_email(self):
        """Test with empty email field"""
        data = {"email": "", "password": "testing"}
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email cannot be empty", serializer.errors.get("email"))

    def test_login_with_invalid_email(self):
        """Test with invalid email field"""
        data = {"email": "tsesting@gmailcom", "password": "testing"}
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("invalid email address", serializer.errors.get("email"))

    def test_login_without_password_field(self):
        """Test without password field"""
        data = {"email": "testing@gmail.com"}
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "password field is required", serializer.errors.get("password")[0]
        )

    def test_login_with_empty_password(self):
        """Test with empty password"""
        data = {"email": "testing@gmail.com", "password": ""}
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "password cannot be empty", serializer.errors.get("password")[0]
        )


class CoreRegistrationSerializerTests(APITestCase):
    def test_registration_serializer(self):
        """Test registration serializer"""
        data = {"full_name": "ABC", "email": "testing@gmail.com", "password": "123"}
        serializer = RegisterSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_registration_without_full_name(self):
        """Test without full_name field"""
        data = {"email": "testing@gmail.com", "password": "123"}
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "full_name field is required", serializer.errors.get("full_name")[0]
        )

    def test_registration_with_empty_full_name(self):
        """Test with empty full_name"""
        data = {"full_name": "", "email": "testing@gmail.com", "password": "123"}
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("full_name cannot be empty", serializer.errors.get("full_name"))

    def test_registration_without_email(self):
        """Test without email field"""
        data = {"full_name": "ABC", "password": "123"}
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email field is required", serializer.errors.get("email"))

    def test_registration_with_empty_email(self):
        """Test with empty email"""
        data = {"full_name": "ABC", "email": "", "password": "123"}
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email cannot be empty", serializer.errors.get("email"))

    def test_registration_with_invalid_email(self):
        """Test with invalid email"""
        data = {"full_name": "ABC", "email": "invalidEmail", "password": "123"}
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("invalid email address", serializer.errors.get("email"))

    def test_registration_email_normailization(self):
        """Test email normalization"""
        data = {"full_name": "ABC", "email": "testing@GMAIL.COM", "password": "123"}
        serializer = RegisterSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual("testing@gmail.com", serializer.data.get("email"))

    def test_registration_without_password_field(self):
        """Test without password field"""
        data = {"full_name": "ABC", "email": "testing@gmail.com"}
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "password field is required", serializer.errors.get("password")[0]
        )

    def test_registration_with_empty_password(self):
        """Test with empty password"""
        data = {"full_name": "ABC", "email": "testing@gmail.com", "password": ""}
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "password cannot be empty", serializer.errors.get("password")[0]
        )

    def test_registration_with_less_than_3_characters_password(self):
        """Test with empty password"""
        data = {"full_name": "ABC", "email": "testing@gmail.com", "password": "12"}
        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "password must be at least 3 characters long",
            serializer.errors.get("password"),
        )


class CoreCustomTokenObtainPairSerializerTests(APITestCase):
    def setUp(self):
        """Setup test cases"""
        data = {"full_name": "ABC", "email": "testing@gmail.com", "password": "123"}
        self.user = User.objects.create_user(**data)

    def test_token_obtain_pair_serializer(self):
        """Test token obtain serializer"""
        data = {"email": "testing@gmail.com", "password": "123"}
        serializer = CustomTokenObtainPairSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "testing@gmail.com")

    def test_token_obtain_without_email(self):
        """Test without email field"""
        data = {"password": "123"}
        serializer = CustomTokenObtainPairSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email field is required", str(serializer.errors.get("email")))

    def test_token_obtain_with_empty_email(self):
        """Test with empty email"""
        data = {"email": "", "password": "123"}
        serializer = CustomTokenObtainPairSerializer(data=data)

        serializer.is_valid()
        self.assertIn("email cannot be empty", str(serializer.errors))

    def test_token_obtain_with_invalid_email(self):
        """Test with invalid email"""
        data = {"email": "invalidEmail", "password": "123"}
        serializer = CustomTokenObtainPairSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("invalid email address", str(serializer.errors.get("email")))

    def test_token_obtain_email_normalization(self):
        """Test email normalization"""
        data = {"email": "testing@GMAIL.COM", "password": "123"}
        serializer = CustomTokenObtainPairSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual("testing@gmail.com", serializer.validated_data.get("email"))

    def test_token_obtain_without_password_field(self):
        """Test without password field"""
        data = {"email": "testing@gmail.com"}
        serializer = CustomTokenObtainPairSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "password field is required", serializer.errors.get("password")[0]
        )

    def test_token_obtain_with_empty_password(self):
        """Test with empty password"""
        data = {"email": "testing@gmail.com", "password": ""}
        serializer = CustomTokenObtainPairSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "password cannot be empty", serializer.errors.get("password")[0]
        )

    def test_token_obtain_with_disabled_account(self):
        """Test disabled or inactive account"""
        data = {
            "full_name": "ABCD",
            "email": "testing2@gmail.com",
            "password": "123",
            "is_active": False,
        }
        User.objects.create_user(**data)

        data = {"email": "testing2@gmail.com", "password": "123"}
        serializer = CustomTokenObtainPairSerializer(data=data)

        with self.assertRaisesMessage(
            AuthenticationFailed, "Invalid email or password"
        ):
            serializer.is_valid()
