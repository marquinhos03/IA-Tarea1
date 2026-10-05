# ======================================
# GENERADO CON IA
# ======================================

import sys
import os
import random
from collections import Counter

# Asegurar que se encuentre el módulo raíz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algoritmos import get_algorithm
from algoritmos.utilidades import INFINITO
from algoritmos.busqueda_genetica import (
    seleccion_ruleta,
    eliminar_ciclos,
    cruce_caminos,
    mutar_camino,
    calcular_costo_camino,
)
from mapa import Mapa
from agente import Agente


def test_caso_base():
    """
    Prueba 1: Si ya estamos en la meta, el costo debe ser 0 y el camino vacío.
    """
    print("Ejecutando Test 1: Inicio == Meta...")

    expandir_mock = lambda nodo: []
    algoritmo_genetico = get_algorithm("genetico")
    costo, camino = algoritmo_genetico((2, 2), (2, 2), expandir_mock)

    assert costo == 0.0, f"Error: El costo esperado era 0.0, pero dio {costo}"
    assert camino == [], f"Error: El camino esperado era [], pero dio {camino}"
    print(" -> PASÓ con éxito.")



def test_caso_inalcanzable():
    """
    Prueba 2: Si la meta no tiene conexión, debe retornar infinito sin quedarse pegado.
    """
    print("Ejecutando Test 2: Objetivo Inalcanzable...")

    expandir_vacio = lambda nodo: []
    algoritmo_genetico = get_algorithm("genetico")
    costo, camino = algoritmo_genetico((0, 0), (5, 5), expandir_vacio)

    assert costo == float('inf'), f"Error: El costo debió ser infinito, pero dio {costo}"
    assert camino == [], f"Error: El camino debió ser [], pero dio {camino}"
    print(" -> PASÓ con éxito.")



def test_caso_lineal():
    """
    Prueba 3: Un camino recto conocido (0,0) -> (1,0) -> (2,0) -> (3,0).
    """
    print("Ejecutando Test 3: Camino Lineal Simple...")

    def expandir_linea(nodo):
        x, y = nodo
        if x < 3:
            return [(1.0, (x + 1, y))]
        return []

    algoritmo_genetico = get_algorithm("genetico")
    costo, camino = algoritmo_genetico((0, 0), (3, 0), expandir_linea, semilla=42)

    assert costo == 3.0, f"Error: Costo esperado 3.0, obtenido {costo}"
    assert camino == [(1, 0), (2, 0), (3, 0)], f"Error en el camino reconstruido: {camino}"
    print(" -> PASÓ con éxito.")



def test_formula_seleccion_ruleta():
    """
    Prueba 4: Verificar la fórmula de Selección por Ruleta proporcional al fitness:
    P(i) = fitness(i) / sum_j fitness(j)
    """
    print("Ejecutando Test 4: Fórmula de Selección por Ruleta P(i) = fitness(i) / sum(fitness)...")

    random.seed(123)
    poblacion = ["A", "B", "C"]
    fitnesses = [10.0, 20.0, 70.0]  # Proporciones teóricas: 10%, 20%, 70%
    total_fit = sum(fitnesses)
    prob_esperadas = {p: f / total_fit for p, f in zip(poblacion, fitnesses)}

    # Muestreo empírico de 10,000 selecciones
    num_muestras = 10000
    conteos = Counter(seleccion_ruleta(poblacion, fitnesses) for _ in range(num_muestras))

    for ind, prob_esperada in prob_esperadas.items():
        prob_empirica = conteos[ind] / num_muestras
        diferencia = abs(prob_empirica - prob_esperada)
        print(f"   Individuo '{ind}': Esperada={prob_esperada:.2f}, Empírica={prob_empirica:.2f} (dif={diferencia:.3f})")
        # Tolerancia estadística del 2.5%
        assert diferencia < 0.025, f"La selección por ruleta de '{ind}' se desvió demasiado ({diferencia:.3f})"

    print(" -> PASÓ con éxito (Distribución proporcional al fitness verificada).")



def test_eliminacion_ciclos():
    """
    Prueba 5: Eliminación de ciclos en caminos para asegurar caminos simples.
    """
    print("Ejecutando Test 5: Operador de Eliminación de Ciclos...")

    # Camino con un bucle: (0,0) -> (0,1) -> (0,2) -> (0,1) -> (1,1)
    camino_con_ciclo = [(0, 0), (0, 1), (0, 2), (0, 1), (1, 1)]
    camino_sin_ciclo = eliminar_ciclos(camino_con_ciclo)

    esperado = [(0, 0), (0, 1), (1, 1)]
    assert camino_sin_ciclo == esperado, f"Ciclo no eliminado correctamente: {camino_sin_ciclo} != {esperado}"
    print(" -> PASÓ con éxito.")



def test_cruce_caminos():
    """
    Prueba 6: Operador de Cruce (Crossover) combinando trayectorias en nodos compartidos.
    """
    print("Ejecutando Test 6: Operador de Cruce en nodos comunes...")

    random.seed(42)
    # Ambos caminos inician en (0,0), se cruzan en (2,2) y terminan en diferentes ramas
    padre1 = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2)]
    padre2 = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4)]

    hijo1, hijo2 = cruce_caminos(padre1, padre2, prob_cruce=1.0)

    # Validar que los hijos mantengan el inicio
    assert hijo1[0] == (0, 0) and hijo2[0] == (0, 0), "Los hijos deben iniciar en el nodo raíz"
    # Validar que no tengan ciclos
    assert len(hijo1) == len(set(hijo1)), "Hijo 1 contiene ciclos"
    assert len(hijo2) == len(set(hijo2)), "Hijo 2 contiene ciclos"
    print(f"   Padre 1: {padre1}")
    print(f"   Padre 2: {padre2}")
    print(f"   Hijo 1 : {hijo1}")
    print(f"   Hijo 2 : {hijo2}")
    print(" -> PASÓ con éxito.")



