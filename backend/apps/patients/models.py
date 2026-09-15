from django.db import models


class Patient(models.Model):
    """A person receiving care.

    A patient may have multiple CancerCases over a lifetime.
    See docs/domain.md for the full domain model.
    """

    class Sex(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        UNKNOWN = "unknown", "Unknown"

    class VitalStatus(models.TextChoices):
        ALIVE = "alive", "Alive"
        DEAD = "dead", "Dead"

    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.PROTECT,
        related_name="patients",
    )
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    sex = models.CharField(
        max_length=16,
        choices=Sex.choices,
        default=Sex.UNKNOWN,
    )
    medical_record_number = models.CharField(max_length=64)
    contacts = models.JSONField(default=dict, blank=True)
    vital_status = models.CharField(
        max_length=16,
        choices=VitalStatus.choices,
        default=VitalStatus.ALIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "medical_record_number"],
                name="unique_mrn_per_organization",
            ),
        ]
        indexes = [
            models.Index(fields=["organization", "full_name"]),
            models.Index(fields=["medical_record_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.medical_record_number})"
