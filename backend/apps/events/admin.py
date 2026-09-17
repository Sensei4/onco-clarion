from django.contrib import admin

from .models import (
    Event,
    EventConsilium,
    EventFollowupVisit,
    EventHospitalization,
    EventObservationVisit,
    EventPrimaryVisit,
    EventTreatment,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "case",
        "patient",
        "status",
        "scheduled_at",
        "author",
        "organization",
    )
    list_filter = ("type", "status", "organization")
    search_fields = (
        "patient__full_name",
        "patient__medical_record_number",
        "notes",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("case", "patient", "author")
    date_hierarchy = "scheduled_at"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "type",
                    "status",
                    "case",
                    "patient",
                    "organization",
                ),
            },
        ),
        (
            "Schedule",
            {
                "fields": ("scheduled_at", "occurred_at", "author"),
            },
        ),
        (
            "Details",
            {
                "fields": ("notes",),
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


@admin.register(EventPrimaryVisit)
class EventPrimaryVisitAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "patient", "status", "scheduled_at", "author")
    list_filter = ("status", "organization")
    search_fields = ("patient__full_name", "patient__medical_record_number")
    autocomplete_fields = ("case", "patient", "author")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EventFollowupVisit)
class EventFollowupVisitAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "patient", "status", "scheduled_at", "author")
    list_filter = ("status", "organization")
    search_fields = ("patient__full_name", "patient__medical_record_number")
    autocomplete_fields = ("case", "patient", "author")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EventObservationVisit)
class EventObservationVisitAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "patient", "status", "scheduled_at", "author")
    list_filter = ("status", "organization")
    search_fields = ("patient__full_name", "patient__medical_record_number")
    autocomplete_fields = ("case", "patient", "author")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EventConsilium)
class EventConsiliumAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "patient", "status", "scheduled_at", "author")
    list_filter = ("status", "organization")
    search_fields = (
        "patient__full_name",
        "patient__medical_record_number",
        "decision",
    )
    autocomplete_fields = ("case", "patient", "author")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("participants",)


@admin.register(EventHospitalization)
class EventHospitalizationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "case",
        "patient",
        "status",
        "ward",
        "scheduled_at",
        "discharge_date",
    )
    list_filter = ("status", "organization")
    search_fields = (
        "patient__full_name",
        "patient__medical_record_number",
        "ward",
    )
    autocomplete_fields = ("case", "patient", "author")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EventTreatment)
class EventTreatmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "case",
        "patient",
        "modality",
        "regimen",
        "cycle_display",
        "status",
        "scheduled_at",
    )
    list_filter = ("modality", "status", "organization")
    search_fields = (
        "patient__full_name",
        "patient__medical_record_number",
        "regimen",
    )
    autocomplete_fields = ("case", "patient", "author")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Cycle")
    def cycle_display(self, obj: EventTreatment) -> str:
        if obj.cycle_number and obj.cycle_total:
            return f"{obj.cycle_number}/{obj.cycle_total}"
        if obj.cycle_number:
            return str(obj.cycle_number)
        return "—"