def test_mutacion_camino():
    """
    Prueba 7: Operador de Mutación (Atajos, desvíos y extensiones).
    """
    print("Ejecutando Test 7: Operador de Mutación...")

    random.seed(10)
    # Camino con un desvío innecesario en una grilla donde (0,0) conecta con (1,0)
    camino_largo = [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0)]

    # Mock expandir con grilla 3x3 ortogonal
    def expandir_mock(nodo):
        x, y = nodo
        vecinos = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx <= 3 and 0 <= ny <= 3:
                vecinos.append((1.0, (nx, ny)))
        return vecinos

    mutado = mutar_camino(camino_largo, expandir_mock, nodo_objetivo=(2, 0), prob_mutacion=1.0)
    assert mutado[0] == (0, 0), "La mutación no debe alterar el nodo inicial"
    # Verificar conectividad de cada paso
    for i in range(len(mutado) - 1):
        u, v = mutado[i], mutado[i + 1]
        vecinos_u = [vec for _, vec in expandir_mock(u)]
        assert v in vecinos_u, f"Paso desconectado tras mutación: {u} -> {v}"

    print(f"   Original: {camino_largo} (longitud {len(camino_largo)})")
    print(f"   Mutado  : {mutado} (longitud {len(mutado)})")
    print(" -> PASÓ con éxito.")



def test_comparacion_cruzada_con_a_estrella():
    """
    Prueba 8: Probar Algoritmo Genético en el mapa 12x12 y comparar con A*.
    Verifica que encuentre una ruta válida hasta la salida y evalúa costo y pasos.
    """
    print("Ejecutando Test 8: Comparación Algoritmo Genético vs A* en mapa 12x12...")

    mapa_matriz = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 1],
        [1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    mapa = Mapa.desde_matriz(mapa_matriz)

    def expandir(nodo):
        return [(mapa.funcion_costo_celda(p, {}), p) for p in mapa.get_celdas_ortogonales(nodo)]

    inicio = (1, 1)
    meta = mapa.pos_salida

    algoritmo_a_estrella = get_algorithm("a_estrella")
    algoritmo_genetico = get_algorithm("genetico")

    costo_astar, camino_astar = algoritmo_a_estrella(inicio, meta, expandir)
    costo_gen, camino_gen = algoritmo_genetico(inicio, meta, expandir, semilla=42)

    print(f"   A*       -> Costo: {costo_astar}, Pasos: {len(camino_astar)}")
    print(f"   Genético -> Costo: {costo_gen}, Pasos: {len(camino_gen)}")

    assert costo_gen != INFINITO, "El Algoritmo Genético no encontró un camino a la salida"
    assert len(camino_gen) > 0, "El camino devuelto por el Algoritmo Genético está vacío"
    assert camino_gen[-1] == meta, f"El camino no termina en la meta: {camino_gen[-1]} != {meta}"

    # Validar que cada paso en el camino genético sea vecino válido según expandir
    pos_actual = inicio
    for paso in camino_gen:
        vecinos_validos = [vec for _, vec in expandir(pos_actual)]
        assert paso in vecinos_validos, f"Paso inválido detectado en la ruta: de {pos_actual} a {paso}"
        pos_actual = paso

    # El costo de la ruta debe coincidir con el costo acumulado calculado
    costo_verificado = calcular_costo_camino([inicio] + camino_gen, expandir)
    assert abs(costo_gen - costo_verificado) < 1e-5, f"Discrepancia en costo: {costo_gen} vs {costo_verificado}"

    # Verificamos que sea óptimo o muy cercano (≤ óptimo + 2 pasos en este laberinto)
    assert len(camino_gen) <= len(camino_astar) + 2, (
        f"El camino genético ({len(camino_gen)}) es significativamente más largo que A* ({len(camino_astar)})"
    )
    print(" -> PASÓ con éxito (Validez de pasos y proximidad a costo óptimo verificadas).")



def test_integracion_con_agente():
    """
    Prueba 9: Integración de 'genetico' con la clase Agente y despacho desde get_algorithm.
    """
    print("Ejecutando Test 9: Integración con la clase Agente...")

    mapa_matriz = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 3, 1],
        [1, 1, 1, 1, 1]
    ]
    mapa = Mapa.desde_matriz(mapa_matriz)
    agente = Agente(id_agente=0, pos_inicial=(1, 1), nombre_algoritmo="genetico")

    assert agente.algoritmo == "genetico"
    assert agente.algoritmo_seleccionado == get_algorithm("genetico")

    agente.planificar_ruta(mapa, {})
    assert len(agente.ruta_planeada) == 2
    assert agente.ruta_planeada[-1] == mapa.pos_salida

    siguiente_mov = agente.decidir_siguiente_movimiento(mapa, {})
    assert siguiente_mov == (1, 2)
    print(" -> PASÓ con éxito.")



if __name__ == "__main__":
    print("=== INICIANDO PRUEBAS UNITARIAS (ALGORITMO GENÉTICO) ===")
    test_caso_base()
    test_caso_inalcanzable()
    test_caso_lineal()
    test_formula_seleccion_ruleta()
    test_eliminacion_ciclos()
    test_cruce_caminos()
    test_mutacion_camino()
    test_comparacion_cruzada_con_a_estrella()
    test_integracion_con_agente()
    print("=== TODAS LAS PRUEBAS PASARON EXITOSAMENTE ===")
