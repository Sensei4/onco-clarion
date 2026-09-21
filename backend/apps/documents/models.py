import os

from django.db import models


def document_upload_path(instance: "Document", filename: str) -> str:
    """Organize uploaded files by case.

    Result: media/documents/case_<id>/<original_filename>
    """
    return f"documents/case_{instance.case_id}/{filename}"


class Document(models.Model):
    """A file attached to a cancer case.

    Files are stored on the filesystem (or S3 in production).
    The database holds only metadata and the file path.

    See docs/domain.md for the full model.
    """

    class Type(models.TextChoices):
        CONCLUSION = "conclusion", "Conclusion"
        SCAN = "scan", "Scan"
        ANALYSIS = "analysis", "Analysis"
        HISTOLOGY = "histology", "Histology"
        OTHER = "other", "Other"

    id = models.BigAutoField(primary_key=True)
    case = models.ForeignKey(
        "cases.CancerCase",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        related_name="documents",
        null=True,
        blank=True,
        help_text="The event during which the document was attached",
    )
    referral = models.ForeignKey(
        "referrals.Referral",
        on_delete=models.SET_NULL,
        related_name="documents",
        null=True,
        blank=True,
        help_text="The referral this document is a result of",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.PROTECT,
        related_name="documents",
    )
    type = models.CharField(
        max_length=32,
        choices=Type.choices,
        default=Type.OTHER,
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short description, e.g. 'CT chest report'",
    )
    file = models.FileField(upload_to=document_upload_path)
    original_filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=128, blank=True)
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Size in bytes",
    )
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="uploaded_documents",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["organization", "-uploaded_at"]),
            models.Index(fields=["case", "-uploaded_at"]),
        ]

    def __str__(self) -> str:
        return self.title or os.path.basename(self.file.name) or f"Document #{self.pk}"

    def save(self, *args, **kwargs):
        # Auto-fill original_filename and file_size on first save
        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except (OSError, ValueError):
                self.file_size = None
        super().save(*args, **kwargs)
