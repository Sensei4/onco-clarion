from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Organization, User


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "created_at")
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "full_name",
        "role",
        "organization",
        "is_active",
    )
    list_filter = ("role", "organization", "is_active", "is_staff")
    search_fields = ("username", "email", "full_name")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("OncoClarion", {"fields": ("full_name", "role", "organization")}),
    )
