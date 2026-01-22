import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")

        # normalize email(lowercase domain part e.g GMAIL.COM == gmail.com)
        email = self.normalize_email(email).lower().strip()
        # create user instance with email and extra_fields
        user = self.model(email=email, **extra_fields)
        # hash password
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(
        unique=True, null=True, blank=True, help_text="only for super users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"  # unique identifier

    # superusers must provide username
    REQUIRED_FIELDS = ["username", "full_name"]

    objects = UserManager()

    def __str__(self):
        return self.email
