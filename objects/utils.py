
import datetime
from typing import TypeVar, TypedDict

from django.db.models import QuerySet

from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict

from accounts.models import CustomUser

from .models import BaseRealEstate
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


def get_sale_report_list_context(lang: str, user: CustomUser, form):
    context = {
        "lang": lang,
        "form": form,
        "can_view_client": has_any_perm_from_list(
            user,
            "handbooks.view_client",
            "handbooks.view_own_client",
            "handbooks.view_filial_client",
        ),
        "can_view_real_estate": user_can_view_real_estate_list(user),
        "can_view_contract": has_any_perm_from_list(
            user,
            "objects.view_contract",
            "objects.view_own_contract",
            "objects.view_filial_contract"
        ),
        "can_view_report": user.has_perm("objects.view_report"),
        "can_view_own_report": user.has_perm("objects.view_own_report"),
        "can_view_filial_report": user.has_perm("objects.view_filial_report"),
    }
    return context


T = TypeVar("T", bound=BaseRealEstate)


class RealEstateFilters(TypedDict):
    creation_date_min: datetime.datetime
    creation_date_max: datetime.datetime
    status: list[int]


def real_estate_form_filter(qs: QuerySet[T], filters: RealEstateFilters) -> QuerySet[T]:
    """Фільтрує список нерухомості згідно зі значеннями словника filters"""

    if (creation_date_min := filters.get("creation_date_min")):
        qs = qs.filter(creation_date__gte=creation_date_min)
    if (creation_date_max := filters.get("creation_date_max")):
        qs = qs.filter(creation_date__lte=creation_date_max)
    if (statuses := filters.get("status")):
        qs = qs.filter(status__in=statuses)
    return qs