from django.contrib.auth.models import Permission

def remove_history_permissions(sender, **kwargs):
    Permission.objects.filter(
        content_type__model__startswith="historical"
    ).delete()
