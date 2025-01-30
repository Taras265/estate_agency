from collections.abc import Iterable

from django.db.models import QuerySet
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict
from django.shortcuts import get_object_or_404

from .models import BaseRealEstate, Apartment, Commerce, House
from accounts.models import CustomUser


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


def has_any_perm_form_list(user: CustomUser, *args: str) -> bool:
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


def real_estate_form_save(
    form: ModelForm,
    formset_class: BaseFormSet,
    formset_data: QueryDict,
    formset_files: MultiValueDict,
    instance: BaseRealEstate = None
) -> tuple[BaseFormSet, bool]:
    """
    Зберігає дані форми та формсету для обʼєкту нерухомості.
    Якщо переданий параметр instance, то виконується оновлення обʼєкта.
    """
    formset = formset_class(
        formset_data,
        formset_files,
        prefix="images",
        instance=instance,
    )
    if not formset.is_valid():
        return (formset, False)

    form.save()
    formset.save()
    return (formset, True)
