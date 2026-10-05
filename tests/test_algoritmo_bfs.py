# ======================================
# EDITADO CON IA
# ======================================

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algoritmos import get_algorithm
from mapa import Mapa

def test_caso_base():
    """
    Prueba 1: Si ya estamos en la meta, el costo debe ser 0 y el camino vacío.
    """
    print("Ejecutando Test 1: Inicio == Meta...")
    
    # Función expandir vacía (no debería necesitar expandir ningún nodo)
    expandir_mock = lambda nodo: []
    
    algoritmo_bfs = get_algorithm("bfs")
    costo, camino = algoritmo_bfs(nodo_inicial=(2, 2), nodo_objetivo=(2, 2), expandir=expandir_mock)
    
    assert costo == 0.0, f"Error: El costo esperado era 0.0, pero dio {costo}"
    assert camino == [], f"Error: El camino esperado era [], pero dio {camino}"
    print(" -> PASÓ con éxito.")



def test_caso_inalcanzable():
    """
    Prueba 2: Si la meta no tiene conexión, debe retornar infinito sin quedarse pegado.
    """
    print("Ejecutando Test 2: Objetivo Inalcanzable...")
    
    # Simula que desde (0, 0) no hay vecinos posibles hacia (5, 5)
    expandir_vacio = lambda nodo: []
    
    algoritmo_bfs = get_algorithm("bfs")
    costo, camino = algoritmo_bfs((0, 0), (5, 5), expandir_vacio)
    
    assert costo == float('inf'), f"Error: El costo debió ser infinito, pero dio {costo}"
    assert camino == [], f"Error: El camino debió ser [], pero dio {camino}"
    print(" -> PASÓ con éxito.")



def test_caso_lineal():
    """
    Prueba 3: Un camino recto conocido (0,0) -> (1,0) -> (2,0) -> (3,0).
    """
    print("Ejecutando Test 3: Camino Lineal Simple...")
    
    # Esta función simula que solo te puedes mover hacia la derecha (x + 1)
    def expandir_linea(nodo):
        x, y = nodo
        if x < 3:
            return [(1.0, (x + 1, y))]
        return []

    algoritmo_bfs = get_algorithm("bfs")
    costo, camino = algoritmo_bfs((0, 0), (3, 0), expandir_linea)
    
    assert costo == 3.0, f"Error: Costo esperado 3.0 (3 pasos), obtenido {costo}"
    assert camino == [(1, 0), (2, 0), (3, 0)], f"Error en el camino reconstruido: {camino}"
    print(" -> PASÓ con éxito.")



def test_comparacion_cruzada_con_a_estrella():
    """
    Prueba 4: Probar BFS en un mapa real y comparar que la cantidad de pasos
    sea idéntica a la ruta óptima encontrada por A*.
    """
    print("Ejecutando Test 4: Comparación BFS vs A* en mapa 12x12...")
    
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

    algoritmo_bfs = get_algorithm("bfs")
    algoritmo_a_estrella = get_algorithm("a_estrella")

    costo_bfs, camino_bfs = algoritmo_bfs(inicio, meta, expandir)
    costo_astar, camino_astar = algoritmo_a_estrella(inicio, meta, expandir)

    print(f"   A*  -> Costo: {costo_astar}, Pasos: {len(camino_astar)}")
    print(f"   BFS -> Pasos (costo): {costo_bfs}, Longitud camino: {len(camino_bfs)}")

    # En un mapa con costo base 1.0 por celda sin agentes, los pasos de BFS deben igualar los de A*
    assert len(camino_bfs) == len(camino_astar), (
        f"BFS encontró {len(camino_bfs)} pasos, pero A* encontró {len(camino_astar)}"
    )
    assert costo_bfs == float(len(camino_astar)), (
        f"El costo de BFS ({costo_bfs}) debería ser igual al número de pasos ({len(camino_astar)})"
    )
    print(" -> PASÓ con éxito (Longitud de pasos mínima verificada).")



if __name__ == "__main__":
    print("=== INICIANDO PRUEBAS UNITARIAS (BFS) ===")
    test_caso_base()
    test_caso_inalcanzable()
    test_caso_lineal()
    test_comparacion_cruzada_con_a_estrella()
    print("=== TODAS LAS PRUEBAS PASARON EXITOSAMENTE ===")
