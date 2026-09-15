from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    """A clinic, dispensary, or hospital."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """Custom user model. Replaces Django's default User."""

    class Role(models.TextChoices):
        DOCTOR = "doctor", "Doctor"
        ADMIN = "admin", "Admin"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.DOCTOR,
    )

    def __str__(self) -> str:
        return self.full_name or self.username
