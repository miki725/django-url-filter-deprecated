from __future__ import unicode_literals, print_function
import six
from copy import deepcopy
from django_auxilium.utils.functools import cache
from .utils import filters_for_model, get_declared_filters


class FilterSetOptions(object):
    def __init__(self, options=None):
        g = lambda k, d: getattr(options, k, d)

        self.model = g('model', None)
        self.fields = g('fields', None)
        self.exclude = g('exclude', None)


class FilterSetMeta(type):
    def __new__(cls, name, bases, attrs):
        try:
            any_parents = any([b for b in bases if issubclass(b, FilterSet)])
        except NameError:
            any_parents = False
        declared_filters = get_declared_filters(bases, attrs)
        new_class = super(FilterSetMeta, cls).__new__(cls, name, bases, attrs)

        # creating FilterSet itself
        if not any_parents:
            return new_class

        opts = new_class._meta = FilterSetOptions(attrs.get('Meta', None))
        if opts.model:
            filters = filters_for_model(opts.model,
                                        opts.fields,
                                        opts.exclude)
            filters.update(declared_filters)
        else:
            filters = declared_filters

        # make sure filters ``model_field`` is instance of ``models.Field``
        for f in filters.values():
            if isinstance(f.model_field, six.string_types):
                if not opts.model:
                    raise ValueError(
                        '``model`` was not defined in filterset\'s ``Meta`` hence '
                        'for filter `{0}`, model field cannot be determined.'
                        ''.format(f.model_field))
                f.model_field = opts.model._meta.get_field_by_name(f.model_field)

        new_class.base_filters = filters

        return new_class


class BaseFilterSet(object):
    def __init__(self, data=None, queryset=None):
        self.data = data or {}
        if queryset is None:
            queryset = self._meta.model.objects.all()
        self.queryset = queryset

        self.filters = deepcopy(self.base_filters)

    @property
    @cache
    def qs(self):
        if not self.data:
            return self.queryset

        kwargs = {
            'filter': {},
            'exclude': {},
        }

        for k, v in self.data.items():
            # find filter for key
            filter = None
            for f in self.filters.keys():
                if k.startswith(f):
                    filter = self.filters[f]
                    break
            if not filter:
                continue

            kwarg = filter.filter_dict(self.queryset, k, v)
            kwargs['filter'].update(kwarg['filter'])
            kwargs['exclude'].update(kwarg['exclude'])

        if kwargs['filter'] or kwargs['exclude']:
            qs = self.queryset
            if kwargs['filter']:
                qs = qs.filter(**kwargs['filter'])
            if kwargs['exclude']:
                qs = qs.exclude(**kwargs['exclude'])
            return qs

        return self.queryset


class FilterSet(six.with_metaclass(FilterSetMeta, BaseFilterSet)):
    pass
