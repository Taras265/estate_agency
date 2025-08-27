from django.db.models import QuerySet

from .models import Client
from accounts.models import CustomUser

def clients_accessible_for_user(user: CustomUser, qs: QuerySet[Client]) -> QuerySet[Client]:
    """
    Повертає лише тих клієнтів з <qs>, які доступні користувачу для перегляду.
    Перевіряються такі права: view_client, view_filial_client, view_own_client.
    """

    if user.has_perm("handbooks.view_client"):
        return qs
    
    if user.has_perm("handbooks.view_filial_client"):
        user_filials = user.filials.all()
        return qs.filter(realtor__filials__in=user_filials)
    
    if user.has_perm("handbooks.view_own_client"):
        return qs.filter(realtor=user)
    
    return qs.none()


def user_can_update_client(user: CustomUser, client: Client) -> bool:
    """Перевіряє, чи може користувач <user> редагувати клієнта <client>"""

    if user.has_perm("handbooks.change_client"):
        return True
    
    if user.has_perm("handbooks.change_filial_client"):
        user_filials = user.filials.all()
        return client.realtor.filials.all() in user_filials
    
    if user.has_perm("handbooks.change_own_client"):
        return client.realtor == user
    
    return False


def user_can_update_client_list(user: CustomUser, clients: QuerySet[Client]) -> dict[int, bool]:
    """
    Перевіряє для кожного клієнта з <clients> чи може користувач <user> його редагувати.
    Повертає словник, в якому ключі - id клієнта, значення - True/False.
    """
    if user.has_perm("handbooks.change_client"):
        return {client.id: True for client in clients}
    
    if user.has_perm("handbooks.change_filial_client"):
        user_filials = user.filials.all()
        return {client.id: client.realtor.filials.all() in user_filials
                for client in clients}
    
    if user.has_perm("handbooks.change_own_client"):
        return {client.id: user == client.realtor for client in clients}
    
    return {client.id: False for client in clients}
    