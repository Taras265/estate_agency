from collections.abc import Iterable

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from estate_agency.services import objects_filter, object_create, objects_all_visible, objects_all
from .choices import RealEstateType, RealEstateStatus
from .models import BaseRealEstate, Apartment, Commerce, House, Selection
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


def user_can_view_report(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.view_report", "objects.view_own_report"
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
        user, apartment, "objects.change_apartment", "objects.change_own_apartment",
        "objects.change_filial_apartment", "realtor", Apartment
    )


def user_can_update_apartment_list(
    user: CustomUser,
    apartment_list: Iterable[Apartment]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user, apartment_list, "objects.change_apartment", "objects.change_own_apartment",
        "objects.change_filial_apartment", "realtor", Apartment
    )


def user_can_update_commerce(user: CustomUser, commerce_id: int) -> bool:
    try:
        commerce = Commerce.objects.only("realtor").get(id=commerce_id, on_delete=False)
    except Commerce.DoesNotExist:
        return False
    
    return can_interact_with_object(
        user, commerce, "objects.change_commerce", "objects.change_own_commerce",
        "objects.change_filial_commerce", "realtor", Commerce
    )


def user_can_update_commerce_list(
    user: CustomUser,
    commerce_list: Iterable[Commerce]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user, commerce_list, "objects.change_commerce", "objects.change_own_commerce",
        "objects.change_filial_commerce", "realtor", Commerce
    )


def user_can_update_house(user: CustomUser, house_id: int) -> bool:
    try:
        house = House.objects.only("realtor").get(id=house_id, on_delete=False)
    except House.DoesNotExist:
        return False
    
    return can_interact_with_object(
        user, house, "objects.change_house", "objects.change_own_house",
        "objects.change_filial_house", "realtor", House
    )


def user_can_update_house_list(
    user: CustomUser,
    house_list: Iterable[House]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user, house_list, "objects.change_house", "objects.change_own_house",
        "objects.change_filial_house", "realtor", House

    )


def user_can_view_apartment_list_history(
    user: CustomUser,
    apartment_list: Iterable[Apartment]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        apartment_list,
        "objects.view_apartment",
        "objects.view_own_apartment",
        "objects.view_filial_apartment",
        "realtor", Apartment
    )


def user_can_view_commerce_list_history(
    user: CustomUser,
    commerce_list: Iterable[Commerce]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        commerce_list,
        "objects.view_commerce",
        "objects.view_own_commerce",
        "objects.view_filial_commerce",
        "realtor", Commerce
    )


def user_can_view_house_list_history(
    user: CustomUser,
    house_list: Iterable[House]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        house_list,
        "objects.view_house",
        "objects.view_own_house",
        "objects.view_filial_house",
        "realtor", House
    )


def apartment_filter_for_user(user_id: int, **kwargs) -> QuerySet[Apartment]:
    """Повертає список квартир, які доступні користувачу для перегляду."""
    user = get_object_or_404(CustomUser, id=user_id)
    can_view_apartment = user.has_perm("objects.view_apartment")
    can_view_own_apartment = user.has_perm("objects.view_own_apartment")
    can_view_filial_apartment = user.has_perm("objects.view_filial_apartment")

    if not can_view_apartment and not can_view_own_apartment and not can_view_filial_apartment:
        return Apartment.objects.none()

    queryset = Apartment.objects.filter(on_delete=False, **kwargs)\
                                .select_related("locality", "street", "realtor")\
                                .only("id", "locality__locality", "street__street", "realtor__email")
    
    if can_view_apartment:
        return queryset
    elif can_view_own_apartment:
        return queryset.filter(realtor=user_id)
    return queryset.filter(**{"realtor__filials__in": user.filials.all()}).distinct()


