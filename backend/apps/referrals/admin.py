from django.contrib import admin

from .models import (
    DiagnosticDepartment,
    DiagnosticMethod,
    Referral,
)


class DiagnosticMethodInline(admin.TabularInline):
    model = DiagnosticMethod
    extra = 0
    fields = ("code", "name", "is_active")
    show_change_link = True


@admin.register(DiagnosticDepartment)
class DiagnosticDepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "organization",
        "is_active",
        "methods_count",
        "created_at",
    )
    list_filter = ("category", "is_active", "organization")
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    inlines = [DiagnosticMethodInline]

    @admin.display(description="Methods")
    def methods_count(self, obj: DiagnosticDepartment) -> int:
        return obj.methods.count()


@admin.register(DiagnosticMethod)
class DiagnosticMethodAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "name",
        "department",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "department__category", "department__organization")
    search_fields = ("code", "name", "department__name")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("department",)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "title",
        "case",
        "status",
        "department",
        "method",
        "assigned_to",
        "scheduled_at",
        "ordered_by",
        "ordered_at",
        "result_received_at",
    )
    list_filter = (
        "type",
        "status",
        "organization",
        "department",
    )
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
    autocomplete_fields = (
        "case",
        "event",
        "ordered_by",
        "completed_by",
        "assigned_to",
        "department",
        "method",
    )
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
            "Diagnostic assignment",
            {
                "fields": (
                    "department",
                    "method",
                    "assigned_to",
                    "scheduled_at",
                    "room",
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
