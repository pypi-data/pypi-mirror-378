from importlib.metadata import version

try:
    __version__ = version("fontes_clp")
except:
    __version__ = "0.1.0"

from .common import Estado, Sexo
from .tabnet import GruposObitos, GruposCausas, TabNetObitos, TabNetMorbidades
from .ibge import IBGEPopulacao

__all__ = [
    "Estado",
    "Sexo",
    "GruposObitos",
    "GruposCausas",
    "TabNetObitos",
    "TabNetMorbidades",
    "IBGEPopulacao",
    "common",
    "tabnet",
    "ibge",
]
