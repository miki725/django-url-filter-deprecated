from __future__ import unicode_literals, print_function
from django.core.validators import RegexValidator, ValidationError
from django.forms import CharField
from django.db.models.sql.constants import QUERY_TERMS
from django.test import TestCase
from mock import patch
from random import randint
import re
import six

from url_filter.fields import (KeyLookupValidator,
                               KeyLookupField,
                               key_lookup_validator,
                               LOOKUP_SEP)


class TestKeyLookupValidator(TestCase):
    def test_class(self):
        self.assertTrue(issubclass(KeyLookupValidator, RegexValidator))

    def test_regex_defined(self):
        re_type = type(re.compile(''))
        self.assertIsInstance(KeyLookupValidator.regex, re_type)

    def test_call(self):
        v = KeyLookupValidator()
        v('foo')
        v('foo{0}foo'.format(LOOKUP_SEP))
        v('foo{0}!foo'.format(LOOKUP_SEP))

        with self.assertRaises(ValidationError):
            v('foo{0}foo&'.format(LOOKUP_SEP))


class TestKeyLookupField(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = KeyLookupField()

    def test_class(self):
        self.assertTrue(issubclass(KeyLookupField, CharField))

    def test_validatators(self):
        self.assertIn(key_lookup_validator, self.f.validators)

    def test_to_python(self):
        r1 = 'f' + six.text_type(randint(1, 100))
        r2 = 'f' + six.text_type(randint(1, 100))

        with patch.object(self.f, 'default_lookup_type', r2):
            result = self.f.to_python(r1)
            self.assertIsInstance(result, list)
            self.assertEqual(result, [r1, r2, True])

            result = self.f.to_python('{0}__!{1}'.format(r1, r2))
            self.assertIsInstance(result, list)
            self.assertEqual(result, [r1, r2, False])

    def test_validate(self):
        for term in QUERY_TERMS:
            self.f.validate(['', term, True])
            self.assertTrue(True)

        with self.assertRaises(ValidationError):
            self.f.validate(['', 'foo', True])

        f = KeyLookupField(lookup_type=['foo'])
        f.validate(['', 'foo', True])
        self.assertTrue(True)
        with self.assertRaises(ValidationError):
            self.f.validate(['', 'bar', True])

    def test_clean(self):
        self.f.clean('foo')
        self.assertTrue(True)

        self.f.clean('foo__exact')
        self.assertTrue(True)

        self.f.clean('foo__!exact')
        self.assertTrue(True)

        with self.assertRaises(ValidationError):
            self.f.clean('foo__')
        with self.assertRaises(ValidationError):
            self.f.clean('foo__exact__foo')
