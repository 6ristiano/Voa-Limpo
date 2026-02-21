from django.apps import AppConfig

class OperacionalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "operacional"

    def ready(self):
        from . import signals  # noqa