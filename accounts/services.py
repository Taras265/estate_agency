from typing import List

from accounts.models import CustomUser
from objects.services import user_can_view_real_estate_list
from utils.utils import table_to_app


def get_user_choices(
    user: CustomUser, choices: List[str]
) -> List[str]:
    available_choices = []
    for choice in choices:
        app: str = table_to_app(choice)
        if choice == "realestate" and user_can_view_real_estate_list(user):
            available_choices.append(choice)
        elif (
            user.has_perm(f"{app}.view_{choice}")
            or user.has_perm(f"{app}.view_own_{choice}")
        ) or user.has_perm(f"{app}.view_filial_{choice}"):
            available_choices.append(choice)
    return available_choices


def user_can_create_user(user: CustomUser) -> bool:
    return user.has_perm("accounts.add_customuser")


def user_can_update_user(user: CustomUser) -> bool:
    return user.has_perm("accounts.change_customuser")


def user_can_view_user_history(user: CustomUser) -> bool:
    return user.has_perm("accounts.view_historicalcustomuser")


def user_can_view_custom_group(user: CustomUser) -> bool:
    return user.has_perm("accounts.view_customgroup")
