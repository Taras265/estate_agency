from django import template
from django.template.defaultfilters import stringfilter

from utils.const import BASE_CHOICES, SALE_CHOICES
from utils.utils import table_to_app

register = template.Library()


@register.simple_tag
@stringfilter
def url_app(value):
    data = table_to_app(value) or "objects"
    return data


@register.simple_tag
@stringfilter
def choices_url(value):
    for choice in BASE_CHOICES:
        if value == choice:
            return "base"
    for choice in SALE_CHOICES:
        if value == choice:
            return "sale"
    return "accounts"
