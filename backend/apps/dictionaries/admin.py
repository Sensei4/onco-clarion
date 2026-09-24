from django.contrib import admin

from .models import FoundationEntity, Icd11SyncLog, MmsEntity


@admin.register(FoundationEntity)
class FoundationEntityAdmin(admin.ModelAdmin):
    list_display = ("uri", "title", "chapter", "last_synced_at")
    list_filter = ("chapter",)
    search_fields = ("uri", "title")
    readonly_fields = ("last_synced_at",)


@admin.register(MmsEntity)
class MmsEntityAdmin(admin.ModelAdmin):
    list_display = ("the_code", "title", "chapter", "is_leaf", "last_synced_at")
    list_filter = ("chapter", "is_leaf", "is_residual_unspecified", "is_residual_other")
    search_fields = ("uri", "the_code", "title")
    readonly_fields = ("last_synced_at",)


@admin.register(Icd11SyncLog)
class Icd11SyncLogAdmin(admin.ModelAdmin):
    list_display = (
        "release_id",
        "started_at",
        "finished_at",
        "status",
        "foundation_count",
        "mms_count",
    )
    list_filter = ("status", "release_id")
    readonly_fields = (
        "release_id",
        "started_at",
        "finished_at",
        "status",
        "foundation_count",
        "mms_count",
        "error_message",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
