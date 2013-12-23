from __future__ import unicode_literals, print_function
import re
import six
from django import forms
from django.core.validators import RegexValidator, ValidationError
from django.db.models.sql.constants import QUERY_TERMS

try:
    from django.db.models.constants import LOOKUP_SEP
except ImportError:
    from django.db.models.sql.constants import LOOKUP_SEP

LOOKUP_RE = re.compile(r'^(?:[^\d\W]\w*)(?:{0}!?[^\d\W]\w*)?$'
                       r''.format(LOOKUP_SEP), re.IGNORECASE)


class KeyLookupValidator(RegexValidator):
    regex = LOOKUP_RE
    message = 'Lookup key is of invalid format. It must be `name[__[!]method]`.'


key_lookup_validator = KeyLookupValidator()


class KeyLookupField(forms.CharField):
    """
    ``QueryDict`` parsing field which also validates the key.

    Parameters
    ----------
    default_lookup_type : str, optional
        Default lookup type when it is not specified in the ``QueryDict`` key.
        Default is ``'exact'``.
    lookup_type : list, None, optional
        Either a list of all supported lookup types or ``None``
        to support all Django query terms.
        Default is ``None``.

    Example
    -------

    ::

        >>> field = KeyLookupField()

        >>> v = field.clean('foo')
        >>> print(v[0])
        foo
        >>> print(v[1])
        exact
        >>> print(v[2])
        True
        
        >>> v = field.clean('foo__contains')
        >>> print(v[0])
        foo
        >>> print(v[1])
        contains
        >>> print(v[2])
        True

        >>> v = field.clean('foo__!exact')
        >>> print(v[0])
        foo
        >>> print(v[1])
        exact
        >>> print(v[2])
        False

        >>> try:
        ...     field.clean('foo__bar')
        ... except ValidationError:
        ...        print('Invalid')
        Invalid
    """
    default_validators = [key_lookup_validator]
    default_error_messages = {
        'invalid_lookup_type': 'Unsupported lookup type - `{0}`.'
    }

    def __init__(self,
                 default_lookup_type='exact',
                 lookup_type=None,
                 *args, **kwargs):
        super(KeyLookupField, self).__init__(*args, **kwargs)

        self.default_lookup_type = default_lookup_type
        if lookup_type is None:
            lookup_type = QUERY_TERMS
        self.lookup_type = lookup_type

    def to_python(self, value):
        """
        Parse the key value into ``[key, lookup_type, negation]``.

        Returns
        -------
        value : list
            Value consisting of ``[key, lookup_type, negation]``.
            If nagation is ``False``, then ``exclude`` should be used
            instead of ``filter``.
        """
        value = super(KeyLookupField, self).to_python(value)
        values = value.split(LOOKUP_SEP, 1)

        if not len(values) == 2:
            values.append(self.default_lookup_type)

        values.append(not values[1].startswith('!'))

        if not values[2]:
            values[1] = values[1][1:]

        return values

    def validate(self, value):
        """
        Check that the lookup type is one of supported lookup types
        as provided in ``__init__``.
        """
        if value[1] not in self.lookup_type:
            raise ValidationError(
                self.error_messages['invalid_lookup_type'].format(value[1]))

    def clean(self, value):
        """
        Clean value. This is very similar to Django's default ``clean``
        method except here the first thing is validation against
        validators.
        """
        self.run_validators(value)
        value = self.to_python(value)
        self.validate(value)
        return value
