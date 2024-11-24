from django import template

register = template.Library()


@register.filter
def add_class(value, css_class):
    return value.as_widget(attrs={'class': css_class})


@register.filter
def to(value):
    return range(1, int(value) + 1)
