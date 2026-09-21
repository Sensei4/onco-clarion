from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "title",
        "original_filename",
        "case",
        "uploaded_by",
        "uploaded_at",
        "file_size",
    )
    list_filter = ("type", "organization")
    search_fields = (
        "title",
        "original_filename",
        "case__patient__full_name",
        "case__patient__medical_record_number",
    )
    readonly_fields = (
        "original_filename",
        "content_type",
        "file_size",
        "uploaded_at",
    )
    autocomplete_fields = ("case", "event", "referral", "uploaded_by")
    date_hierarchy = "uploaded_at"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "case",
                    "event",
                    "referral",
                    "organization",
                    "type",
                    "title",
                ),
            },
        ),
        (
            "File",
            {
                "fields": (
                    "file",
                    "original_filename",
                    "content_type",
                    "file_size",
                ),
            },
        ),
        (
            "Audit",
            {
                "fields": ("uploaded_by", "uploaded_at"),
            },
        ),
    )
