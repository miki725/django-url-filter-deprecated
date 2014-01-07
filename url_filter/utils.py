from __future__ import unicode_literals, print_function
import six
try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict
from .filters import ModelFieldFilter


def get_filters_dict(filters):
    """
    Get ordered dictionary of given filters.
    """
    return OrderedDict([(f.key, f) for f in filters])


def filters_for_model(model, fields=None, exclude=None):
    """
    Get all filters for a given model.

    Parameters
    ----------
    model : Model
        Model class for which to get filers
    fields : list, tuple, optional
        List of fields for which to get filters.
        If ``None``, all model fields will be used.
        Default is ``None``.
    exclude : list, tuple, optional
        List of model field names which should be ignored.
        Default is ``None``.
    """
    opts = model._meta
    exclude = exclude or []
    if fields is None:
        fields = [(f.name, f) for f in opts.fields]
    else:
        fields = [(f, opts.get_field_by_name(f)[0]) for f in fields]

    filters = []

    for name, field in fields:
        if name in exclude:
            continue

        filters.append(ModelFieldFilter(field, key=name))

    return get_filters_dict(filters)


def get_declared_filters(bases, attrs):
    """
    Get declared filters in a FieldSet definition.
    This also return filters from the base classes.
    """
    filters = []
    for filter_name, filter in list(attrs.items()):
        if not isinstance(filter, ModelFieldFilter):
            continue
        filter = attrs.pop(filter_name)
        if filter.key is None:
            filter.key = filter_name
        filters.append(filter)

    filters = get_filters_dict(filters)

    for base in bases[::-1]:
        if hasattr(base, 'base_filters'):
            all_filters = base.base_filters.copy()
            all_filters.update(filters)
            filters = all_filters

    return filters
