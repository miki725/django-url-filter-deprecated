from __future__ import unicode_literals, print_function
from django.test import TestCase
from rest_framework.filters import DjangoFilterBackend
from url_filter.backend import URLDjangoFilterBackend, FilterSet


class TestDjangoFilterBackend(TestCase):
    def test_class(self):
        self.assertTrue(issubclass(URLDjangoFilterBackend.default_filter_set,
                                   FilterSet))

    def test_django_filters_assertion(self):
        try:
            DjangoFilterBackend()
        except AssertionError:
            # no assertion should happen
            # even default raises exception
            URLDjangoFilterBackend()
            self.assertTrue(True)
