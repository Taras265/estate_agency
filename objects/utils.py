from typing import Any
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict

from .models import BaseRealEstate
from accounts.models import CustomUser
from .services import has_any_perm_from_list, user_can_view_real_estate_list


def real_estate_form_save(
    form: ModelForm,
    formset_class: BaseFormSet,
    formset_data: QueryDict,
    formset_files: MultiValueDict,
    instance: BaseRealEstate = None,
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
    formset.instance = form.save()
    formset.save()
    return (formset, True)


def get_report_list_context(user: CustomUser) -> dict[str, Any]:
    """Повертає контекст для списку контрактів об'єктів нерухомості"""
    context = {
        "can_view_client": has_any_perm_from_list(
            user,
            "handbooks.view_client",
            "handbooks.view_own_client",
            "handbooks.view_filial_client",
        ),
        "can_view_real_estate": user_can_view_real_estate_list(user),
        "can_view_contract": (
            user.has_perm("objects.view_contract")
            or user.has_perm("objects.view_filial_contract")
            or user.has_perm("objects.view_own_contract")
        ),
    }
    return context
