from django.db import models


class Event(models.Model):
    """Base event in a cancer case.

    Every meaningful action in a case is an Event:
    visit, tumor board, hospitalization, treatment, follow-up.

    Type-specific details live in the subclasses (multi-table
    inheritance): EventPrimaryVisit, EventFollowupVisit, etc.

    See docs/domain.md for the full model.
    """

    class Type(models.TextChoices):
        PRIMARY_VISIT = "primary_visit", "Primary visit"
        FOLLOWUP_VISIT = "followup_visit", "Follow-up visit"
        CONSILIUM = "consilium", "Consilium"
        HOSPITALIZATION = "hospitalization", "Hospitalization"
        TREATMENT = "treatment", "Treatment"
        OBSERVATION_VISIT = "observation_visit", "Observation visit"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    id = models.BigAutoField(primary_key=True)
    case = models.ForeignKey(
        "cases.CancerCase",
        on_delete=models.PROTECT,
        related_name="events",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="events",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.PROTECT,
        related_name="events",
    )
    type = models.CharField(max_length=32, choices=Type.choices)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    scheduled_at = models.DateTimeField()
    occurred_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="authored_events",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["organization", "status", "scheduled_at"]),
            models.Index(fields=["case", "-scheduled_at"]),
            models.Index(fields=["patient", "-scheduled_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_type_display()} #{self.pk} ({self.status})"


class EventPrimaryVisit(Event):
    """First visit of a patient for this case.

    The entry point into the cancer care pathway.
    """

    chief_complaint = models.TextField(
        blank=True,
        help_text="Patient's complaints at presentation",
    )
    physical_exam = models.TextField(
        blank=True,
        help_text="Findings from physical examination",
    )

    class Meta:
        verbose_name = "Primary visit"
        verbose_name_plural = "Primary visits"


class EventFollowupVisit(Event):
    """Follow-up visit after primary visit or treatment.

    Used for interim check-ups, discussing test results, etc.
    """

    findings = models.TextField(
        blank=True,
        help_text="Findings and test results reviewed",
    )
    plan = models.TextField(
        blank=True,
        help_text="Next steps and treatment plan",
    )

    class Meta:
        verbose_name = "Follow-up visit"
        verbose_name_plural = "Follow-up visits"


class EventObservationVisit(Event):
    """Planned visit during the observation (follow-up) phase.

    These visits are routine: patient is monitored after treatment.
    """

    findings = models.TextField(
        blank=True,
        help_text="Findings from the observation visit",
    )

    class Meta:
        verbose_name = "Observation visit"
        verbose_name_plural = "Observation visits"


class EventConsilium(Event):
    """Tumor board (multidisciplinary consilium).

    Multiple specialists gather to discuss a case and produce
    a joint decision. In the current MVP the consilium happens
    offline; the result is recorded here after the fact.
    """

    participants = models.ManyToManyField(
        "accounts.User",
        related_name="consiliums_attended",
        blank=True,
        help_text="Specialists who participated in the consilium",
    )
    decision = models.TextField(
        blank=True,
        help_text="Joint decision of the consilium",
    )
    recommended_plan = models.TextField(
        blank=True,
        help_text="Recommended treatment plan",
    )

    class Meta:
        verbose_name = "Consilium"
        verbose_name_plural = "Consilia"


class EventHospitalization(Event):
    """Admission to an inpatient ward.

    Covers the whole stay: admission, treatment during stay,
    discharge. The actual treatment details are stored separately
    in EventTreatment records.
    """

    ward = models.CharField(
        max_length=128,
        blank=True,
        help_text="Ward or department (e.g. 'Oncology ward 3')",
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason for hospitalization",
    )
    discharge_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of discharge, if already discharged",
    )

    class Meta:
        verbose_name = "Hospitalization"
        verbose_name_plural = "Hospitalizations"


class EventTreatment(Event):
    """A single treatment cycle.

    One record per cycle. A course of 6 cycles of chemotherapy
    is 6 EventTreatment records.

    This is the core unit of oncological work: what is being done
    to the patient, with which drugs, at which cycle.
    """

    class Modality(models.TextChoices):
        CHEMO = "chemo", "Chemotherapy"
        RADIATION = "radiation", "Radiation therapy"
        SURGERY = "surgery", "Surgery"
        TARGETED = "targeted", "Targeted therapy"
        IMMUNOTHERAPY = "immunotherapy", "Immunotherapy"
        OTHER = "other", "Other"

    modality = models.CharField(
        max_length=32,
        choices=Modality.choices,
        default=Modality.CHEMO,
    )
    regimen = models.CharField(
        max_length=128,
        blank=True,
        help_text="Regimen name (e.g. 'AC', 'FOLFOX')",
    )
    cycle_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Current cycle number (e.g. 3)",
    )
    cycle_total = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Total number of cycles in the course (e.g. 6)",
    )
    drugs = models.TextField(
        blank=True,
        help_text="Drugs and doses (free text)",
    )

    class Meta:
        verbose_name = "Treatment"
        verbose_name_plural = "Treatments"

    def __str__(self) -> str:
        cycle = ""
        if self.cycle_number:
            if self.cycle_total:
                cycle = f" cycle {self.cycle_number}/{self.cycle_total}"
            else:
                cycle = f" cycle {self.cycle_number}"
        return f"{self.get_modality_display()}{cycle} #{self.pk}"
