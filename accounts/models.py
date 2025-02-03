from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from estate_agency.models import BaseModel


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    first_name = models.CharField(blank=True, null=True, max_length=150)
    last_name = models.CharField(blank=True, null=True, max_length=150)
    phone = models.CharField(blank=True, null=True, max_length=15)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    image = models.ImageField(upload_to="avatar/", default="avatar/avatar.png")

    on_delete = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []
    history = HistoricalRecords()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        default_permissions = ("add", "change", "view")
        permissions = (
            ("profile", "Profile"),
        )

    def get_full_name(self):
        return self.first_name, self.last_name, self.email

    def get_short_name(self):
        return self.email

    def set_active(self) -> None:
        """Set is_active to True and save"""
        self.is_active = True
        self.save()


class CustomGroup(Group, BaseModel):
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        default_permissions = ("add", "change", "view")
