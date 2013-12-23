from __future__ import unicode_literals, print_function
import inspect
from django.db import models
from django import forms
from django_auxilium.forms import MultipleValuesField


class ModelDict(dict):
    def get(self, k, d=None):
        """
        If no value is found by using Python's default implementation,
        try to find the value where the key is a base class of the
        provided search key.

        This is useful for finding field overwrites by class
        for custom Django model fields (illustrated below).

        Example
        -------

        ::

            >>> from django import forms
            >>> class ImgField(forms.ImageField):
            ...     pass
            >>> overwrites = ModelDict({
            ...     forms.CharField: 'foo',
            ...     forms.FileField: 'bar',
            ... })
            >>> print(overwrites.get(forms.CharField))
            foo
            >>> print(overwrites.get(ImgField))
            bar
        """
        value = super(ModelDict, self).get(k, d)

        # try to match by value
        if value is d and inspect.isclass(k):
            for model, opts in self.items():
                if not inspect.isclass(model):
                    continue
                if issubclass(k, model):
                    return opts

        return value


def get_multiple_values_field(**kwargs):
    def wrapper(model, field):
        mapping = lambda v: field.clean(v)
        params = {
            'min_values': 2,
            'mapping': mapping,
        }
        params.update(kwargs)
        return MultipleValuesField(**params)

    return wrapper


MODEL_FIELD_OVERWRITES = ModelDict({
    models.AutoField: {
        'value_form_field': forms.IntegerField(min_value=0),
    },
    models.FileField: {
        'value_form_field': lambda m, f: forms.CharField(max_length=m.max_length),
    },
})

LOOKUP_TYPES_OVERWRITES = {
    'in': {
        'value_form_field': get_multiple_values_field(),
    },
    'range': {
        'value_form_field': get_multiple_values_field(max_values=2),
    },
    'isnull': {
        'value_form_field': forms.BooleanField(),
    },
    'second': {
        'value_form_field': forms.IntegerField(min_value=0, max_value=59),
    },
    'minute': {
        'value_form_field': forms.IntegerField(min_value=0, max_value=59),
    },
    'hour': {
        'value_form_field': forms.IntegerField(min_value=0, max_value=23),
    },
    'week_day': {
        'value_form_field': forms.IntegerField(min_value=1, max_value=7),
    },
    'day': {
        'value_form_field': forms.IntegerField(min_value=1, max_value=31),
    },
    'month': {
        'value_form_field': forms.IntegerField(),
    },
    'year': {
        'value_form_field': forms.IntegerField(min_value=0, max_value=9999),
    },
}
