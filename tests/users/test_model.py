from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        """test creating a normal user"""
        user = User.objects.create_user(**{
            'email': 'test1@gmail.com',
            'password': 'test1',
            'full_name': 'test'
            })
        self.assertEqual(user.email, 'test1@gmail.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """test creating a superuser"""
        user = User.objects.create_superuser(**{
            'email': 'test2@gmail.com',
            'full_name': 'test',
            'password': 'test2'
            })
        self.assertEqual(user.email, 'test2@gmail.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)

    def test_email_normalization(self):
        """test email is normalized"""
        user = User.objects.create_user(**{
            'email': 'test@GMAIl.COm',
            'password': 'test',
            'full_name': 'test'
            })
        self.assertEqual(user.email, 'test@gmail.com')



class UserModelValidationTests(TestCase):
    def test_missing_email_raises_error(self):
        """ test missing email field validation """
        with self.assertRaises(TypeError):
            User.objects.create_user(**{
                'password': 'test1',
                'full_name': 'full test'
            })

    def test_empty_email_raises_error(self):
        """ test empty email validation """
        with self.assertRaises(ValueError):
            User.objects.create_user(**{
                'email': '',
                'password': 'test1',
                'full_name': 'full test'
            })

    def test_missing_full_name_raises_error(self):
        """ test missing full_name validation """
        with self.assertRaises(ValidationError):
            User.objects.create_user(**{
                'email': 'test@gmail.com',
                'password': 'test1',
            })

    def test_empty_full_name_raises_error(self):
        """ test missing full_name validation """
        with self.assertRaises(ValidationError):
            User.objects.create_user(**{
                'email': 'test@gmail.com',
                'password': 'test1',
                'full_name': ''
            })

    def test_missing_password_does_not_raise_error(self):
        """ test missing password validation """
        user = User.objects.create_user(**{
            'email': 'test@gmail.com',
            'full_name': 'mytest'
        })
        self.assertEqual(user.email, "test@gmail.com")

    def test_duplicate_email_raises_error(self):
        """test email does not already exists"""
        User.objects.create_user(**{
            'email': 'unique@gmail.com',
            'password': 'unique1',
            'full_name': 'test'
            })

        with self.assertRaises(ValidationError):
            User.objects.create_user(**{
                'email': 'unique@gmail.com',
                'password': 'unique2',
                'full_name': 'test'
                })
