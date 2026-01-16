from django.apps import AppConfig


class HandbooksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "handbooks"

    def ready(self):
        from django.db.models.signals import post_migrate
        from .signals import remove_history_permissions
        post_migrate.connect(remove_history_permissions, sender=self)