def commerce_filter_for_user(user_id: int, **kwargs) -> QuerySet[Commerce]:
    """Повертає список комерцій, які доступні користувачу для перегляду."""
    user = get_object_or_404(CustomUser, id=user_id)
    can_view_commerce = user.has_perm("objects.view_commerce")
    can_view_own_commerce = user.has_perm("objects.view_own_commerce")
    can_view_filial_commerce = user.has_perm("objects.view_filial_commerce")

    if not can_view_commerce and not can_view_own_commerce and not can_view_filial_commerce:
        return Commerce.objects.none()

    queryset = Commerce.objects.filter(on_delete=False, **kwargs)\
                                .select_related("locality", "street", "realtor")\
                                .only("id", "locality__locality", "street__street", "realtor__email")
    

    if can_view_commerce:
        return queryset
    elif can_view_own_commerce:
        return queryset.filter(realtor=user_id)
    return queryset.filter(**{"realtor__filials__in": user.filials.all()}).distinct()


def house_filter_for_user(user_id: int, **kwargs) -> QuerySet[House]:
    """Повертає список будинків, які доступні користувачу для перегляду."""
    user = get_object_or_404(CustomUser, id=user_id)
    can_view_house = user.has_perm("objects.view_house")
    can_view_own_house = user.has_perm("objects.view_own_house")
    can_view_filial_house = user.has_perm("objects.view_filial_house")

    if not can_view_house and not can_view_own_house and not can_view_filial_house:
        return House.objects.none()

    queryset = House.objects.filter(on_delete=False, **kwargs)\
                            .select_related("locality", "street", "realtor")\
                            .only("id", "locality__locality", "street__street", "realtor__email")
    
    if can_view_house:
        return queryset
    elif can_view_own_house:
        return queryset.filter(realtor=user_id)
    return queryset.filter(**{"realtor__filials__in": user.filials.all()}).distinct()


def apartment_filter_by_user(user_id: int, **kwargs) -> QuerySet[Apartment]:
    """Повертає список квартир, які є у користувача."""
    queryset = Apartment.objects.filter(on_delete=False, **kwargs) \
        .select_related("locality", "street", "realtor") \
        .only("id", "locality__locality", "street__street", "realtor__email")

    return queryset.filter(realtor=user_id)


def commerce_filter_by_user(user_id: int, **kwargs) -> QuerySet[Commerce]:
    """Повертає список комерцій, які є у користувача'."""
    queryset = Commerce.objects.filter(on_delete=False, **kwargs) \
        .select_related("locality", "street", "realtor") \
        .only("id", "locality__locality", "street__street", "realtor__email")

    return queryset.filter(realtor=user_id)


def house_filter_by_user(user_id: int, **kwargs) -> QuerySet[House]:
    """Повертає список будинків, які є у користувача."""
    queryset = House.objects.filter(on_delete=False, **kwargs) \
        .select_related("locality", "street", "realtor") \
        .only("id", "locality__locality", "street__street", "realtor__email")

    return queryset.filter(realtor=user_id)


def apartment_filter_by_filial(user: CustomUser, **kwargs) -> QuerySet[Apartment]:
    """Повертає список квартир, які є у користувача."""
    queryset = Apartment.objects.filter(on_delete=False, **kwargs) \
        .select_related("locality", "street", "realtor") \
        .only("id", "locality__locality", "street__street", "realtor__email")

    return queryset.filter(**{"realtor__filials__in": user.filials.all()}).distinct()


def commerce_filter_by_filial(user: CustomUser, **kwargs) -> QuerySet[Commerce]:
    """Повертає список комерцій, які є у користувача'."""
    queryset = Commerce.objects.filter(on_delete=False, **kwargs) \
        .select_related("locality", "street", "realtor") \
        .only("id", "locality__locality", "street__street", "realtor__email")

    return queryset.filter(**{"realtor__filials__in": user.filials.all()}).distinct()


def house_filter_by_filial(user: CustomUser, **kwargs) -> QuerySet[House]:
    """Повертає список будинків, які є у користувача."""
    queryset = House.objects.filter(on_delete=False, **kwargs) \
        .select_related("locality", "street", "realtor") \
        .only("id", "locality__locality", "street__street", "realtor__email")

    return queryset.filter(**{"realtor__filials__in": user.filials.all()}).distinct()


