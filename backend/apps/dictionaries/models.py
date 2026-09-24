from django.db import models


class DiagnosisCode(models.Model):
    """Reference code from a medical classification.

    Currently used for ICD-10 topography (C00-C97 blocks).
    Later will also hold ICD-O-3 morphology codes.
    """

    class System(models.TextChoices):
        ICD10 = "icd10", "ICD-10"
        ICD_O_3 = "icd_o_3", "ICD-O-3"

    id = models.BigAutoField(primary_key=True)
    system = models.CharField(
        max_length=16,
        choices=System.choices,
        default=System.ICD10,
    )
    code = models.CharField(
        max_length=16,
        db_index=True,
        help_text="e.g. 'C50.9'",
    )
    name = models.CharField(max_length=512)
    name_en = models.CharField(max_length=512, blank=True)
    chapter = models.CharField(max_length=8, blank=True)
    block = models.CharField(max_length=16, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["system", "code"],
                name="unique_code_per_system",
            ),
        ]
        indexes = [
            models.Index(fields=["system", "code"]),
            models.Index(fields=["system", "block"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class MorphologyCode(models.Model):
    """ICD-O-3 morphology code (e.g. 8140/3 — Adenocarcinoma, NOS).

    Stored separately because the structure is different from ICD-10.
    """

    id = models.BigAutoField(primary_key=True)
    code = models.CharField(
        max_length=16,
        unique=True,
        db_index=True,
        help_text="e.g. '8140/3'",
    )
    name = models.CharField(max_length=512)
    name_en = models.CharField(max_length=512, blank=True)
    behavior = models.CharField(
        max_length=8,
        blank=True,
        help_text="/0 benign, /1 uncertain, /2 in situ, /3 malignant, /6 metastatic",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"
