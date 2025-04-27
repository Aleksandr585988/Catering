from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .enums import Role


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        """Create and save a user with passed parameters."""

        email = self.normalize_email(email)
        password = make_password(password)

        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False
        extra_fields.setdefault("is_active", False)  # Initially the user is inactive
        extra_fields["role"] = Role.CLIENT

        user = self.model(email=email, password=password, **extra_fields)
        user.save()

        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        """Create and save a user with passed parameters."""

        email = self.normalize_email(email)
        password = make_password(password)

        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields.setdefault("is_active", True)  # Admins are active at once
        extra_fields["role"] = Role.ADMIN

        user = self.model(email=email, password=password, **extra_fields)
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

        return self.email

    email = models.EmailField(max_length=255, unique=True, null=False)
    phone_number = models.CharField(max_length=10, unique=True, null=False)
    first_name = models.CharField(max_length=20, null=False)
    last_name = models.CharField(max_length=50, null=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    role = models.CharField(
        max_length=10,
        choices=Role.choices(),
        default=Role.CLIENT,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
