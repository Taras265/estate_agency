from typing import Any

from accounts.models import CustomUser
from .services import user_can_update_client_list
from objects.services import (
    user_can_view_real_estate_list,
    user_can_view_report
)

def get_sale_client_list_context(lang: str, user: CustomUser, object_list) -> dict[str, Any]:
    context = {
        "lang": lang,
        "can_view_real_estate_list": user_can_view_real_estate_list(user),
        "can_view_reports": user_can_view_report(user),
        "can_update_clients": user_can_update_client_list(user, object_list),
        "can_view_client_history": user.has_perm("handbooks.view_historicalclient")
    }
    return context