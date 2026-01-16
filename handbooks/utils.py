from typing import Any

from accounts.models import CustomUser
from .services import user_can_update_client_list

def get_sale_client_list_context(lang: str, user: CustomUser, object_list) -> dict[str, Any]:
    context = {
        "lang": lang,
        "can_update_clients": user_can_update_client_list(user, object_list),
        "can_view_client_history": user.has_perm("handbooks.view_own_clients")
    }
    return context