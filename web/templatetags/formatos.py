from django import template

register = template.Library()

@register.filter
def clp_format(value):
    try:
        value = int(value)
        return "${:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value