def real_estate_contract_all(type: int):
    """Повертає список всіх контрактів для об'єктів нерухомості з типом type."""
    model_class = None
    if type == RealEstateType.APARTMENT:
        model_class = Apartment
    elif type == RealEstateType.COMMERCE:
        model_class = Commerce
    elif type == RealEstateType.HOUSE:
        model_class = House
    else:
        raise ValueError(f"Invalid real estate type: {type}")

    return model_class.objects.filter(on_delete=False, status=RealEstateStatus.SOLD)\
                            .select_related("locality", "street", "realtor")\
                            .only("locality__locality", "street__street", "realtor__email")


def real_estate_contract_by_filials(type: int, filials):
    """Повертає список контрактів для об'єктів нерухомості з типом type для заданих філіалів"""
    qs = real_estate_contract_all(type)
    return qs.filter(realtor__filials__in=filials).distinct()


def has_any_perm_from_list(user: CustomUser, *args: str) -> bool:
    """Перевіряє, чи має користувач хоча б одне з вказаних прав зі списку args"""
    return any(user.has_perm(perm) for perm in args)


def can_interact_with_object(
    user: CustomUser,
    current_object: BaseRealEstate,
    perm: str, own_perm: str, filial_perm: str, user_field: str, model
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

    if user.has_perm(filial_perm):
        filials_obj = model.objects.filter(**{f"{user_field}__filials__in": user.filials.all()}).distinct()
        return current_object in filials_obj

    if user.has_perm(own_perm):
        return current_object.realtor == user

    return False


def can_interact_with_object_list(
    user: CustomUser,
    object_list: Iterable[BaseRealEstate],
    perm: str, own_perm: str, filial_perm: str, user_field: str, model
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

    if user.has_perm(filial_perm):
        filials_obj = model.objects.filter(**{f"{user_field}__filials__in": user.filials.all()}).distinct()
        return {item.id: item in filials_obj for item in object_list}

    if user.has_perm(own_perm):
        return {item.id: item.realtor == user for item in object_list}

    return {item.id: False for item in object_list}


def estate_objects_filter_visible(object_type: int, *args, **kwargs) -> QuerySet[Apartment | Commerce | House]:
    """
    Функція для того щоб отримати кверісет об'єктів в залежності від object_type (типа об'єкта)
    """
    if object_type == RealEstateType.APARTMENT:
        return objects_filter(Apartment.objects, on_delete=False, *args, **kwargs)
    elif object_type == RealEstateType.COMMERCE:
        return objects_filter(Commerce.objects, on_delete=False, *args, **kwargs)
    return objects_filter(House.objects, on_delete=False, *args, **kwargs)


def selection_add_selected(object_type: int, selection: Selection, selected, *args, **kwargs) -> None:
    """
    Функція для того щоб створити запис того, що ми зробили виборку для клієнтів (Selection)
    """
    if object_type == RealEstateType.APARTMENT:
        selection.selected_apartments.add(selected)
    elif object_type == RealEstateType.COMMERCE:
        selection.selected_commerces.add(selected)
    else:
        selection.selected_houses.add(selected)


def selection_create(*args, **kwargs) -> Selection:
    return object_create(Selection.objects, *args, **kwargs)


def selection_all(*args, **kwargs) -> QuerySet[Selection]:
    return objects_all(Selection.objects, *args, **kwargs)


def selection_filter(*args, **kwargs) -> QuerySet[Selection]:
    return Selection.objects.filter(*args, **kwargs)


def get_all_apartment_history(*args, **kwargs):
    return objects_all(Apartment.history, *args, **kwargs)


def get_all_commerce_history(*args, **kwargs):
    return objects_all(Commerce.history, *args, **kwargs)


def get_all_houses_history(*args, **kwargs):
    return objects_all(House.history, *args, **kwargs)
