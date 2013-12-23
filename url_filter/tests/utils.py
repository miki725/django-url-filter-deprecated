from __future__ import unicode_literals, print_function
from django.test import TestCase
from mock import MagicMock, patch
from random import randint
from url_filter.filters import ModelFieldFilter
from url_filter.utils import (get_filters_dict,
                              filters_for_model,
                              get_declared_filters)

try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict


class TestUtils(TestCase):
    def test_get_filters_dict(self):
        r = get_filters_dict([])
        self.assertIsInstance(r, OrderedDict)

        a = type(str('A'), (object,), {'key': 'foo'})
        b = type(str('B'), (object,), {'key': 'bar'})
        r = get_filters_dict([a, b])
        self.assertEqual(r, {'foo': a, 'bar': b})

    def test_filters_for_model(self):
        field = MagicMock()
        filter_dict = MagicMock()
        filter_dict.side_effect = lambda x: x

        class Foo(object):
            pass

        model = Foo()
        opts = model._meta = Foo()
        f1 = Foo()
        f1.name = 'foo'.format(randint(1, 100))
        f2 = Foo()
        f2.name = 'bar'.format(randint(1, 100))
        opts.fields = [f1, f2]

        # default
        with patch.multiple('url_filter.utils',
                            ModelFieldFilter=field,
                            get_filters_dict=filter_dict):
            r = filters_for_model(model)
            self.assertEqual(len(field.mock_calls), 2)
            field.assert_any_called_with(f1, key=f1.name)
            field.assert_any_called_with(f2, key=f2.name)
            filter_dict.assert_called_with(r)

        # exclude
        with patch.multiple('url_filter.utils',
                            ModelFieldFilter=field,
                            get_filters_dict=filter_dict):
            r = filters_for_model(model, exclude=[f2.name])
            field.assert_called_with(f1, key=f1.name)

        # fields
        field.reset_mock()
        opts = model._meta = MagicMock()
        opts.get_field_by_name.return_value = [f1]
        with patch.multiple('url_filter.utils',
                            ModelFieldFilter=field,
                            get_filters_dict=filter_dict):
            r = filters_for_model(model, fields=[f1.name])
            opts.get_field_by_name.assert_called_with(f1.name)
            field.assert_called_with(f1, key=f1.name)

    def test_get_declared_filters(self):
        filter_dict = MagicMock()
        filter_dict.side_effect = lambda x: get_filters_dict(x)

        # valid filter
        filter = MagicMock(spec=ModelFieldFilter)
        filter.key = randint(1, 100)
        attrs = MagicMock()
        attrs.items.return_value = [('foo', filter)]
        attrs.pop.return_value = filter

        with patch.multiple('url_filter.utils',
                            get_filters_dict=filter_dict):
            r = get_declared_filters([], attrs)
            attrs.items.assert_called_with()
            attrs.pop.assert_called_with('foo')
            filter_dict.assert_called_with([filter])
            self.assertEqual(r, {filter.key: filter})

        # filter without key
        filter.key = None

        with patch.multiple('url_filter.utils',
                            get_filters_dict=filter_dict):
            r = get_declared_filters([], attrs)
            self.assertEqual(list(r.values())[0].key, 'foo')

        # base classes
        filters = {'cat': filter}
        base = type(str('Base'), (object,), {
            'base_filters': filters,
        })
        all_filters = dict(filters)
        all_filters.update({'foo': filter})
        with patch.multiple('url_filter.utils',
                            get_filters_dict=filter_dict):
            r = get_declared_filters([base], attrs)
            self.assertEqual(dict(r), all_filters)

        # invalid filter
        filter = MagicMock()
        attrs.reset_mock()
        attrs.items.return_value = [('foo', filter)]

        with patch.multiple('url_filter.utils',
                            get_filters_dict=filter_dict):
            r = get_declared_filters([], attrs)
            self.assertFalse(attrs.pop.called)
            self.assertFalse(r)
