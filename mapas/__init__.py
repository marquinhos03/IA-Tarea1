# ======================================
# MODULO GENERADO CON IA
# ======================================

from collections.abc import Callable
from typing import Any

from mapa import Mapa

from .mapa_1 import obtener_mapa_1, POSICIONES_AGENTES_MAPA_1
from .mapa_2 import obtener_mapa_2, POSICIONES_AGENTES_MAPA_2
from .mapa_3 import obtener_mapa_3, POSICIONES_AGENTES_MAPA_3
from .mapa_1_benchmark import obtener_mapa_1_benchmark
from .mapa_2_benchmark import obtener_mapa_2_benchmark
from .mapa_3_benchmark import obtener_mapa_3_benchmark

_MAPAS: dict[str, Callable[..., Any]] = {
    "mapa_1": obtener_mapa_1,
    "mapa_2": obtener_mapa_2,
    "mapa_3": obtener_mapa_3,
    "mapa_1_benchmark": obtener_mapa_1_benchmark,
    "mapa_2_benchmark": obtener_mapa_2_benchmark,
    "mapa_3_benchmark": obtener_mapa_3_benchmark,
}


_POSICIONES_AGENTES: dict[str, list[tuple[int, int]]] = {
    "mapa_1": POSICIONES_AGENTES_MAPA_1,
    "mapa_2": POSICIONES_AGENTES_MAPA_2,
    "mapa_3": POSICIONES_AGENTES_MAPA_3,
}


def obtener_mapa(numero: int, benchmark: bool = False, capacidad_celda: int = 1) -> Mapa:
    """Retorna la instancia del mapa correspondiente según su número y configuración."""

    suffix = "_benchmark" if benchmark else ""
    key = f"mapa_{numero}{suffix}"
    if key not in _MAPAS:
        disponibles = ", ".join(_MAPAS.keys())
        raise ValueError(f"Mapa '{key}' no soportado. Disponibles: {disponibles}")
    return _MAPAS[key](capacidad_celda=capacidad_celda)


def obtener_posiciones_agentes(numero: int) -> list[tuple[int, int]]:
    """Retorna una lista de posiciones iniciales de los agentes para el mapa correspondiente."""

    key = f"mapa_{numero}"
    if key not in _POSICIONES_AGENTES:
        disponibles = ", ".join(_POSICIONES_AGENTES.keys())
        raise ValueError(f"Mapa '{key}' no soportado para posiciones de agentes. Disponibles: {disponibles}")
    return list(_POSICIONES_AGENTES[key])
