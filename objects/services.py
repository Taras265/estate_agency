from collections.abc import Iterable
from typing import List, Optional, TypeVar, Literal


from django.db.models import QuerySet

from .choices import RealEstateType, RealEstateStatus
from .models import BaseRealEstate, Apartment, Commerce, House, Selection
from accounts.models import CustomUser


T = TypeVar("T", bound=BaseRealEstate)


def user_can_view_apartment_list(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user,
        "objects.view_apartment",
        "objects.view_own_apartment",
        "objects.view_filial_apartment",
    )


def user_can_view_commerce_list(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user,
        "objects.view_commerce",
        "objects.view_own_commerce",
        "objects.view_filial_commerce",
    )


def user_can_view_house_list(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.view_house", "objects.view_own_house", "objects.view_filial_house"
    )


def user_can_view_real_estate_list(user: CustomUser) -> bool:
    return (
        user_can_view_apartment_list(user)
        or user_can_view_commerce_list(user)
        or user_can_view_house_list(user)
    )


def user_can_view_report(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.view_report", "objects.view_own_report", "objects.view_filial_report"
    )

def user_can_view_office_report(user: CustomUser) -> bool:
    return has_any_perm_from_list(
        user, "objects.view_office_report", "objects.view_office_own_report", "objects.view_office_filial_report"
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
    return has_any_perm_from_list(user, "objects.add_house", "objects.add_own_house")


def user_can_update_apartment(user: CustomUser, apartment_id: int) -> bool:
    try:
        apartment = Apartment.objects.only("realtor").get(
            id=apartment_id, on_delete=False
        )
    except Apartment.DoesNotExist:
        return False

    return can_interact_with_object(
        user,
        apartment,
        "objects.change_apartment",
        "objects.change_own_apartment",
        "objects.change_filial_apartment",
        "realtor",
        Apartment,
        partial_edit_perm=[
            "objects.change_object_comment",
            "objects.change_object_price",
        ],
    )


def user_can_update_full_apartment(user: CustomUser, apartment_id: int) -> bool:
    try:
        apartment = Apartment.objects.only("realtor").get(
            id=apartment_id, on_delete=False
        )
    except Apartment.DoesNotExist:
        return False

    return can_interact_with_object(
        user,
        apartment,
        "objects.change_apartment",
        "objects.change_own_apartment",
        "objects.change_filial_apartment",
        "realtor",
        Apartment,
    )


def user_can_update_apartment_list(
    user: CustomUser, apartment_list: Iterable[Apartment]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        apartment_list,
        "objects.change_apartment",
        "objects.change_own_apartment",
        "objects.change_filial_apartment",
        "realtor",
        Apartment,
        partial_edit_perm=[
            "objects.change_object_comment",
            "objects.change_object_price",
        ],
    )


def user_can_update_full_commerce(user: CustomUser, commerce_id: int) -> bool:
    try:
        commerce = Commerce.objects.only("realtor").get(id=commerce_id, on_delete=False)
    except Commerce.DoesNotExist:
        return False

    return can_interact_with_object(
        user,
        commerce,
        "objects.change_commerce",
        "objects.change_own_commerce",
        "objects.change_filial_commerce",
        "realtor",
        Commerce,
    )


def user_can_update_commerce(user: CustomUser, commerce_id: int) -> bool:
    try:
        commerce = Commerce.objects.only("realtor").get(id=commerce_id, on_delete=False)
    except Commerce.DoesNotExist:
        return False

    return can_interact_with_object(
        user,
        commerce,
        "objects.change_commerce",
        "objects.change_own_commerce",
        "objects.change_filial_commerce",
        "realtor",
        Commerce,
        partial_edit_perm=[
            "objects.change_object_comment",
            "objects.change_object_price",
        ],
    )


def user_can_update_commerce_list(
    user: CustomUser, commerce_list: Iterable[Commerce]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        commerce_list,
        "objects.change_commerce",
        "objects.change_own_commerce",
        "objects.change_filial_commerce",
        "realtor",
        Commerce,
        partial_edit_perm=[
            "objects.change_object_comment",
            "objects.change_object_price",
        ],
    )


def user_can_update_house(user: CustomUser, house_id: int) -> bool:
    try:
        house = House.objects.only("realtor").get(id=house_id, on_delete=False)
    except House.DoesNotExist:
        return False

    return can_interact_with_object(
        user,
        house,
        "objects.change_house",
        "objects.change_own_house",
        "objects.change_filial_house",
        "realtor",
        House,
        partial_edit_perm=[
            "objects.change_object_comment",
            "objects.change_object_price",
        ],
    )


def user_can_update_full_house(user: CustomUser, house_id: int) -> bool:
    try:
        house = House.objects.only("realtor").get(id=house_id, on_delete=False)
    except House.DoesNotExist:
        return False

    return can_interact_with_object(
        user,
        house,
        "objects.change_house",
        "objects.change_own_house",
        "objects.change_filial_house",
        "realtor",
        House,
    )


def user_can_update_house_list(
    user: CustomUser, house_list: Iterable[House]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        house_list,
        "objects.change_house",
        "objects.change_own_house",
        "objects.change_filial_house",
        "realtor",
        House,
        partial_edit_perm=[
            "objects.change_object_comment",
            "objects.change_object_price",
        ],
    )


def user_can_view_apartment_list_history(
    user: CustomUser, apartment_list: Iterable[Apartment]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        apartment_list,
        "objects.view_apartment",
        "objects.view_own_apartment",
        "objects.view_filial_apartment",
        "realtor",
        Apartment,
    )


def user_can_view_commerce_list_history(
    user: CustomUser, commerce_list: Iterable[Commerce]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        commerce_list,
        "objects.view_commerce",
        "objects.view_own_commerce",
        "objects.view_filial_commerce",
        "realtor",
        Commerce,
    )


def user_can_view_house_list_history(
    user: CustomUser, house_list: Iterable[House]
) -> dict[int, bool]:
    return can_interact_with_object_list(
        user,
        house_list,
        "objects.view_house",
        "objects.view_own_house",
        "objects.view_filial_house",
        "realtor",
        House,
    )


def real_estate_model_from_type(type: int) -> type[BaseRealEstate]:
    """
    Повертає клас моделі нерухомості в залежності від вказаного типу.
    Якщо вказано неправильний тип нерухомості, буде повернуто None.
    """
    model_class = None
    if type == RealEstateType.APARTMENT:
        model_class = Apartment
    elif type == RealEstateType.COMMERCE:
        model_class = Commerce
    elif type == RealEstateType.HOUSE:
        model_class = House
    
    return model_class


def apartment_accessible_for_user(user: CustomUser, qs: QuerySet[Apartment]) -> QuerySet[Apartment]:
    """
    Повертає лише ті квартири з <qs>, які доступні користувачу для перегляду.
    Перевіряються такі права: view_apartment, view_filial_apartment, view_own_apartment.
    """
    if user.has_perm("objects.view_apartment"):
        return qs
    
    if user.has_perm("objects.view_filial_apartment"):
        user_filials = user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()
    
    if user.has_perm("objects.view_own_apartment"):
        return qs.filter(realtor=user)
    
    return qs.none()


def commerce_accessible_for_user(user: CustomUser, qs: QuerySet[Commerce]) -> QuerySet[Commerce]:
    """
    Повертає лише ті комерції з <qs>, які доступні користувачу для перегляду.
    Перевіряються такі права: view_commerce, view_filial_commerce, view_own_commerce.
    """
    if user.has_perm("objects.view_commerce"):
        return qs

    if user.has_perm("objects.view_filial_commerce"):
        user_filials = user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()

    if user.has_perm("objects.view_own_commerce"):
        return qs.filter(realtor=user)

    return qs.none()


def house_accessible_for_user(user: CustomUser, qs: QuerySet[Commerce]) -> QuerySet[House]:
    """
    Повертає лише ті будинки з <qs>, які доступні користувачу для перегляду.
    Перевіряються такі права: view_house, view_filial_house, view_own_house.
    """
    if user.has_perm("objects.view_house"):
        return qs
    
    if user.has_perm("objects.view_filial_house"):
        user_filials = user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()

    if user.has_perm("objects.view_own_house"):
        return qs.filter(realtor=user)

    return qs.none()


def reports_accessible_for_user(user: CustomUser, qs: QuerySet[T]) -> QuerySet[T]:
    """
    Повертає лише ті звіти з <qs>, які доступні користувачу для перегляду.
    Перевіряються такі права: view_report, view_filial_report, view_own_report.
    """
    if user.has_perm("objects.view_report"):
        return qs

    if user.has_perm("objects.view_filial_report"):
        user_filials = user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()

    if user.has_perm("objects.view_own_report"):
        return qs.filter(realtor=user)

    return qs.none()


def reports_accessible_for_user_in_office(user: CustomUser, qs: QuerySet[T]) -> QuerySet[T]:
    """
    Повертає лише ті звіти з <qs>, які доступні користувачу для перегляду.
    Перевіряються такі права: view_office_report, view_office_filial_report,
    view_office_own_report.
    """
    if user.has_perm("objects.view_office_report"):
        return qs

    if user.has_perm("objects.view_office_filial_report"):
        user_filials = user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()

    if user.has_perm("objects.view_office_own_report"):
        return qs.filter(realtor=user)

    return qs.none()


def contracts_accessible_for_user(user: CustomUser, qs: QuerySet[T]) -> QuerySet[T]:
    """
    Повертає лише ті контракти з <qs>, які доступні користувачу для перегляду.
    Перевіряються такі права: view_contract, view_filial_contract, view_own_contract.
    """
    qs = qs.filter(status=RealEstateStatus.SOLD)

    if user.has_perm("objects.view_contract"):
        return qs
    
    if user.has_perm("objects.view_filial_contract"):
        user_filials = user.filials.all()
        return qs.filter(realtor__filials__in=user_filials).distinct()
    
    if user.has_perm("objects.view_own_contract"):
        return qs.filter(realtor=user)
    
    return qs.none()


def has_any_perm_from_list(user: CustomUser, *args: str) -> bool:
    """Перевіряє, чи має користувач хоча б одне з вказаних прав зі списку args"""
    return any(user.has_perm(perm) for perm in args)


def can_interact_with_object(
    user: CustomUser,
    current_object: BaseRealEstate,
    perm: str,
    own_perm: str,
    filial_perm: str,
    user_field: str,
    model,
    partial_edit_perm: Optional[List[str]] = None,
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

    if partial_edit_perm:
        for p in partial_edit_perm:
            if user.has_perm(p):
                return True

    p = False
    if user.has_perm(filial_perm):
        filials_obj = model.objects.filter(
            **{f"{user_field}__filials__in": user.filials.all()}
        ).distinct()
        p = current_object in filials_obj

    if user.has_perm(own_perm):
        p = current_object.realtor == user or p

    return p


def can_interact_with_object_list(
    user: CustomUser,
    object_list: Iterable[BaseRealEstate],
    perm: str,
    own_perm: str,
    filial_perm: str,
    user_field: str,
    model,
    partial_edit_perm: Optional[List[str]] = None,
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

    loc = {item.id: False for item in object_list}
    if user.has_perm(filial_perm):
        filials_obj = model.objects.filter(
            **{f"{user_field}__filials__in": user.filials.all()}
        ).distinct()
        for item in object_list:
            if not loc[item.id]:
                loc[item.id] = item in filials_obj

    if user.has_perm(own_perm):
        for item in object_list:
            if not loc[item.id]:
                loc[item.id] = item.realtor == user

    if partial_edit_perm:
        for p in partial_edit_perm:
            if user.has_perm(p):
                return {item.id: True for item in object_list}

    return loc


def selection_add_selected(
    object_type: int, selection: Selection, selected, *args, **kwargs
) -> None:
    """
    Функція для того щоб створити запис того, що ми зробили виборку для клієнтів (Selection)
    """
    if object_type == RealEstateType.APARTMENT:
        selection.selected_apartments.add(selected)
    elif object_type == RealEstateType.COMMERCE:
        selection.selected_commerces.add(selected)
    elif object_type == RealEstateType.HOUSE:
        selection.selected_houses.add(selected)
