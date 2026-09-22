from django.db import models


class AuditEvent(models.Model):
    """Security audit trail: who accessed or modified what.

    Every read or write on a medical object is recorded here.
    Used for compliance (HIPAA, GDPR, 152-ФЗ) and investigations.

    Distinct from StatusTransition (which is business logic).
    """

    class Action(models.TextChoices):
        VIEW = "view", "View"
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        DOWNLOAD = "download", "Download"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="audit_events",
        null=True,
        blank=True,
        help_text="User who performed the action (null if anonymous)",
    )
    action = models.CharField(max_length=16, choices=Action.choices)
    entity_type = models.CharField(
        max_length=64,
        help_text="Model name, e.g. 'Patient', 'CancerCase'",
    )
    entity_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text="Primary key of the object (null for lists)",
    )
    entity_repr = models.CharField(
        max_length=255,
        blank=True,
        help_text="Human-readable representation at the time of the event",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.SET_NULL,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    request_method = models.CharField(max_length=8, blank=True)
    request_path = models.CharField(max_length=512, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id", "-timestamp"]),
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["organization", "-timestamp"]),
        ]

    def __str__(self) -> str:
        who = self.user.username if self.user else "anonymous"
        target = self.entity_repr or f"{self.entity_type}#{self.entity_id}"
        return f"{who} {self.action} {target}"
