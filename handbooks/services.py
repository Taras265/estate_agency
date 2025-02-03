from typing import Any

from django.db.models import QuerySet

from handbooks.models import (Region, District, Locality, LocalityDistrict, Street,
                              Handbook, FilialAgency, FilialReport, Client)

from estate_agency.services import objects_all_visible, objects_filter


def region_all_visible(objects: QuerySet = Region.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def region_filter(objects: QuerySet = Region.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)


def district_all_visible(objects: QuerySet = District.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def district_filter(objects: QuerySet = District.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)


def locality_all_visible(objects: QuerySet = Locality.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def locality_filter(objects: QuerySet = Locality.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)


def localitydistrict_all_visible(objects: QuerySet = LocalityDistrict.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def localitydistrict_filter(objects: QuerySet = LocalityDistrict.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)


def street_all_visible(objects: QuerySet = Street.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def street_filter(objects: QuerySet = Street.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)


def handbook_all_visible(objects: QuerySet = Handbook.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def handbook_filter(objects: QuerySet = Handbook.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, *args, **kwargs)


def handbook_filter_visible(objects: QuerySet = Handbook.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, **kwargs)


def filialagency_all_visible(objects: QuerySet = FilialAgency.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def filialagency_filter(objects: QuerySet = FilialAgency.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)


def filialreport_all_visible(objects: QuerySet = FilialReport.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def filialreport_filter(objects: QuerySet = FilialReport.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)


def client_all_visible(objects: QuerySet = Client.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def client_filter(objects: QuerySet = Client.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, *args, **kwargs)


def client_filter_visible(objects: QuerySet = Client.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, **kwargs)
