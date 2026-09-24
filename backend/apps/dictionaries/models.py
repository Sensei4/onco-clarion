from django.db import models


class FoundationEntity(models.Model):
    """ICD-11 foundation entity (semantic layer).

    Source: http://id.who.int/icd/entity/{id}
    Stores: URI, title, definitions, synonyms, parent/child relations.
    No codes — codes are in the MMS layer.
    """

    uri = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="e.g. http://id.who.int/icd/entity/1047754165",
    )
    title = models.CharField(max_length=1024, db_index=True)
    definition = models.TextField(blank=True)
    long_definition = models.TextField(blank=True)
    synonyms = models.JSONField(
        default=list,
        blank=True,
        help_text="List of synonym strings",
    )
    parent_uris = models.JSONField(default=list, blank=True)
    child_uris = models.JSONField(default=list, blank=True)
    exclusions = models.JSONField(
        default=list,
        blank=True,
        help_text="List of {label, uri} dicts",
    )
    browser_url = models.URLField(max_length=512, blank=True)
    chapter = models.CharField(max_length=8, blank=True, db_index=True)
    last_synced_at = models.DateTimeField()

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["chapter"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.uri})"


class MmsEntity(models.Model):
    """ICD-11 MMS (Mortality and Morbidity Statistics) entity.

    Source: http://id.who.int/icd/release/11/{release}/mms/{id}
    Stores: URI, theCode, title, chapter, links to foundation.
    """

    uri = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="e.g. http://id.who.int/icd/release/11/2026-01/mms/1047754165/unspecified",
    )
    foundation_uri = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="Link to the foundation entity",
    )
    the_code = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="e.g. 2C6Z (may include postcoordination, e.g. 2E0Y&XA12C1)",
    )
    title = models.CharField(max_length=1024, db_index=True)
    chapter = models.CharField(max_length=8, blank=True, db_index=True)
    is_leaf = models.BooleanField(default=False)
    is_residual_unspecified = models.BooleanField(default=False)
    is_residual_other = models.BooleanField(default=False)
    parent_uris = models.JSONField(default=list, blank=True)
    child_uris = models.JSONField(default=list, blank=True)
    synonyms = models.JSONField(
        default=list,
        blank=True,
        help_text="Synonym strings extracted from matchingPVs",
    )
    last_synced_at = models.DateTimeField()

    class Meta:
        ordering = ["the_code"]
        indexes = [
            models.Index(fields=["the_code"]),
            models.Index(fields=["chapter"]),
            models.Index(fields=["foundation_uri"]),
        ]

    def __str__(self) -> str:
        code = self.the_code or "—"
        return f"[{code}] {self.title}"


class Icd11SyncLog(models.Model):
    """History of ICD-11 synchronization runs."""

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    release_id = models.CharField(
        max_length=32,
        help_text="e.g. 2026-01",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.RUNNING,
    )
    foundation_count = models.IntegerField(default=0)
    mms_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"Sync {self.release_id} at {self.started_at} ({self.status})"
