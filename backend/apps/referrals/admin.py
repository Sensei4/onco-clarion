from django.contrib import admin

from .models import Referral


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "title",
        "case",
        "status",
        "ordered_by",
        "ordered_at",
        "result_received_at",
    )
    list_filter = ("type", "status", "organization")
    search_fields = (
        "title",
        "notes",
        "result_text",
        "case__patient__full_name",
        "case__patient__medical_record_number",
    )
    readonly_fields = (
        "ordered_at",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("case", "event", "ordered_by", "completed_by")
    date_hierarchy = "ordered_at"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "case",
                    "event",
                    "organization",
                    "type",
                    "title",
                ),
            },
        ),
        (
            "Order",
            {
                "fields": (
                    "status",
                    "ordered_by",
                    "ordered_at",
                    "notes",
                ),
            },
        ),
        (
            "Result",
            {
                "fields": (
                    "result_text",
                    "result_received_at",
                    "completed_by",
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
