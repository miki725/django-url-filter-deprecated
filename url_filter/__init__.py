__version__ = '0.1'
__author__ = 'Miroslav Shubernetskiy'

try:
    from .backend import DjangoFilterBackend
    from .filters import ModelFieldFilter
    from .filterset import FilterSet
except Exception:
    pass
