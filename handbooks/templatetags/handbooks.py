from django import template
from django.template.defaultfilters import stringfilter
from django.utils.translation import gettext_lazy as _

from utils.const import TABLE_TO_APP, BASE_CHOICES

register = template.Library()


@register.simple_tag
@stringfilter
def url_app(value):
    data = TABLE_TO_APP.get(value) or 'objects'
    return data


@register.simple_tag
@stringfilter
def choices_url(value):
    if (_(value), value) in BASE_CHOICES:
        return 'base'
    return 'sale'
