from django import template
from django.template.defaultfilters import stringfilter

from utils.const import BASE_CHOICES, SALE_CHOICES, TABLE_TO_APP

register = template.Library()


@register.simple_tag
@stringfilter
def url_app(value):
    data = TABLE_TO_APP.get(value) or "objects"
    return data


@register.simple_tag
@stringfilter
def choices_url(value):
    for choice in BASE_CHOICES:
        if value == choice[1]:
            return "base"
    for choice in SALE_CHOICES:
        if value == choice[1]:
            return "sale"
    return "accounts"
