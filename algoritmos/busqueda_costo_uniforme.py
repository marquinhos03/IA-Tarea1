import heapq
from typing import Callable
from .utilidades import INFINITO, reconstruir_camino


def busqueda_costo_uniforme(
    nodo_inicial: tuple[int, int],
    nodo_objetivo: tuple[int, int],
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
) -> tuple[float, list[tuple[int, int]]]:
    """
    Búsqueda de Costo Uniforme (Uniform Cost Search - UCS / Dijkstra).
    Explora el espacio de estados priorizando siempre el nodo con menor costo acumulado g(n).
    """
    frontera: list[tuple[float, tuple[int, int]]] = []
    heapq.heappush(frontera, (0.0, nodo_inicial))

    costos_minimos: dict[tuple[int, int], float] = {nodo_inicial: 0.0}
    padres: dict[tuple[int, int], tuple[int, int]] = {nodo_inicial: None}

    while frontera:
        costo_g, nodo_actual = heapq.heappop(frontera)

        if costo_g > costos_minimos[nodo_actual]:
            continue

        # Test de objetivo al expandir
        if nodo_actual == nodo_objetivo:
            camino = reconstruir_camino(nodo_actual, padres)
            costo_total = costos_minimos[nodo_actual]
            return costo_total, camino

        for costo_arista, hijo in expandir(nodo_actual):
            nuevo_costo = costo_g + costo_arista

            if hijo not in costos_minimos or nuevo_costo < costos_minimos[hijo]:
                costos_minimos[hijo] = nuevo_costo
                padres[hijo] = nodo_actual
                heapq.heappush(frontera, (nuevo_costo, hijo))

    return INFINITO, []
