from django.contrib import admin

from .models import DiagnosisCode, MorphologyCode


@admin.register(DiagnosisCode)
class DiagnosisCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "name_en", "block", "system", "is_active")
    list_filter = ("system", "block", "is_active")
    search_fields = ("code", "name", "name_en")
    readonly_fields = ("created_at",)
    ordering = ("code",)


@admin.register(MorphologyCode)
class MorphologyCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "name_en", "behavior", "is_active")
    list_filter = ("behavior", "is_active")
    search_fields = ("code", "name", "name_en")
    readonly_fields = ("created_at",)
    ordering = ("code",)
