from django.db import models


class Referral(models.Model):
    """A request for a diagnostic procedure in a cancer case.

    Unlike Event (which records what happened), a Referral records
    what needs to be done: a lab test, histology, cytology, imaging.
    It has its own lifecycle and can be completed or cancelled
    independently of the Event that created it.

    See docs/domain.md for the full model.
    """

    class Type(models.TextChoices):
        LAB = "lab", "Laboratory test"
        HISTOLOGY = "histology", "Histology"
        CYTOLOGY = "cytology", "Cytology"
        IMAGING = "imaging", "Imaging"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ORDERED = "ordered", "Ordered"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.BigAutoField(primary_key=True)
    case = models.ForeignKey(
        "cases.CancerCase",
        on_delete=models.PROTECT,
        related_name="referrals",
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        related_name="referrals",
        null=True,
        blank=True,
        help_text="The event during which the referral was issued",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.PROTECT,
        related_name="referrals",
    )
    type = models.CharField(
        max_length=32,
        choices=Type.choices,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ORDERED,
    )
    ordered_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="referrals_ordered",
    )
    ordered_at = models.DateTimeField(auto_now_add=True)

    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short description, e.g. 'CT chest with contrast'",
    )
    notes = models.TextField(blank=True)

    result_text = models.TextField(
        blank=True,
        help_text="Result of the procedure (free text in MVP)",
    )
    result_received_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    completed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="referrals_completed",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-ordered_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["case", "-ordered_at"]),
        ]

    def __str__(self) -> str:
        label = self.title or self.get_type_display()
        return f"{label} #{self.pk} ({self.status})"
