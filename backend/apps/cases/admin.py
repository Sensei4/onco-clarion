from django.contrib import admin

from .models import CancerCase


@admin.register(CancerCase)
class CancerCaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "status",
        "stage",
        "diagnosis_code",
        "organization",
        "created_at",
    )
    list_filter = ("status", "stage", "organization")
    search_fields = (
        "patient__full_name",
        "patient__medical_record_number",
        "diagnosis_code",
        "diagnosis_text",
    )
    readonly_fields = ("created_at", "updated_at", "status")
    autocomplete_fields = ("patient",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "patient",
                    "organization",
                    "status",
                ),
            },
        ),
        (
            "Diagnosis",
            {
                "fields": (
                    "diagnosis_code",
                    "diagnosis_text",
                    "verification_date",
                ),
            },
        ),
        (
            "Staging",
            {
                "fields": (
                    "tnm_t",
                    "tnm_n",
                    "tnm_m",
                    "stage",
                ),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
