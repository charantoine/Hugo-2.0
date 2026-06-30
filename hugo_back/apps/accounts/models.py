"""
Accounts: Organisation, User (organisation_id, roles).
All IDs UUIDv4; timestamps UTC.
"""
import os
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class Organisation(models.Model):
    """Multi-tenant organisation (OF)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    default_learner_display_profile = models.CharField(
        max_length=32,
        choices=[
            ("youth", "Youth"),
            ("adult", "Adult"),
            ("professional", "Professional"),
        ],
        default="professional",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organisation"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Role(models.TextChoices):
    LEARNER = "LEARNER", "Learner"
    TUTOR = "TUTOR", "Tutor"
    TRAINER = "TRAINER", "Trainer"
    COORDO = "COORDO", "Coordinateur"
    ORGADMIN = "ORGADMIN", "Admin organisation"
    SUPERADMIN = "SUPERADMIN", "Super admin"


class UserManager(DjangoUserManager):
    """
    Custom manager to make `createsuperuser` workable in a fresh DB:
    - if no organisation is provided, create/get a default Organisation and attach it.
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        if extra_fields.get("organisation") is None:
            default_org_name = os.environ.get("BOOTSTRAP_ORG_NAME", "Default organisation")
            org, _ = Organisation.objects.get_or_create(name=default_org_name)
            extra_fields["organisation"] = org

        extra_fields.setdefault("role", Role.SUPERADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return super().create_superuser(username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    """User tied to one organisation; roles stored on user."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="users",
        null=False,
        blank=False,
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.LEARNER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        db_table = "user"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} ({self.organisation.name})"
