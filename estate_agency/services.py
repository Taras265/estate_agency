from typing import Optional, Any

from django.db.models import QuerySet, Model


def object_get(objects: QuerySet, *args: Any, **kwargs: Any) -> Model | None:
    return objects.filter(**kwargs).first()


def objects_all(objects: QuerySet, *args: Any, **kwargs: Any) -> QuerySet:
    return objects.all()


def objects_filter(objects: QuerySet, *args: Any, **kwargs: Any) -> QuerySet:
    return objects.filter(**kwargs)


def objects_all_visible(objects: QuerySet, *args: Any, **kwargs: Any) -> QuerySet:
    return objects_filter(objects, on_delete=False)


def object_create(objects: QuerySet, *args: Any, **kwargs: Any) -> Model:
    return objects.create(**kwargs)


def object_update(objects: QuerySet, pk: int, *args: Any, **kwargs: Any) -> Model | None:
    obj = object_get(objects, id=pk)

    if obj is None:
        return None

    for key, value in kwargs.items():
        setattr(obj, key, value)
    obj.save()
    return obj


def object_delete(objects: QuerySet, pk: int, *args: Any, **kwargs: Any) -> None:
    obj = object_get(objects, id=pk)

    if obj:
        obj.delete()
