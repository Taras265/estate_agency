from typing import List, Tuple, Any

from django.db.models import QuerySet

from accounts.models import CustomUser, CustomGroup
from estate_agency.services import object_get, objects_all_visible, objects_filter
from utils.const import TABLE_TO_APP


def get_user_choices(user: CustomUser, choices: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    available_choices = []
    for choice in choices:
        app: str = TABLE_TO_APP.get(choice[1])
        if ((user.has_perm(f'{app}.view_{choice[1]}')
             or user.has_perm(f'{app}.view_own_{choice[1]}'))):
            available_choices.append(choice)
    return available_choices


def user_get(objects: QuerySet = CustomUser.objects, *args: Any, **kwargs: Any) -> CustomUser | None:
    return object_get(objects, *args, **kwargs)


def user_all_visible(objects: QuerySet = CustomUser.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def user_filter(objects: QuerySet = CustomUser.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)


def group_all_visible(objects: QuerySet = CustomGroup.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_all_visible(objects, *args, **kwargs)


def group_filter(objects: QuerySet = CustomGroup.objects, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False, *args, **kwargs)