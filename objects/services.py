from collections.abc import Iterable

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from estate_agency.services import objects_filter
from .choices import RealEstateType
from .models import BaseRealEstate, Apartment, Commerce, House
from accounts.models import CustomUser


def user_can_view_apartment_list(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.view_apartment", "objects.view_own_apartment"
    )


def user_can_view_commerce_list(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.view_commerce", "objects.view_own_commerce"
    )


def user_can_view_house_list(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.view_house", "objects.view_own_house"
    )


def user_can_view_real_estate_list(user: CustomUser) -> bool:
    return (
        user_can_view_apartment_list(user) or
        user_can_view_commerce_list(user) or
        user_can_view_house_list(user)
    )


def user_can_create_apartment(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.add_apartment", "objects.add_own_apartment"
    )


def user_can_create_commerce(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.add_commerce", "objects.add_own_commerce"
    )


def user_can_create_house(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.add_house", "objects.add_own_house"
    )


def user_can_update_apartment(user: CustomUser, apartment_id: int) -> bool:
    try:
        apartment = Apartment.objects.only("realtor").get(id=apartment_id, on_delete=False)
    except Apartment.DoesNotExist:
        return False

    return can_interact_with_object(
        user, apartment, "objects.change_apartment", "objects.change_own_apartment"
    )


def user_can_update_apartment_list(
    user: CustomUser,
    apartment_list: Iterable[Apartment]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user, apartment_list, "objects.change_apartment", "objects.change_own_apartment"
    )


def user_can_update_commerce(user: CustomUser, commerce_id: int) -> bool:
    try:
        commerce = Commerce.objects.only("realtor").get(id=commerce_id, on_delete=False)
    except Commerce.DoesNotExist:
        return False
    
    return can_interact_with_object(
        user, commerce, "objects.change_commerce", "objects.change_own_commerce"
    )


def user_can_update_commerce_list(
    user: CustomUser,
    commerce_list: Iterable[Commerce]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user, commerce_list, "objects.change_commerce", "objects.change_own_commerce"
    )


def user_can_update_house(user: CustomUser, house_id: int) -> bool:
    try:
        house = House.objects.only("realtor").get(id=house_id, on_delete=False)
    except House.DoesNotExist:
        return False
    
    return can_interact_with_object(
        user, house, "objects.change_house", "objects.change_own_house"
    )


def user_can_update_house_list(
    user: CustomUser,
    house_list: Iterable[House]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user, house_list, "objects.change_house", "objects.change_own_house"
    )


def user_can_view_apartment_list_history(
    user: CustomUser,
    apartment_list: Iterable[Apartment]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        apartment_list,
        "objects.view_historicalapartment",
        "objects.view_own_historicalapartment"
    )


def user_can_view_commerce_list_history(
    user: CustomUser,
    commerce_list: Iterable[Commerce]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        commerce_list,
        "objects.view_historicalcommerce",
        "objects.view_own_historicalcommerce"
    )


def user_can_view_house_list_history(
    user: CustomUser,
    house_list: Iterable[House]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        house_list,
        "objects.view_historicalhouse",
        "objects.view_own_historicalhouse"
    )


def apartment_filter_for_user(user_id: int, **kwargs) -> QuerySet[Apartment]:
    """Повертає список квартир, які доступні користувачу для перегляду."""
    user = get_object_or_404(CustomUser, id=user_id)
    can_view_apartment = user.has_perm("objects.view_apartment")
    can_view_own_apartment = user.has_perm("objects.view_own_apartment")

    if not can_view_apartment and not can_view_own_apartment:
        return Apartment.objects.none()

    queryset = Apartment.objects.filter(on_delete=False, **kwargs)\
                                .select_related("locality", "street", "realtor")\
                                .only("id", "locality__locality", "street__street", "realtor__email")
    
    if can_view_apartment:
        return queryset
    
    return queryset.filter(realtor=user_id)


def commerce_filter_for_user(user_id: int, **kwargs) -> QuerySet[Commerce]:
    """Повертає список комерцій, які доступні користувачу для перегляду."""
    user = get_object_or_404(CustomUser, id=user_id)
    can_view_commerce = user.has_perm("objects.view_commerce")
    can_view_own_commerce = user.has_perm("objects.view_own_commerce")

    if not can_view_commerce and not can_view_own_commerce:
        return Commerce.objects.none()

    queryset = Commerce.objects.filter(on_delete=False, **kwargs)\
                                .select_related("locality", "street", "realtor")\
                                .only("id", "locality__locality", "street__street", "realtor__email")
    
    if can_view_commerce:
        return queryset
    
    return queryset.filter(realtor=user_id)


def house_filter_for_user(user_id: int, **kwargs) -> QuerySet[House]:
    """Повертає список будинків, які доступні користувачу для перегляду."""
    user = get_object_or_404(CustomUser, id=user_id)
    can_view_house = user.has_perm("objects.view_house")
    can_view_own_house = user.has_perm("objects.view_own_house")

    if not can_view_house and not can_view_own_house:
        return House.objects.none()

    queryset = House.objects.filter(on_delete=False, **kwargs)\
                            .select_related("locality", "street", "realtor")\
                            .only("id", "locality__locality", "street__street", "realtor__email")
    
    if can_view_house:
        return queryset
    
    return queryset.filter(realtor=user_id)


def has_any_perm_from_list(user: CustomUser, *args: str) -> bool:
    """Перевіряє, чи має користувач хоча б одне з вказаних прав зі списку args"""
    return any(user.has_perm(perm) for perm in args)


def can_interact_with_object(
    user: CustomUser,
    current_object: BaseRealEstate,
    perm: str, own_perm: str
) -> bool:
    """
    Перевіряє, чи має користувач відповідне право для для взаємодії
    (наприклад, редагування, видалення, перегляду історії змін)
    з переданим обʼєктом нерухомості.
    Повертає True, якщо хоча б одне з наступних твержень виконується:
    1) користувач має право для видалення будь-якого обʼєкту відповідного типу
       (наприклад "objects.change_apartment");
    2) користувач хоче видалити власний обʼєкт та має право для видалення
       власного обʼєкту (наприклад "objects.change_own_apartment");
    """
    if user.has_perm(perm):
        return True
    
    if not user.has_perm(own_perm):
        return False

    return current_object.realtor == user


def can_interact_with_object_list(
    user: CustomUser,
    object_list: Iterable[BaseRealEstate],
    perm: str, own_perm: str
) -> dict[int, bool]:
    """
    Перевіряє, чи має користувач відповідне право для взаємодії
    (наприклад, редагування, видалення, перегляду історії змін)
    з переданим переліком обʼєктів.
    perm - загальне право (наприклад, "objects.change_apartment"),
    own_perm - право для взаємодії з власними обʼєктами
    (наприклад, "objects.change_own_apartment").
    Повертає хеш-таблицю, в якій ключі - id обʼєкта, значення - булеве значення.
    """
    if user.has_perm(perm):
        return {item.id: True for item in object_list}
    
    if not user.has_perm(own_perm):
        return {item.id: False for item in object_list}

    return {item.id: item.realtor == user for item in object_list}


def estate_objects_filter_visible(object_type:int, *args, **kwargs) -> QuerySet[Apartment | Commerce | House]:
    if object_type == RealEstateType.APARTMENT:
        return objects_filter(Apartment.objects, on_delete=False, *args, **kwargs)
    elif object_type == RealEstateType.COMMERCE:
        return objects_filter(Commerce.objects, on_delete=False, *args, **kwargs)
    return objects_filter(House.objects, on_delete=False, *args, **kwargs)
