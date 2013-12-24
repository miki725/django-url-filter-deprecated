from __future__ import unicode_literals, print_function
from rest_framework.filters import DjangoFilterBackend
from .filterset import FilterSet


class URLDjangoFilterBackend(DjangoFilterBackend):
    """
    Filter Backend for Django REST Framework.
    It is very similar to the default ``DjangoFilterBackend``,
    except that it redefined the default ``FilterSet``.
    The name is kept the same so that existing code can be
    swapped to this by just changing the import.
    """
    default_filter_set = FilterSet

    def __init__(self):
        """
        Remove assertion about ``django-filter``.
        """
        pass
