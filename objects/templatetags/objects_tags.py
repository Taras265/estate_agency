from typing import TypeVar

from django import template


K = TypeVar("K")
V = TypeVar("V")

register = template.Library()

@register.filter(name="get_dict_value")
def get_dict_value(dictionary: dict[K, V], key: K) -> V | None:
    return dictionary.get(key)