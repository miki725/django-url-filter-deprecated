from __future__ import unicode_literals, print_function
from django.db import models
from django.test import TestCase
from mock import MagicMock, patch
from random import randint
from url_filter.filters import (ModelFieldFilter,
                                ParseError,
                                ValidationError,
                                LOOKUP_SEP,
                                forms)


class TestModelFieldFilter(TestCase):
    def test_init(self):
        field = 'foo'
        key_field = MagicMock()
        default_lt = 'foo'
        default_lt_list = ['cat', 'dog']

        m = ModelFieldFilter(field)

        with patch.multiple(ModelFieldFilter,
                            default_key_form_field_class=key_field,
                            default_lookup_type=default_lt,
                            default_lookup_type_list=default_lt_list):
            # defaults
            m = ModelFieldFilter(field)

            self.assertIs(m.model_field, field)
            self.assertIs(m.key, None)
            self.assertIs(m.default_lookup_type, default_lt)
            self.assertIs(m.lookup_type, default_lt_list)
            key_field.assert_called_with(default_lookup_type=default_lt,
                                         lookup_type=default_lt_list)

            #key
            key = randint(1, 100)
            m = ModelFieldFilter(field, key=key)
            self.assertIs(m.key, key)

            # key_form_field_class
            key_field2 = MagicMock()
            m = ModelFieldFilter(field, key_form_field_class=key_field2)
            key_field2.assert_called_once_with(default_lookup_type=default_lt,
                                               lookup_type=default_lt_list)

            # default_lookup_type
            default_lt2 = randint(1, 100)
            key_field.reset_mock()
            m = ModelFieldFilter(field, default_lookup_type=default_lt2)
            key_field.assert_called_with(default_lookup_type=default_lt2,
                                         lookup_type=default_lt_list)

            # lookup_type
            default_lt_list2 = [randint(1, 100)]
            key_field.reset_mock()
            m = ModelFieldFilter(field, lookup_type=default_lt_list2)
            key_field.assert_called_with(default_lookup_type=default_lt,
                                         lookup_type=default_lt_list2)

            # lookup_type convert to list
            m = ModelFieldFilter(field, lookup_type='foo')
            self.assertEqual(m.lookup_type, ['foo'])

    def test_get_value_form_field(self):
        # no mfo and no lto
        # -----------------
        class Foo(models.Field):
            pass

        formfield = MagicMock()
        model = MagicMock(spec=Foo)
        model.formfield.return_value = formfield
        m = ModelFieldFilter(model)
        _mfo = MagicMock()
        _mfo.get.return_value = None
        mfo = MagicMock()
        mfo.get.return_value = _mfo
        _lto = MagicMock()
        _lto.get.return_value = None
        lto = MagicMock()
        lto.get.return_value = _lto
        with patch.multiple('url_filter.filters',
                            MODEL_FIELD_OVERWRITES=mfo,
                            LOOKUP_TYPES_OVERWRITES=lto):
            r = m.get_value_form_field('bar')
            self.assertIs(r, formfield)
            mfo.get.assert_called_with(Foo, {})
            lto.get.assert_called_with('bar', {})
            _mfo.get.assert_called_with('value_form_field', None)
            _lto.get.assert_called_with('value_form_field', None)

        # mfo
        # --------------
        class Bar(forms.Field):
            pass

        bar = Bar()
        _mfo.get.return_value = bar
        with patch.multiple('url_filter.filters',
                            MODEL_FIELD_OVERWRITES=mfo,
                            LOOKUP_TYPES_OVERWRITES=lto):
            r = m.get_value_form_field('bar')
            self.assertIs(r, bar)

        r1 = randint(1, 100)
        c = MagicMock()
        c.return_value = r1
        _mfo.get.return_value = c
        with patch.multiple('url_filter.filters',
                            MODEL_FIELD_OVERWRITES=mfo,
                            LOOKUP_TYPES_OVERWRITES=lto):
            r = m.get_value_form_field('bar')
            self.assertIs(r, r1)
            c.assert_called_with(model, formfield)

        # cto
        # --------------
        class Cat(forms.Field):
            pass

        cat = Cat()
        _lto.get.return_value = cat
        with patch.multiple('url_filter.filters',
                            MODEL_FIELD_OVERWRITES=mfo,
                            LOOKUP_TYPES_OVERWRITES=lto):
            r = m.get_value_form_field('bar')
            self.assertIs(r, cat)

        r2 = randint(1, 100)
        c = MagicMock()
        c.return_value = r2
        _lto.get.return_value = c
        with patch.multiple('url_filter.filters',
                            MODEL_FIELD_OVERWRITES=mfo,
                            LOOKUP_TYPES_OVERWRITES=lto):
            r = m.get_value_form_field('bar')
            self.assertIs(r, r2)
            c.assert_called_with(model, r1)

    def test_filter_dict(self):
        m = ModelFieldFilter('')
        key = ['foo{0}'.format(randint(1, 100)), 'exact', True]
        value = randint(1, 100)

        key_field = MagicMock()
        key_field.clean.side_effect = ValidationError('')
        with patch.object(m, 'key_form_field', key_field):
            with self.assertRaises(ParseError):
                r = randint(1, 100)
                m.filter_dict('', r, '')
                key_field.clean.assert_called_with(r)

        key_field = MagicMock()
        key_field.clean.return_value = key
        value_field = MagicMock()
        value_field.clean.side_effect = ValidationError('')
        value_field_getter = MagicMock()
        value_field_getter.return_value = value_field
        with patch.multiple(m,
                            key_form_field=key_field,
                            get_value_form_field=value_field_getter):
            with self.assertRaises(ParseError):
                r = randint(1, 100)
                m.filter_dict('', '', r)
                value_field.clean.assert_called_with(r)

        key_field.reset_mock()
        key_field.clean.return_value = key
        value_field = MagicMock()
        value_field.clean.return_value = value
        value_field_getter = MagicMock()
        value_field_getter.return_value = value_field
        with patch.multiple(m,
                            key_form_field=key_field,
                            get_value_form_field=value_field_getter):
            r1 = randint(1, 100)
            r2 = randint(1, 100)
            r = m.filter_dict('', r1, r2)
            key_field.clean.assert_called_with(r1)
            value_field.clean.assert_called_with(r2)
            self.assertIsInstance(r, dict)
            self.assertEqual(set(r.keys()), set(['filter', 'exclude']))
            self.assertIsInstance(r['filter'], dict)
            self.assertIsInstance(r['exclude'], dict)
            self.assertEqual(r['filter'], {
                '{0}{1}{2}'.format(key[0], LOOKUP_SEP, key[1]): value,
            })
            self.assertFalse(r['exclude'])

        key = ['foo{0}'.format(randint(1, 100)), 'exact', False]
        key_field.reset_mock()
        key_field.clean.return_value = key
        with patch.multiple(m,
                            key_form_field=key_field,
                            get_value_form_field=value_field_getter):
            r = m.filter_dict('', '', '')
            self.assertFalse(r['filter'])
            self.assertEqual(r['exclude'], {
                '{0}{1}{2}'.format(key[0], LOOKUP_SEP, key[1]): value,
            })

    def test_filter(self):
        qs = MagicMock()
        qs.filter.return_value = qs
        args = ('foo{0}'.format(randint(1, 100)),)
        kwargs = {'foo{0}'.format(randint(1, 100)): 'foo{0}'.format(randint(1, 100))}
        filter_dict = MagicMock()
        filters = {
            'filter': {
                'foo{0}'.format(randint(1, 100)): 'foo{0}'.format(randint(1, 100))
            },
            'exclude': {
                'foo{0}'.format(randint(1, 100)): 'foo{0}'.format(randint(1, 100))
            },
        }
        filter_dict.return_value = filters

        with patch.object(ModelFieldFilter, 'filter_dict', filter_dict):
            m = ModelFieldFilter('')
            m.filter(qs, *args, **kwargs)
            filter_dict.assert_called_with(qs, *args, **kwargs)
            qs.filter.assert_called_with(**filters['filter'])
            qs.exclude.assert_called_with(**filters['exclude'])
