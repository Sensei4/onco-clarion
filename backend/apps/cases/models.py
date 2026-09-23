from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition


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

    # -----------------------------------------------------------------------
    # State machine transitions
    #
    # Each method is a valid transition of the case status.
    # `source` lists allowed from-states. If the case is not in one of them,
    # `TransitionNotAllowed` is raised.
    #
    # Every transition accepts:
    #   - by_user: User who triggered it (may be None for automated)
    #   - reason: optional free-text reason (stored in StatusTransition)
    #
    # The actual StatusTransition record is created in the signal handler.
    # -----------------------------------------------------------------------

    @transition(
        field=status,
        source=[Status.NEW],
        target=Status.DIAGNOSTIC,
    )
    def start_diagnostics(self, by_user=None, reason=""):
        """Move from new to diagnostic (start of workup)."""
        self._last_transition = (by_user, reason)

    @transition(
        field=status,
        source=[Status.DIAGNOSTIC],
        target=Status.CONSILIUM,
    )
    def schedule_consilium(self, by_user=None, reason=""):
        """Move from diagnostic to consilium (ready for tumor board)."""
        self._last_transition = (by_user, reason)

    @transition(
        field=status,
        source=[Status.CONSILIUM],
        target=Status.WAITING_HOSPITALIZATION,
    )
    def approve_hospitalization(self, by_user=None, reason=""):
        """Move from consilium to waiting list for hospitalization."""
        self._last_transition = (by_user, reason)

    @transition(
        field=status,
        source=[Status.WAITING_HOSPITALIZATION],
        target=Status.IN_TREATMENT,
    )
    def admit_to_hospital(self, by_user=None, reason=""):
        """Move from waiting list to in-treatment (admitted)."""
        self._last_transition = (by_user, reason)

    @transition(
        field=status,
        source=[Status.IN_TREATMENT],
        target=Status.OBSERVATION,
    )
    def complete_treatment(self, by_user=None, reason=""):
        """Move from in-treatment to observation (treatment finished)."""
        self._last_transition = (by_user, reason)

    @transition(
        field=status,
        source=[Status.OBSERVATION],
        target=Status.REMISSION,
    )
    def mark_remission(self, by_user=None, reason=""):
        """Move from observation to remission."""
        self._last_transition = (by_user, reason)

    @transition(
        field=status,
        source=[Status.OBSERVATION, Status.REMISSION],
        target=Status.RELAPSE,
    )
    def mark_relapse(self, by_user=None, reason=""):
        """Mark relapse (from observation or remission)."""
        self._last_transition = (by_user, reason)

    @transition(
        field=status,
        source=[Status.RELAPSE],
        target=Status.CONSILIUM,
    )
    def reschedule_consilium(self, by_user=None, reason=""):
        """Move from relapse back to consilium for a new plan."""
        self._last_transition = (by_user, reason)

    @transition(
        field=status,
        source=[
            Status.NEW,
            Status.DIAGNOSTIC,
            Status.CONSILIUM,
            Status.WAITING_HOSPITALIZATION,
            Status.IN_TREATMENT,
            Status.OBSERVATION,
            Status.RELAPSE,
        ],
        target=Status.TERMINAL,
    )
    def mark_terminal(self, by_user=None, reason=""):
        """Mark terminal (patient died or treatment discontinued).

        Allowed from any non-final status. Not allowed from REMISSION
        because remission is not a terminal state (patient is monitored).
        """
        self._last_transition = (by_user, reason)


class StatusTransition(models.Model):
    """Audit trail of status changes for a CancerCase.

    Every successful transition creates one record here.
    This is the foundation for the case timeline and for reports.
    """

    id = models.BigAutoField(primary_key=True)
    case = models.ForeignKey(
        CancerCase,
        on_delete=models.CASCADE,
        related_name="status_transitions",
    )
    from_status = models.CharField(max_length=32)
    to_status = models.CharField(max_length=32)
    transitioned_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="status_transitions",
        null=True,
        blank=True,
    )
    transitioned_at = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-transitioned_at"]
        indexes = [
            models.Index(fields=["case", "-transitioned_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.case_id}: {self.from_status} → {self.to_status}"
