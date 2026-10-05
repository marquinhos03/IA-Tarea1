# ======================================
# MODULO EDITADO CON IA
# ======================================

import heapq
import random
from typing import Callable
from .utilidades import INFINITO, heuristica


def eliminar_ciclos(camino: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Elimina ciclos en una trayectoria para garantizar que sea un camino simple.
    """
    nuevo_camino: list[tuple[int, int]] = []
    pos_a_indice: dict[tuple[int, int], int] = {}
    for nodo in camino:
        if nodo in pos_a_indice:
            idx = pos_a_indice[nodo]
            for n in nuevo_camino[idx + 1:]:
                if n in pos_a_indice and pos_a_indice[n] > idx:
                    del pos_a_indice[n]
            nuevo_camino = nuevo_camino[:idx + 1]
        else:
            pos_a_indice[nodo] = len(nuevo_camino)
            nuevo_camino.append(nodo)
    return nuevo_camino


def calcular_costo_camino(
    camino: list[tuple[int, int]],
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]]
) -> float:
    """
    Calcula el costo acumulado de una trayectoria sumando los costos de las aristas.
    Si alguna transición es inválida, retorna INFINITO.
    """
    if len(camino) <= 1:
        return 0.0

    costo_total = 0.0
    for i in range(len(camino) - 1):
        u = camino[i]
        v = camino[i + 1]
        vecinos = expandir(u)
        costo_paso = next((c for c, vec in vecinos if vec == v), None)
        if costo_paso is None:
            return INFINITO
        costo_total += costo_paso

    return costo_total


def calcular_fitness_camino(
    camino: list[tuple[int, int]],
    nodo_objetivo: tuple[int, int],
    costo: float | None = None,
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]] | None = None
) -> float:
    """
    Calcula la función de aptitud (fitness) de un camino candidato.
    - Si llega a la meta: fitness = 1000.0 / (1.0 + costo)
    - Si no llega a la meta: fitness = 10.0 / (1.0 + 5.0 * dist_manhattan + 0.1 * costo)
    Garantiza fitness > 0 para la selección por ruleta P(i) = fitness(i) / sum_j(fitness(j)).
    """
    if not camino:
        return 1e-6

    if costo is None:
        if expandir is not None:
            costo = calcular_costo_camino(camino, expandir)
        else:
            costo = float(len(camino) - 1)

    if costo == INFINITO:
        return 1e-6

    nodo_final = camino[-1]
    dist_meta = heuristica(nodo_final, nodo_objetivo)

    if nodo_final == nodo_objetivo:
        return 1000.0 / (1.0 + costo)
    else:
        return 10.0 / (1.0 + 5.0 * dist_meta + 0.1 * costo)


def seleccion_ruleta(poblacion: list, fitnesses: list[float]):
    """
    Selección de los más aptos mediante Ruleta proporcional al fitness:
    P(i) = fitness(i) / sum_j fitness(j)
    """
    total_fitness = sum(fitnesses)
    if total_fitness <= 0:
        return random.choice(poblacion)

    probabilidades = [f / total_fitness for f in fitnesses]
    return random.choices(poblacion, weights=probabilidades, k=1)[0]


def cruce_caminos(
    padre1: list[tuple[int, int]],
    padre2: list[tuple[int, int]],
    prob_cruce: float = 0.8
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """
    Fase de cruce: Combina características de dos padres seleccionando
    un punto de cruce en un nodo común que compartan ambas trayectorias.
    """
    if random.random() > prob_cruce:
        return list(padre1), list(padre2)

    set_p2 = set(padre2)
    nodos_comunes = [nodo for nodo in padre1 if nodo in set_p2]

    # Si comparten al menos un nodo además del inicial (o la meta)
    if len(nodos_comunes) > 1:
        nodo_cruce = random.choice(nodos_comunes[1:])
        idx1 = padre1.index(nodo_cruce)
        idx2 = padre2.index(nodo_cruce)

        hijo1 = eliminar_ciclos(padre1[:idx1] + padre2[idx2:])
        hijo2 = eliminar_ciclos(padre2[:idx2] + padre1[idx1:])
        return hijo1, hijo2

    return list(padre1), list(padre2)


def mutar_camino(
    camino: list[tuple[int, int]],
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]],
    nodo_objetivo: tuple[int, int],
    prob_mutacion: float = 0.3
) -> list[tuple[int, int]]:
    """
    Fase de mutación: Introduce cambios aleatorios para escapar de óptimos locales:
    1. Atajo: Conectar directamente dos nodos no contiguos si son vecinos válidos.
    2. Desvío: Explorar un vecino alternativo y reconectar con la ruta.
    3. Extensión: Avanzar pasos hacia la meta si el camino no la ha alcanzado aún.
    """
    if random.random() > prob_mutacion or len(camino) < 2:
        return camino

    nuevo_camino = list(camino)
    tipo = random.choice(["atajo", "desvio", "extension"])

    if tipo == "atajo" and len(nuevo_camino) > 3:
        for _ in range(5):
            i = random.randint(0, len(nuevo_camino) - 3)
            j = random.randint(i + 2, min(i + 6, len(nuevo_camino) - 1))
            u = nuevo_camino[i]
            v = nuevo_camino[j]
            vecinos_u = [vec for _, vec in expandir(u)]
            if v in vecinos_u:
                nuevo_camino = nuevo_camino[:i + 1] + nuevo_camino[j:]
                break

    elif tipo == "desvio" and len(nuevo_camino) > 2:
        idx = random.randint(0, len(nuevo_camino) - 2)
        nodo = nuevo_camino[idx]
        vecinos = [vec for _, vec in expandir(nodo) if vec != nuevo_camino[idx + 1]]
        if vecinos:
            desvio = random.choice(vecinos)
            vecinos_desvio = [vec for _, vec in expandir(desvio)]
            reconnect_idx = -1
            for k in range(idx + 1, len(nuevo_camino)):
                if nuevo_camino[k] in vecinos_desvio:
                    reconnect_idx = k
                    break
            if reconnect_idx != -1:
                nuevo_camino = nuevo_camino[:idx + 1] + [desvio] + nuevo_camino[reconnect_idx:]

    elif tipo == "extension" and nuevo_camino[-1] != nodo_objetivo:
        ultimo = nuevo_camino[-1]
        vecinos = [vec for _, vec in expandir(ultimo) if vec not in nuevo_camino]
        if vecinos:
            vecinos.sort(key=lambda n: heuristica(n, nodo_objetivo))
            nuevo_camino.append(vecinos[0])

    return eliminar_ciclos(nuevo_camino)


def busqueda_genetica(
    nodo_inicial: tuple[int, int],
    nodo_objetivo: tuple[int, int],
    expandir: Callable[[tuple[int, int]], list[tuple[float, tuple[int, int]]]],
    tamano_poblacion: int = 30,
    max_generaciones: int = 40,
    prob_cruce: float = 0.8,
    prob_mutacion: float = 0.3,
    elitismo: int = 2,
    semilla: int | None = None
) -> tuple[float, list[tuple[int, int]]]:
    """
    Búsqueda basada en Algoritmo Genético (Optimización Bioinspirada):
    - Trabaja con una población de estados (caminos candidatos).
    - Función de aptitud (Fitness) inversamente proporcional al costo y distancia a la meta.
    - Selección por Ruleta: P(i) = fitness(i) / sum_j fitness(j).
    - Cruce (Crossover): Combinación de sub-rutas en puntos de corte de nodos compartidos.
    - Mutación: Atajos, desvíos y extensiones para escapar de mínimos locales.
    - Elitismo: Preserva las mejores soluciones a lo largo de las generaciones.
    """
    if semilla is not None:
        random.seed(semilla)

    # Caso base 1: Inicio es igual a la meta
    if nodo_inicial == nodo_objetivo:
        return 0.0, []

    # Caso base 2: Inicio sin vecinos válidos
    vecinos_inicio = expandir(nodo_inicial)
    if not vecinos_inicio:
        return INFINITO, []

    # Cache de vecinos para optimizar llamadas repetidas a expandir
    cache_vecinos: dict[tuple[int, int], list[tuple[float, tuple[int, int]]]] = {
        nodo_inicial: vecinos_inicio
    }

    def get_vecinos_cached(u: tuple[int, int]):
        if u not in cache_vecinos:
            cache_vecinos[u] = expandir(u)
        return cache_vecinos[u]

    # Generador de caminos iniciales diversos
    def generar_camino_candidato(aleatoriedad: float) -> list[tuple[int, int]]:
        frontera: list[tuple[float, float, tuple[int, int], list[tuple[int, int]]]] = []
        heapq.heappush(frontera, (0.0, 0.0, nodo_inicial, [nodo_inicial]))
        g_scores = {nodo_inicial: 0.0}
        mejor_camino_parcial = [nodo_inicial]
        menor_dist = heuristica(nodo_inicial, nodo_objetivo)

        iteraciones = 0
        max_iter = 400

        while frontera and iteraciones < max_iter:
            iteraciones += 1
            _, g, actual, camino = heapq.heappop(frontera)

            if actual == nodo_objetivo:
                return camino

            dist_actual = heuristica(actual, nodo_objetivo)
            if dist_actual < menor_dist:
                menor_dist = dist_actual
                mejor_camino_parcial = camino

            vecinos = get_vecinos_cached(actual)
            for costo_arista, hijo in vecinos:
                if hijo in camino:
                    continue
                nuevo_g = g + costo_arista
                if hijo not in g_scores or nuevo_g < g_scores[hijo]:
                    g_scores[hijo] = nuevo_g
                    h = heuristica(hijo, nodo_objetivo)
                    ruido = random.uniform(0, aleatoriedad * (h + 1.0)) if aleatoriedad > 0 else 0.0
                    f = nuevo_g + h + ruido
                    heapq.heappush(frontera, (f, nuevo_g, hijo, camino + [hijo]))

        return mejor_camino_parcial

    # 1. Inicialización de la población
    poblacion: list[list[tuple[int, int]]] = []
    poblacion.append(generar_camino_candidato(0.0))
    for i in range(1, tamano_poblacion):
        factor = 0.5 + 2.0 * (i / tamano_poblacion)
        poblacion.append(generar_camino_candidato(factor))

    def evaluar(ind: list[tuple[int, int]]) -> tuple[float, float]:
        costo = calcular_costo_camino(ind, get_vecinos_cached)
        fit = calcular_fitness_camino(ind, nodo_objetivo, costo=costo)
        return fit, costo

    mejor_global = poblacion[0]
    mejor_fit_global, mejor_costo_global = evaluar(mejor_global)

    # 2. Ciclo Evolutivo
    for _ in range(max_generaciones):
        evaluaciones = [evaluar(ind) for ind in poblacion]
        fitnesses = [e[0] for e in evaluaciones]

        for i, (fit, costo) in enumerate(evaluaciones):
            if fit > mejor_fit_global:
                mejor_fit_global = fit
                mejor_costo_global = costo
                mejor_global = poblacion[i]

        # Elitismo: transferir los mejores individuos
        indices_ordenados = sorted(
            range(len(poblacion)),
            key=lambda idx: fitnesses[idx],
            reverse=True
        )
        nueva_poblacion = [poblacion[idx] for idx in indices_ordenados[:elitismo]]

        # Reproducción (Selección Ruleta + Cruce + Mutación)
        while len(nueva_poblacion) < tamano_poblacion:
            padre1 = seleccion_ruleta(poblacion, fitnesses)
            padre2 = seleccion_ruleta(poblacion, fitnesses)
            hijo1, hijo2 = cruce_caminos(padre1, padre2, prob_cruce=prob_cruce)
            hijo1_mut = mutar_camino(hijo1, get_vecinos_cached, nodo_objetivo, prob_mutacion=prob_mutacion)
            nueva_poblacion.append(hijo1_mut)
            if len(nueva_poblacion) < tamano_poblacion:
                hijo2_mut = mutar_camino(hijo2, get_vecinos_cached, nodo_objetivo, prob_mutacion=prob_mutacion)
                nueva_poblacion.append(hijo2_mut)

        poblacion = nueva_poblacion

    # Evaluación final
    for ind in poblacion:
        fit, costo = evaluar(ind)
        if fit > mejor_fit_global:
            mejor_fit_global = fit
            mejor_costo_global = costo
            mejor_global = ind

    costo_final = calcular_costo_camino(mejor_global, get_vecinos_cached)
    if mejor_global and mejor_global[-1] == nodo_objetivo and costo_final != INFINITO:
        return costo_final, mejor_global[1:]

    return INFINITO, []


# Alias para compatibilidad
Busqueda_Genetica = busqueda_genetica
