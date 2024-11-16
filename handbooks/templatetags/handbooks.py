from django import template
from django.template.defaultfilters import stringfilter

from utils.const import TABLE_TO_APP

register = template.Library()


@register.simple_tag
@stringfilter
def url_app(value):
    data = TABLE_TO_APP.get(value) or 'objects'
    return data
