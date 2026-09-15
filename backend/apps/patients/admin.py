from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "medical_record_number",
        "birth_date",
        "sex",
        "vital_status",
        "organization",
        "created_at",
    )
    list_filter = ("sex", "vital_status", "organization")
    search_fields = ("full_name", "medical_record_number")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "full_name",
                    "birth_date",
                    "sex",
                    "medical_record_number",
                    "vital_status",
                ),
            },
        ),
        (
            "Additional",
            {
                "fields": ("contacts", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
