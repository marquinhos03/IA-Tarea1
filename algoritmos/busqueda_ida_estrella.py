# ======================================
# MÓDULO EDITADO CON IA
# ======================================

from typing import Callable
from .utilidades import ENCONTRADO, NO_ENCONTRADO, INFINITO, heuristica


def _busqueda_recursiva_ida(
    nodo_actual: tuple[int, int],
    nodo_objetivo: tuple[int, int],
    g: float,
    umbral: float,
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]],
    camino: list[tuple[int, int]],
    visitados_g: dict[tuple[int, int], float],
) -> tuple[str, float]:
    """
    Búsqueda recursiva en profundidad acotada por el umbral de f(n).
    Función auxiliar de Busqueda_IDA_Estrella.
    """
    f = g + heuristica(nodo_actual, nodo_objetivo)

    # Si se supera la cota de f, se poda la rama y se devuelve el valor para el próximo ciclo
    if f > umbral:
        return (NO_ENCONTRADO, f)

    # Test de objetivo al expandir el nodo
    if nodo_actual == nodo_objetivo:
        return (ENCONTRADO, f)

    # Si ya se alcanzó este nodo con un costo menor o igual en esta iteración, se poda la rama
    if nodo_actual in visitados_g and visitados_g[nodo_actual] <= g:
        return (NO_ENCONTRADO, INFINITO)
    visitados_g[nodo_actual] = g

    minimo = INFINITO
    vecinos = expandir(nodo_actual)
    # Ordenamiento de movimientos: explorar primero los caminos con menor f(n) estimado
    vecinos.sort(key=lambda item: g + item[0] + heuristica(item[1], nodo_objetivo))

    for costo_arista, hijo in vecinos:
        # Evitar ciclos en la rama de exploración actual
        if hijo not in camino:
            camino.append(hijo)

            resultado, f_estimado = _busqueda_recursiva_ida(
                nodo_actual=hijo,
                nodo_objetivo=nodo_objetivo,
                g=g + costo_arista,
                umbral=umbral,
                expandir=expandir,
                camino=camino,
                visitados_g=visitados_g,
            )

            if resultado == ENCONTRADO:
                return (ENCONTRADO, f_estimado)
            if f_estimado < minimo:
                minimo = f_estimado

            # Regresión (Backtracking): liberar nodo al retroceder en la rama
            camino.pop()

    return (NO_ENCONTRADO, minimo)


def busqueda_ida_estrella(
    nodo_inicial: tuple[int, int],
    nodo_objetivo: tuple[int, int],
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
) -> tuple[float, list[tuple[int, int]]]:
    """
    Búsqueda IDA* (Iterative Deepening A*).
    Combina búsqueda en profundidad con la heurística de A* usando umbrales crecientes de f(n).
    """
    # Inicialización del umbral con la heurística del nodo raíz
    umbral = heuristica(nodo_inicial, nodo_objetivo)
    camino: list[tuple[int, int]] = [nodo_inicial]

    while umbral != INFINITO:
        visitados_g: dict[tuple[int, int], float] = {}
        resultado, nuevo_umbral = _busqueda_recursiva_ida(
            nodo_actual=nodo_inicial, 
            nodo_objetivo=nodo_objetivo,
            g=0.0, 
            umbral=umbral,
            expandir=expandir,
            camino=camino,
            visitados_g=visitados_g,
        )

        if resultado == ENCONTRADO:
            camino_encontrado = camino[1:]
            costo_total = nuevo_umbral
            return costo_total, camino_encontrado

        if nuevo_umbral == INFINITO:
            return INFINITO, []

        # Se actualiza el umbral con el menor valor f(n) que superó el límite anterior
        umbral = nuevo_umbral

    return INFINITO, []
