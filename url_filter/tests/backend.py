from __future__ import unicode_literals, print_function
from django.test import TestCase
from rest_framework.filters import DjangoFilterBackend as DefaultFilterBackend
from url_filter.backend import DjangoFilterBackend, FilterSet


class TestDjangoFilterBackend(TestCase):
    def test_class(self):
        self.assertTrue(issubclass(DjangoFilterBackend.default_filter_set,
                                   FilterSet))

    def test_django_filters_assertion(self):
        try:
            DefaultFilterBackend()
        except AssertionError:
            # no assertion should happen
            # even default raises exception
            DjangoFilterBackend()
            self.assertTrue(True)
