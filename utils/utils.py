from typing import Any

from django.apps import apps

from accounts.models import CustomUser
from handbooks.models import Handbook


def get_office_context(user: CustomUser) -> dict[str, Any]:
    """
    Повертає контекст для сторінки офісу
    """
    context = {
        "users": user.has_perm("accounts.view_office_user"),
    }
    return context


def table_to_app(table):
    for model in apps.get_models():
        if model.__name__.lower() == table.lower():
            return model._meta.app_label
        if table in ["".join(label.split("_")) for _, label in Handbook.HANDBOOKS_TYPE_CHOICE]:
            return "handbooks"
        if table.lower() == "realestate":
            return "objects"
