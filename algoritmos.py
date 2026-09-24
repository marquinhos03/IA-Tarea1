import heapq
from collections import deque
from typing import Callable

# Constantes de estado
ENCONTRADO = "ENCONTRADO"
NO_ENCONTRADO = "NO_ENCONTRADO"
INFINITO = float('inf')

class Algoritmo:

    @staticmethod
    def reconstruir_camino(
        nodo_meta: tuple[int, int],
        padres: dict[tuple[int, int], tuple[int, int]]
    ) -> list[tuple[int, int]]:
        camino: list[tuple[int, int]] = []
        nodo_paso = nodo_meta

        while padres[nodo_paso] is not None:
            camino.append(nodo_paso)
            nodo_paso = padres[nodo_paso]

        camino.reverse()

        return camino

    @staticmethod
    def heuristica(nodo1: tuple[int, int], nodo2: tuple[int, int]) -> float:
        """
        Distancia Manhattan entre dos nodos
        """
        x1, y1 = nodo1
        x2, y2 = nodo2
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
    def busqueda_recursiva_ida(
        nodo_actual: tuple[int, int],
        nodo_objetivo: tuple[int, int],
        g: float,
        umbral: float,
        expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]],
        camino: list[tuple[int, int]],
    ) -> tuple[str, float]:
        """
        Búsqueda recursiva en profundidad acotada por el umbral de f(n).
        """
        f = g + Algoritmo.heuristica(nodo_actual, nodo_objetivo)

        # Si se supera la cota de f, se poda la rama y se devuelve el valor para el próximo ciclo
        if f > umbral:
            return (NO_ENCONTRADO, f)

        # Test de objetivo al expandir el nodo
        if nodo_actual == nodo_objetivo:
            return (ENCONTRADO, f)

        minimo = INFINITO

        for costo_arista, hijo in expandir(nodo_actual):
            # Evitar ciclos en la rama de exploración actual
            if hijo in camino:
                continue

            camino.append(hijo)

            resultado, f_estimado = Algoritmo.busqueda_recursiva_ida(
                hijo,
                nodo_objetivo,
                g + costo_arista,
                umbral,
                expandir,
                camino
            )

            if resultado == ENCONTRADO:
                return (ENCONTRADO, f_estimado)
            if f_estimado < minimo:
                minimo = f_estimado

            # Regresión (Backtracking): liberar nodo al retroceder en la rama
            camino.pop()

        return (NO_ENCONTRADO, minimo)


    
    @staticmethod
    def Busqueda_En_Amplitud(
        nodo_inicial: tuple[int, int],
        nodo_objetivo: tuple[int, int],
        expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
    ) -> tuple[float, list[tuple[int, int]]]:

        if nodo_inicial == nodo_objetivo:
            return 0.0, []

        frontera = deque([nodo_inicial])
        visitados : set[tuple[int, int]] = set([nodo_inicial])
        padres: dict[tuple[int, int], tuple[int, int]] = {nodo_inicial: None}

        while frontera:
            nodo_actual = frontera.popleft()

            for _, hijo in expandir(nodo_actual):
                if hijo not in visitados:
                    visitados.add(hijo)
                    padres[hijo] = nodo_actual

                    # Test de objetivo al generar
                    if hijo == nodo_objetivo:
                        camino = Algoritmo.reconstruir_camino(hijo, padres)

                        return float(len(camino)), camino

                    frontera.append(hijo)

        return INFINITO, []



    @staticmethod
    def Busqueda_Costo_Uniforme(
        nodo_inicial: tuple[int, int],
        nodo_objetivo: tuple[int, int],
        expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
    ) -> tuple[float, list[tuple[int, int]]]:
        
        frontera: list[tuple[float, tuple[int, int]]] = []
        heapq.heappush(frontera, (0, nodo_inicial))

        costos_minimos: dict[tuple[int, int], float] = {nodo_inicial: 0}
        padres: dict[tuple[int, int], tuple[int, int]] = {nodo_inicial: None}

        while frontera:
            costo_g, nodo_actual = heapq.heappop(frontera)

            if costo_g > costos_minimos[nodo_actual]:
                continue

            # Test de objetivo al expandir
            if nodo_actual == nodo_objetivo:
                camino = Algoritmo.reconstruir_camino(nodo_actual, padres)
                costo_total = costos_minimos[nodo_actual]

                return costo_total, camino

            for (costo_arista, hijo) in expandir(nodo_actual):
                nuevo_costo = costo_g + costo_arista

                if hijo not in costos_minimos or nuevo_costo < costos_minimos[hijo]:
                    costos_minimos[hijo] = nuevo_costo
                    padres[hijo] = nodo_actual
                    heapq.heappush(frontera, (nuevo_costo, hijo))

        return INFINITO, []


        
    @staticmethod
    def Busqueda_A_Estrella(
        nodo_inicial: tuple[int, int],
        nodo_objetivo: tuple[int, int],
        expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
    ) -> tuple[float, list[tuple[int, int]]]:
        
        # La cola de prioridad ordena de menor a mayor según f(n) = g(n) + h(n)
        frontera: list[tuple[float, tuple[int, int]]] = []

        g_score: dict[tuple[int, int], float] = {nodo_inicial: 0}

        padres: dict[tuple[int, int], tuple[int, int]] = {nodo_inicial: None}

        # Prioridad inicial
        f_inicial = 0 + Algoritmo.heuristica(nodo_inicial, nodo_objetivo)
        heapq.heappush(frontera, (f_inicial, nodo_inicial))

        while frontera:
            f_actual, nodo_actual = heapq.heappop(frontera)

            # Si f_actual es mayor que el mejor f conocido para este nodo, es una entrada obsoleta
            if f_actual > g_score[nodo_actual] + Algoritmo.heuristica(nodo_actual, nodo_objetivo):
                continue

            # Test de objetivo al expandir
            if nodo_actual == nodo_objetivo:
                camino = Algoritmo.reconstruir_camino(nodo_actual, padres)
                costo_total = g_score[nodo_actual]

                return costo_total, camino

            for costo_arista, hijo in expandir(nodo_actual):
                nuevo_g = g_score[nodo_actual] + costo_arista

                # Si encontramos un camino mejor/más barato hacia el hijo
                if (hijo not in g_score) or (nuevo_g < g_score[hijo]):
                    g_score[hijo] = nuevo_g
                    padres[hijo] = nodo_actual
                    f_hijo = nuevo_g + Algoritmo.heuristica(hijo, nodo_objetivo)     # f(n) = g(n) + h(n)

                    heapq.heappush(frontera, (f_hijo, hijo))

        return INFINITO, []



    @staticmethod
    def Busqueda_IDA_Estrella(
        nodo_inicial: tuple[int, int],
        nodo_objetivo: tuple[int, int],
        expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
    ) -> tuple[float, list[tuple[int, int]]]:

        # Inicialización del umbral con la heurística del nodo raíz
        umbral = Algoritmo.heuristica(nodo_inicial, nodo_objetivo)
        camino: list[tuple[int, int]] = [nodo_inicial]

        while umbral != INFINITO:
            resultado, nuevo_umbral = Algoritmo.busqueda_recursiva_ida(
                nodo_inicial, 
                nodo_objetivo,
                0.0, 
                umbral,
                expandir,
                camino
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



    @staticmethod
    def busqueda(nombre: str):
        """
        Devuelve la función de búsqueda elegida
        """
        estrategia_busqueda = {
            "BFS": Algoritmo.Busqueda_En_Amplitud,
            "Costo Uniforme": Algoritmo.Busqueda_Costo_Uniforme,
            "A*": Algoritmo.Busqueda_A_Estrella,
            "IDA*": Algoritmo.Busqueda_IDA_Estrella
        }

        if nombre not in estrategia_busqueda:
            raise ValueError(f"Algoritmo {nombre} no válido. Opciones: {list(estrategia_busqueda.keys())}")

        return estrategia_busqueda[nombre]