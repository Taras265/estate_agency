from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict

from .models import BaseRealEstate
from accounts.models import CustomUser


def has_any_perm_form_list(user: CustomUser, *args: str) -> bool:
    """Перевіряє, чи має користувач хоча б одне з вказаних прав зі списку args"""
    return any(user.has_perm(perm) for perm in args)


def has_appropriate_change_perm(
    user: CustomUser,
    model: BaseRealEstate,
    pk: int,
    change_perm: str, change_own_perm: str
) -> bool:
    """
    Перевіряє, чи має користувач відповідне право для редагування
    обʼєкту нерухомості з id=pk.
    Повертає True, якщо хоча б одне з наступних твержень виконується:
    1) користувач має право для видалення будь-якого обʼєкту відповідного типу
       (наприклад "objects.change_apartment");
    2) користувач хоче видалити власний обʼєкт та має право для видалення
       власного обʼєкту (наприклад "objects.change_own_apartment");
    """
    if user.has_perm(change_perm):
        return True
    
    if not user.has_perm(change_own_perm):
        return False

    current_object = model.objects.select_related("realtor")\
                                  .only("realtor__id")\
                                  .get(id=pk)
    return current_object.realtor.pk == user.pk


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
