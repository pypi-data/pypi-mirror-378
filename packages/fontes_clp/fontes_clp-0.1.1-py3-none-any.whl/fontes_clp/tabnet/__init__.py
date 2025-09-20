from . import grupos, obitos

from .grupos import GruposObitos, GruposCausas
from .obitos import TabNetObitos
from .morbidade import TabNetMorbidades

__all__ = [
    "GruposObitos",
    "GruposCausas",
    "TabNetObitos",
    "TabNetMorbidades",
    "grupos",
    "obitos",
    "morbidade",
]
