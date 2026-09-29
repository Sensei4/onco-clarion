from django.db import models


class DiagnosticDepartment(models.Model):
    """A diagnostic department within an organization.

    Examples: Clinical laboratory, Cytology, Radiology, Endoscopy,
    Molecular diagnostics, Day surgery.

    Departments are organization-scoped: each clinic defines its own.
    """

    class Category(models.TextChoices):
        LABORATORY = "laboratory", "Laboratory"
        PATHOLOGY = "pathology", "Pathology / Morphology"
        IMAGING = "imaging", "Radiology / Imaging"
        ENDOSCOPY = "endoscopy", "Endoscopy"
        FUNCTIONAL = "functional", "Functional diagnostics"
        SURGERY = "surgery", "Day surgery"
        MOLECULAR = "molecular", "Molecular diagnostics"
        OTHER = "other", "Other"

    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.PROTECT,
        related_name="diagnostic_departments",
    )
    name = models.CharField(max_length=128)
    category = models.CharField(
        max_length=32,
        choices=Category.choices,
        default=Category.OTHER,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_department_name_per_org",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_category_display()})"


class DiagnosticMethod(models.Model):
    """A diagnostic method available in a department.

    Examples: CT, MRI (Radiology); CBC, biochemistry (Laboratory);
    gastroscopy (Endoscopy).
    """

    id = models.BigAutoField(primary_key=True)
    department = models.ForeignKey(
        DiagnosticDepartment,
        on_delete=models.CASCADE,
        related_name="methods",
    )
    code = models.CharField(
        max_length=32,
        blank=True,
        help_text="Short code, e.g. 'CT', 'CBC'",
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["department", "is_active"]),
        ]

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.name}"
        return self.name


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
        blank=True,
        help_text="Denormalized from department category for quick filters",
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
        help_text="Short description, denormalized from method name",
    )
    notes = models.TextField(blank=True)

    # New fields (Stage 16)
    department = models.ForeignKey(
        DiagnosticDepartment,
        on_delete=models.SET_NULL,
        related_name="referrals",
        null=True,
        blank=True,
        help_text="The department performing the procedure",
    )
    method = models.ForeignKey(
        DiagnosticMethod,
        on_delete=models.SET_NULL,
        related_name="referrals",
        null=True,
        blank=True,
        help_text="The specific diagnostic method",
    )
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="assigned_referrals",
        null=True,
        blank=True,
        help_text="The doctor who will perform the procedure",
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the procedure is scheduled",
    )
    room = models.CharField(
        max_length=32,
        blank=True,
        help_text="Room or cabinet number",
    )

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
            models.Index(fields=["department", "status"]),
        ]

    def __str__(self) -> str:
        label = self.title or self.get_type_display()
        return f"{label} #{self.pk} ({self.status})"
