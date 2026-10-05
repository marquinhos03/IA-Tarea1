import heapq
from typing import Callable
from .utilidades import INFINITO, heuristica, reconstruir_camino


def busqueda_a_estrella(
    nodo_inicial: tuple[int, int],
    nodo_objetivo: tuple[int, int],
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
) -> tuple[float, list[tuple[int, int]]]:
    """
    Búsqueda A* (A-Estrella).
    Utiliza una cola de prioridad ordenada por f(n) = g(n) + h(n),
    donde g(n) es el costo real acumulado y h(n) es la heurística Manhattan a la meta.
    """
    # La cola de prioridad ordena de menor a mayor según f(n) = g(n) + h(n)
    frontera: list[tuple[float, tuple[int, int]]] = []

    g_score: dict[tuple[int, int], float] = {nodo_inicial: 0.0}
    padres: dict[tuple[int, int], tuple[int, int]] = {nodo_inicial: None}

    # Prioridad inicial
    f_inicial = 0.0 + heuristica(nodo_inicial, nodo_objetivo)
    heapq.heappush(frontera, (f_inicial, nodo_inicial))

    while frontera:
        f_actual, nodo_actual = heapq.heappop(frontera)

        # Si f_actual es mayor que el mejor f conocido para este nodo, es una entrada obsoleta
        if f_actual > g_score[nodo_actual] + heuristica(nodo_actual, nodo_objetivo):
            continue

        # Test de objetivo al expandir
        if nodo_actual == nodo_objetivo:
            camino = reconstruir_camino(nodo_actual, padres)
            costo_total = g_score[nodo_actual]
            return costo_total, camino

        for costo_arista, hijo in expandir(nodo_actual):
            nuevo_g = g_score[nodo_actual] + costo_arista

            # Si encontramos un camino mejor/más barato hacia el hijo
            if (hijo not in g_score) or (nuevo_g < g_score[hijo]):
                g_score[hijo] = nuevo_g
                padres[hijo] = nodo_actual
                f_hijo = nuevo_g + heuristica(hijo, nodo_objetivo)     # f(n) = g(n) + h(n)
                heapq.heappush(frontera, (f_hijo, hijo))

    return INFINITO, []
