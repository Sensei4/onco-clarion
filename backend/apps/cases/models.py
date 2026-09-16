from django.db import models
from django_fsm import FSMField


class CancerCase(models.Model):
    """One primary tumor with its metastases.

    A patient may have multiple CancerCases over a lifetime.
    The `status` field drives the patient flow through queues
    (see docs/domain.md). Transitions are defined in a later step.
    """

    class Status(models.TextChoices):
        NEW = "new", "New"
        DIAGNOSTIC = "diagnostic", "Diagnostic"
        CONSILIUM = "consilium", "Consilium"
        WAITING_HOSPITALIZATION = (
            "waiting_hospitalization",
            "Waiting for hospitalization",
        )
        IN_TREATMENT = "in_treatment", "In treatment"
        OBSERVATION = "observation", "Observation"
        REMISSION = "remission", "Remission"
        RELAPSE = "relapse", "Relapse"
        TERMINAL = "terminal", "Terminal"

    id = models.BigAutoField(primary_key=True)
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="cases",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.PROTECT,
        related_name="cases",
    )
    diagnosis_code = models.CharField(
        max_length=64,
        blank=True,
        help_text="ICD-O-3 morphology + ICD-10 topography",
    )
    diagnosis_text = models.TextField(blank=True)
    verification_date = models.DateField(null=True, blank=True)

    tnm_t = models.CharField(max_length=8, blank=True)
    tnm_n = models.CharField(max_length=8, blank=True)
    tnm_m = models.CharField(max_length=8, blank=True)
    stage = models.CharField(
        max_length=8,
        blank=True,
        help_text="I, II, III, IV, or empty if unknown",
    )

    status = FSMField(
        max_length=32,
        choices=Status.choices,
        default=Status.NEW,
        protected=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["patient", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Case #{self.pk} — {self.patient.full_name} ({self.status})"
