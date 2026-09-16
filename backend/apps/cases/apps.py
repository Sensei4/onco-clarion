from django.apps import AppConfig


class CasesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cases"

    def ready(self):
        # Import signals so they are registered.
        from . import signals  # noqa: F401
