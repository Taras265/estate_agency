from typing import TypeVar

from django import template
from django.utils.html import format_html

K = TypeVar("K")
V = TypeVar("V")

register = template.Library()


@register.filter(name="get_dict_value")
def get_dict_value(dictionary: dict[K, V], key: K) -> V | None:
    return dictionary.get(key)


@register.simple_tag
def get_model_name(obj):
    return obj.__class__.__name__.lower()


@register.simple_tag(takes_context=True)
def next_sort_direction(context, field):
    """
    Обчислює якою має бути сортировка
    """
    request = context['request']
    current_sort = request.GET.get('sort')
    current_direction = request.GET.get('direction', 's')

    if current_sort == field:
        return 'd' if current_direction == 's' else 's'
    return 's'