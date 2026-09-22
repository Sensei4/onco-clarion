from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "action",
        "entity_type",
        "entity_repr",
        "ip_address",
        "organization",
    )
    list_filter = ("action", "entity_type", "organization")
    search_fields = (
        "user__username",
        "entity_repr",
        "entity_id",
        "ip_address",
    )
    readonly_fields = (
        "user",
        "action",
        "entity_type",
        "entity_id",
        "entity_repr",
        "organization",
        "timestamp",
        "ip_address",
        "user_agent",
        "request_method",
        "request_path",
    )
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
