from accounts.models import CustomUser


def user_can_update_user(user: CustomUser) -> bool:
    return user.has_perm("accounts.change_customuser")


def user_can_view_user_history(user: CustomUser) -> bool:
    return user.has_perm("accounts.view_historicalcustomuser")
