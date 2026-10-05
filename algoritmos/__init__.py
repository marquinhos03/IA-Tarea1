from collections.abc import Callable
from typing import Any

from .busqueda_en_amplitud import busqueda_en_amplitud
from .busqueda_costo_uniforme import busqueda_costo_uniforme
from .busqueda_a_estrella import busqueda_a_estrella
from .busqueda_ida_estrella import busqueda_ida_estrella
from .busqueda_genetica import busqueda_genetica

_REGISTRY: dict[str, Callable[..., Any]] = {
    "bfs": busqueda_en_amplitud,
    "costo_uniforme": busqueda_costo_uniforme,
    "a_estrella": busqueda_a_estrella,
    "ida_estrella": busqueda_ida_estrella,
    "genetico": busqueda_genetica,
}

def get_algorithm(name: str) -> Callable[..., Any]:
    """Retorna la función del algoritmo correspondiente por su nombre."""

    key = name.strip().lower()
    if key not in _REGISTRY:
        disponibles = ", ".join(_REGISTRY.keys())
        raise ValueError(f"Algoritmo '{name}' no soportado. Disponibles: {disponibles}")
    return _REGISTRY[key]