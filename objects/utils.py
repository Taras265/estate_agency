
import datetime
from typing import TypeVar, TypedDict, Any

from django.db.models import QuerySet
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict

from accounts.models import CustomUser
from .models import BaseRealEstate


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