import json

from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe


register = Library()


@register.filter(name='add_class')
def add_class(value, arg):
    """
    Extend widget classes collection
    :param value: form field
    :param arg: class name
    :return: updated form field
    """
    cls = value.field.widget.attrs.get('class') or ''
    return value.as_widget(attrs={'class': arg + ' ' + cls})


@register.simple_tag
def get_attr(obj, attr):
    return getattr(obj, attr)


@register.simple_tag
def replace(value, arg1, arg2):
    """
    Python's replace analog
    """
    return value.replace(arg1, arg2)


@register.simple_tag
def settings_value(name):
    """
    Get django settings variable by name
    :param name: variable name
    :return: setting value
    """
    value = getattr(settings, name, "")
    if isinstance(value, (list, tuple)):
        value = mark_safe(list(value))
    return value


@register.simple_tag
def get_settings_value(name):
    """
    Get django settings variable by name
    :param name: variable name
    :return: setting value
    """
    return settings_value(name)


@register.filter(name='simple_replace')
def simple_replace(value, repl):
    return value.replace('REPLACE', str(repl))


@register.filter(name='linebreak_replace')
def linebreak_replace(value, repl='<br />'):
    return mark_safe(value.replace('\n', repl))


@register.filter(name='is_in')
def is_in(value, collection):
    return value in collection


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))


@register.filter(name='get_field_type')
def get_field_type(form_field):
    """
    Get form field type
    """
    return form_field.field.__class__.__name__.lower()
