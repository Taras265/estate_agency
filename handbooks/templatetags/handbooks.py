from django import template
from django.template.defaultfilters import stringfilter

from utils.utils import table_to_app

register = template.Library()


@register.simple_tag
@stringfilter
def url_app(value):
    data = table_to_app(value) or "objects"
    return data
