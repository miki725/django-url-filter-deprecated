from __future__ import unicode_literals, print_function
from django import forms
from django.db import models
from django.db.models.sql.constants import QUERY_TERMS
from rest_framework.exceptions import ParseError
from .overwrites import MODEL_FIELD_OVERWRITES, LOOKUP_TYPES_OVERWRITES
from .fields import KeyLookupField, ValidationError, LOOKUP_SEP


class ModelFieldFilter(object):
    """
    Parameters
    ----------
    model_field : Field
        Django model's ``Field`` instance for which the filter
        is being created. The field is required because it is used
        to get the default form field for validating querydict values.
    key : str, optional
        The name of the ``QueryDict`` key for filtering excluding lookup_type.
        Default is the name of the field.
    key_form_field_class : Field, optional.
        Django form's ``Field`` subclass which will be used to validate the
        ``QueryDict`` key including the lookup type.
        Default is ``KeyLookupField``.
    default_lookup_type : str, optional
        When the lookup type is not specified in the ``QueryDict``'s key,
        this lookup type will be used.
        Default is ``'exact'``.
    lookup_type : str, list, optional
        Either a single or a list of supported lookup types.
        Default are all lookup types.
    """
    default_key_form_field_class = KeyLookupField
    default_lookup_type = 'exact'
    default_lookup_type_list = QUERY_TERMS

    def __init__(self,
                 model_field, key=None,
                 key_form_field_class=None,
                 default_lookup_type=None,
                 lookup_type=None):
        self.model_field = model_field
        self.key = key
        self.key_form_field_class = (key_form_field_class or
                                     self.default_key_form_field_class)
        self.default_lookup_type = (default_lookup_type or
                                    self.default_lookup_type)
        if lookup_type is None:
            lookup_type = self.default_lookup_type_list
        if not isinstance(lookup_type, (list, tuple, set)):
            lookup_type = [lookup_type]
        self.lookup_type = lookup_type

        kwargs = {
            'default_lookup_type': self.default_lookup_type,
            'lookup_type': self.lookup_type,
        }
        self.key_form_field = self.key_form_field_class(**kwargs)

    def get_value_form_field(self, lookup_type):
        if not isinstance(self.model_field, models.Field):
            print(self.model_field)
            raise TypeError('Filter\'s ``model_field`` must be an instance of '
                            '``models.Field``.')

        field = self.model_field.formfield()

        # model field overwrite
        mfo = MODEL_FIELD_OVERWRITES.get(self.model_field.__class__, {})
        mfo = mfo.get('value_form_field', None)
        if mfo:
            if isinstance(mfo, forms.Field):
                field = mfo
            elif callable(mfo):
                field = mfo(self.model_field, field)

        # lookup types overwrite
        # isnull required boolean field
        lto = LOOKUP_TYPES_OVERWRITES.get(lookup_type, {})
        lto = lto.get('value_form_field', None)
        if lto:
            if isinstance(lto, forms.Field):
                field = lto
            elif callable(lto):
                field = lto(self.model_field, field)

        return field

    def filter_dict(self, qs, key, value):
        """
        Filter the queryset.
        """
        try:
            key, lookup_type, negation = self.key_form_field.clean(key)
        except ValidationError as e:
            raise ParseError('{0}: {1}'.format(self.key, e.message))

        value_form_field = self.get_value_form_field(lookup_type)
        try:
            value = value_form_field.clean(value)
        except ValidationError as e:
            raise ParseError('{0}: {1}'.format(self.key, e.message))

        filter_kwargs = {}
        exclude_kwargs = {}

        if negation:
            update = filter_kwargs
        else:
            update = exclude_kwargs

        update.update({
            '{0}{1}{2}'.format(key, LOOKUP_SEP, lookup_type): value
        })

        return {
            'filter': filter_kwargs,
            'exclude': exclude_kwargs,
        }

    def filter(self, qs, *args, **kwargs):
        """
        Filter the queryset by calling either ``filter`` or ``exclude``
        with the correct value.
        """
        kwargs = self.filter_dict(qs, *args, **kwargs)
        if kwargs['filter']:
            qs = qs.filter(**kwargs['filter'])
        if kwargs['exclude']:
            qs = qs.exclude(**kwargs['exclude'])
        return qs
