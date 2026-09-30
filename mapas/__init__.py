from mapa import Mapa

from .mapa_1 import obtener_mapa_1, POSICIONES_AGENTES_MAPA_1
from .mapa_2 import obtener_mapa_2, POSICIONES_AGENTES_MAPA_2
from .mapa_3 import obtener_mapa_3, POSICIONES_AGENTES_MAPA_3

from .mapa_1_benchmark import obtener_mapa_1_benchmark
from .mapa_2_benchmark import obtener_mapa_2_benchmark
from .mapa_3_benchmark import obtener_mapa_3_benchmark


_MAPAS_NORMALES = {
    1: obtener_mapa_1,
    2: obtener_mapa_2,
    3: obtener_mapa_3,
}

_MAPAS_BENCHMARK = {
    1: obtener_mapa_1_benchmark,
    2: obtener_mapa_2_benchmark,
    3: obtener_mapa_3_benchmark,
}

_POSICIONES_AGENTES = {
    1: POSICIONES_AGENTES_MAPA_1,
    2: POSICIONES_AGENTES_MAPA_2,
    3: POSICIONES_AGENTES_MAPA_3,
}


def obtener_mapa(numero: int, benchmark: bool = False, capacidad_celda: int = 1) -> Mapa:
    constructor = _MAPAS_BENCHMARK[numero] if benchmark else _MAPAS_NORMALES[numero]
    instancia = constructor(capacidad_celda=capacidad_celda)
    instancia.numero = numero
    return instancia


def obtener_posiciones_agentes(numero: int) -> list[tuple[int, int]]:
    return list(_POSICIONES_AGENTES[numero])
