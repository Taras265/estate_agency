from collections.abc import Iterable
from typing import TypeVar

from django.db.models import QuerySet

from .choices import RealEstateType, RealEstateStatus, PermissionUpdateLevel
from .models import BaseRealEstate, Apartment, Commerce, House, Selection, Land
from .forms import RealEstateSearchForm
from accounts.models import CustomUser


T = TypeVar("T", bound=BaseRealEstate)


def user_can_update_real_estate(
    user: CustomUser,
    real_estate: BaseRealEstate
) -> PermissionUpdateLevel:
    if user.has_perm("objects.change_real_estate"):
        return PermissionUpdateLevel.FULL
    
    if (
        user.has_perm("objects.change_own_real_estate")
        and real_estate.realtor == user
    ):
        return PermissionUpdateLevel.FULL
    
    # додати перевірку на можливість частково оновлювати об'єкт нерухомості
    # return PermissionUpdateLevel.PARTIAL

    return PermissionUpdateLevel.NONE


def user_can_update_real_estate_list(
    user: CustomUser,
    real_estate_list: Iterable[BaseRealEstate]
) -> dict[int, bool]:
    # додати перевірку на можливість частково оновлювати об'єкти нерухомості

    if user.has_perm("objects.change_real_estate"):
        return {real_estate.id: PermissionUpdateLevel.FULL
                for real_estate in real_estate_list}
    
    if user.has_perm("objects.change_own_real_estate"):
        return {real_estate.id: PermissionUpdateLevel.FULL if user == real_estate.realtor else PermissionUpdateLevel.NONE
                for real_estate in real_estate_list}
    
    return {real_estate.id: PermissionUpdateLevel.NONE
            for real_estate in real_estate_list}

'''
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


def user_can_update_land(user: CustomUser, land_id: int) -> bool:
    try:
        land = House.objects.only("realtor").get(id=land_id, on_delete=False)
    except Land.DoesNotExist:
        return False

    return can_interact_with_object(
        user,
        land,
        "objects.change_land",
        "objects.change_own_land",
        "objects.change_filial_land",
        "realtor",
        Land,
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


def user_can_update_full_land(user: CustomUser, house_id: int) -> bool:
    try:
        land = Land.objects.only("realtor").get(id=house_id, on_delete=False)
    except Land.DoesNotExist:
        return False

    return can_interact_with_object(
        user,
        land,
        "objects.change_land",
        "objects.change_own_land",
        "objects.change_filial_land",
        "realtor",
        Land,
    )
'''

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
    elif type == RealEstateType.LAND:
        model_class = Land
    return model_class


'''
def can_interact_with_object(
    user: CustomUser,
    current_object: BaseRealEstate,
    perm: str,
    own_perm: str,
    filial_perm: str,
    user_field: str,
    model,
    partial_edit_perm: list[str] | None = None,
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
'''

def selection_add_selected_objects(
    selection: Selection, object_type: int, *objects: BaseRealEstate
) -> None:
    """
    Функція для того щоб створити запис того, що ми зробили виборку для клієнтів (Selection)
    """
    if object_type == RealEstateType.APARTMENT:
        selection.selected_apartments.add(*objects)
    elif object_type == RealEstateType.COMMERCE:
        selection.selected_commerces.add(*objects)
    elif object_type == RealEstateType.HOUSE:
        selection.selected_houses.add(*objects)
    elif object_type == RealEstateType.LAND:
        selection.selected_lands.add(*objects)


def process_real_estate_search_form(
    qs: QuerySet[BaseRealEstate],
    form: RealEstateSearchForm,
    user: CustomUser
) -> QuerySet[BaseRealEstate]:
    """Фільтрує нерухомість <qs> в залежності від значень полів форми <form>"""
    if (id := form.cleaned_data.get("id")):
        qs = qs.filter(pk=id)
    
    locality_district_vals = form.cleaned_data.get("locality_district")
    street_vals = form.cleaned_data.get("street")
    if street_vals:
        # якщо вказано вулиці,
        # шукаємо нерухомість лише за вулицями, без районів
        print("streets", flush=True)
        qs = qs.filter(street__in=street_vals)
    elif locality_district_vals:
        # якщо вулиць не вказано, а райони вказано,
        # то шукаємо нерухомість за районами
        print("locality_district", flush=True)
        qs = qs.filter(street__locality_district__in=locality_district_vals)

    if (price_min := form.cleaned_data.get("price_min")):
        qs = qs.filter(price__gte=price_min)
    
    if (price_max := form.cleaned_data.get("price_max")):
        qs = qs.filter(price__lte=price_max)
    
    if (status_vals := form.cleaned_data.get("status")):
        qs = qs.filter(status__in=status_vals)
    
    if (rubric_vals := form.cleaned_data.get("rubric")):
        qs = qs.filter(rubric__in=rubric_vals)

    if (whose_objects := form.cleaned_data.get("whose_objects")) == "own":
        qs = qs.filter(realtor=user)
    
    if len((exclusive := form.cleaned_data.get("exclusive"))) == 1:
        qs = qs.filter(exclusive=exclusive[0])
    
    if len((in_selection := form.cleaned_data.get("in_selection"))) == 1:
        qs.filter(in_selection=in_selection[0])

    return qs