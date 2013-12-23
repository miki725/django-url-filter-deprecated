from __future__ import unicode_literals, print_function
import inspect
import six
from django.test import TestCase
from mock import MagicMock, patch
from random import randint
from url_filter.overwrites import (ModelDict,
                                   get_multiple_values_field,
                                   MODEL_FIELD_OVERWRITES,
                                   LOOKUP_TYPES_OVERWRITES)


class TestOverwrites(TestCase):
    def test_model_field_overwrites(self):
        self.assertIsInstance(MODEL_FIELD_OVERWRITES, ModelDict)

    def test_lookup_type_overwrites(self):
        self.assertIsInstance(LOOKUP_TYPES_OVERWRITES, dict)

    def test_model_dict_get(self):
        class Foo(object):
            pass

        class Bar(Foo):
            pass

        class Cat(object):
            pass

        m = ModelDict({
            Foo: 'parrot',
            'foo': 'bar',
        })

        self.assertIs(m.get('cat'), None)
        self.assertIs(m.get('foo'), 'bar')
        self.assertIs(m.get(Bar), 'parrot')
        self.assertIs(m.get(Cat), None)

    def test_get_multiple_values_field(self):
        v = randint(1, 100)
        field = MagicMock()
        field.clean.return_value = v

        with patch('url_filter.overwrites.MultipleValuesField') as mock:
            r = get_multiple_values_field()
            self.assertTrue(callable(r))
            r('', field)
            self.assertTrue(mock.called)

            calls = mock.call_args
            args, kwargs = calls
            mapping = kwargs['mapping']
            self.assertFalse(args)
            self.assertTrue(kwargs)
            self.assertEqual(set(kwargs.keys()), set(['min_values', 'mapping']))
            self.assertEqual(kwargs['min_values'], 2)
            self.assertTrue(callable(mapping))
            args = inspect.getargspec(mapping)
            self.assertEqual(len(args.args), 1)
            self.assertFalse(args.keywords)

            r = mapping('foo')
            field.clean.assert_called_with('foo')
            self.assertEqual(r, v)

        with patch('url_filter.overwrites.MultipleValuesField') as mock:
            kwargs = {
                six.text_type(randint(1, 100)): randint(1, 100),
                six.text_type(randint(1, 100)): randint(1, 100),
                six.text_type(randint(1, 100)): randint(1, 100),
                'mapping': randint(1, 100),
                'min_values': randint(1, 100),
            }
            r = get_multiple_values_field(**kwargs)
            r('', field)
            mock.assert_called_with(**kwargs)
