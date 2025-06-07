from typing import Any, Optional

from django.db.models import QuerySet

from accounts.models import CustomUser
from utils.const import TABLE_TO_APP, LIST_BY_USER, OBJECT_FIELDS


def have_permission_to_do(user, perm_type, handbook_type, obj, p=""):

    p_handbook_type = "".join(handbook_type.split("_"))
    has_perm = user.has_perm(f"{TABLE_TO_APP[handbook_type]}.{perm_type}_{p}{p_handbook_type}")
    if handbook_type in LIST_BY_USER.keys() and not has_perm:
        if isinstance(LIST_BY_USER[handbook_type], str):
            return check_own_perm_by_field(obj,
                                           LIST_BY_USER[handbook_type],
                                           user,
                                           f"{TABLE_TO_APP[handbook_type]}.{perm_type}_own_{p}{p_handbook_type}")
        else:
            for field in LIST_BY_USER[handbook_type]:
                has_perm = check_own_perm_by_field(obj,
                                                   field,
                                                   user,
                                                   f"{TABLE_TO_APP[handbook_type]}.{perm_type}_own_{p}{p_handbook_type}")

                if has_perm:
                    break

    return has_perm


def check_own_perm_by_field(obj, field, user, perm):
    if obj.get(f"{field}_id") == user.id:
        return user.has_perm(perm)
    return False


def model_to_dict(user, queryset, app, handbook_type, own=False):
    object_fields: list[str] | None = OBJECT_FIELDS.get(handbook_type)

    if object_fields:
        n_queryset = queryset.values(*object_fields)
    else:
        n_queryset = queryset.values()

    for i, instance in enumerate(n_queryset):
        if user.has_perm(f"{app}.change_{handbook_type}"):
            instance.update({
                "user_permissions": {
                    "can_update": True,
                }
            })
        elif own and user.has_perm(f"{app}.change_filial_{handbook_type}"):
            if isinstance(LIST_BY_USER[handbook_type], str):
                filials = getattr(queryset[i], LIST_BY_USER[handbook_type]).filials.all()
                if set(filials).intersection(set(user.filials.all())):
                    instance.update({
                        "user_permissions": {
                            "can_update": True,
                        }
                    })
        elif own and user.has_perm(f"{app}.change_own_{handbook_type}"):
            if isinstance(LIST_BY_USER[handbook_type], str) and \
                getattr(queryset[i], LIST_BY_USER[handbook_type]).id == user.id:
                    instance.update({
                        "user_permissions": {
                            "can_update": True,
                        }
                    })
        else:
            instance.update({
                "user_permissions": {
                    "can_update": False,
                }
            })
        """instance.update({
            "user_permissions": {
                "can_update": change_perm or user.has_perm(f"{app}.change_own_{handbook_type}")
                                    if own else change_perm
            }
        })"""
    return n_queryset


def by_user_queryset(queryset: QuerySet, handbook_type: str, filter_by, pref: Optional[str] = None) -> QuerySet:
    if isinstance(LIST_BY_USER[handbook_type], str):
        field = f"{LIST_BY_USER[handbook_type]}__{pref}" if pref else LIST_BY_USER[handbook_type]
        return queryset.filter(**{field: filter_by}).distinct()
    new_queryset = None
    for field in LIST_BY_USER[handbook_type]:
        if pref:
            field = f"{field}__{pref}"
        if new_queryset:
            new_queryset = new_queryset | queryset.filter(**{field: filter_by}).distinct()
        else:
            new_queryset = queryset.filter(**{field: filter_by}).distinct()
    return new_queryset


def get_office_context(user: CustomUser) -> dict[str, Any]:
    """
    Повертає контекст для сторінки офісу
    """
    context = {
        "my_clients": user.has_perm("handbooks.view_own_office_client"),
        "my_objects": user.has_perm("objects.view_own_office_objects"),
        "filial_clients": user.has_perm("handbooks.view_filial_office_client"),
        "filial_objects": user.has_perm("objects.view_filial_office_objects"),
        "report": user.has_perm("objects.view_office_report"),
        "users": user.has_perm("accounts.view_office_user"),
    }
    return context