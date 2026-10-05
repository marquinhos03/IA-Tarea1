# Constantes de estado
ENCONTRADO = "ENCONTRADO"
NO_ENCONTRADO = "NO_ENCONTRADO"
INFINITO = float('inf')


def heuristica(nodo1: tuple[int, int], nodo2: tuple[int, int]) -> float:
    """
    Distancia Manhattan entre dos nodos.
    """
    x1, y1 = nodo1
    x2, y2 = nodo2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruir_camino(
    nodo_meta: tuple[int, int],
    padres: dict[tuple[int, int], tuple[int, int]]
) -> list[tuple[int, int]]:
    """
    Reconstruye el camino desde el nodo meta hasta el nodo inicial utilizando el diccionario de padres.
    """
    camino: list[tuple[int, int]] = []
    nodo_paso = nodo_meta

    while padres[nodo_paso] is not None:
        camino.append(nodo_paso)
        nodo_paso = padres[nodo_paso]

    camino.reverse()

    return camino
