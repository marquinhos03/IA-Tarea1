from collections import deque
from typing import Callable
from .utilidades import INFINITO, reconstruir_camino


def busqueda_en_amplitud(
    nodo_inicial: tuple[int, int],
    nodo_objetivo: tuple[int, int],
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
) -> tuple[float, list[tuple[int, int]]]:
    """
    Búsqueda en Amplitud (Breadth-First Search - BFS).
    Explora nivel por nivel garantizando encontrar el camino con menor cantidad de pasos.
    """
    if nodo_inicial == nodo_objetivo:
        return 0.0, []

    frontera = deque([nodo_inicial])
    visitados: set[tuple[int, int]] = set([nodo_inicial])
    padres: dict[tuple[int, int], tuple[int, int]] = {nodo_inicial: None}

    while frontera:
        nodo_actual = frontera.popleft()

        for _, hijo in expandir(nodo_actual):
            if hijo not in visitados:
                visitados.add(hijo)
                padres[hijo] = nodo_actual

                # Test de objetivo al generar
                if hijo == nodo_objetivo:
                    camino = reconstruir_camino(hijo, padres)
                    return float(len(camino)), camino

                frontera.append(hijo)

    return INFINITO, []
