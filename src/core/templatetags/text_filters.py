from django import template

from src.core.utils import full_url_for_path

register = template.Library()

@register.filter
def full_url_filter(value):
    return full_url_for_path(value)