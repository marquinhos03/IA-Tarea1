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
    
    # Creamos una función expandir vacía, ya que ni siquiera debería necesitar expandir
    expandir_mock = lambda nodo: []
    
    algoritmo_ida = get_algorithm("ida_estrella")
    costo, camino = algoritmo_ida((2, 2), (2, 2), expandir_mock)
    
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
    
    algoritmo_ida = get_algorithm("ida_estrella")
    costo, camino = algoritmo_ida((0, 0), (5, 5), expandir_vacio)
    
    assert costo == float('inf'), f"Error: El costo debió ser infinito, pero dio {costo}"
    assert camino == [], f"Error: El camino debió ser [], pero dio {camino}"
    print(" -> PASÓ con éxito.")



def test_caso_lineal():
    """
    Prueba 3: Un camino recto conocido (0,0) -> (1,0) -> (2,0) -> (3,0).
    """

    print("Ejecutando Test 3: Camino Lineal Simple...")
    
    # Esta función simula que solo te puedes mover hacia la derecha (x + 1) con costo 1.0
    def expandir_linea(nodo):
        x, y = nodo
        if x < 3:
            return [(1.0, (x + 1, y))]
        return []

    algoritmo_ida = get_algorithm("ida_estrella")
    costo, camino = algoritmo_ida((0, 0), (3, 0), expandir_linea)
    
    assert costo == 3.0, f"Error: Costo esperado 3.0, obtenido {costo}"
    assert camino == [(1, 0), (2, 0), (3, 0)], f"Error en el camino reconstruido: {camino}"
    print(" -> PASÓ con éxito.")



def test_comparacion_cruzada_con_a_estrella():
    """
    Prueba 4: Probar IDA* en un mapa real y comparar que dé el mismo costo que A*.
    """
    
    print("Ejecutando Test 4: Comparación IDA* vs A* en mapa 12x12...")
    
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

    algoritmo_ida = get_algorithm("ida_estrella")
    algoritmo_a_estrella = get_algorithm("a_estrella")

    costo_astar, camino_astar = algoritmo_a_estrella(inicio, meta, expandir)
    costo_ida, camino_ida = algoritmo_ida(inicio, meta, expandir)
    print(f"   A*   -> Costo: {costo_astar}, Pasos: {len(camino_astar)}")
    print(f"   IDA* -> Costo: {costo_ida}, Pasos: {len(camino_ida)}")
    assert costo_ida == costo_astar, f"IDA* dio costo {costo_ida} diferente a A* {costo_astar}"
    assert len(camino_ida) == len(camino_astar), "Las longitudes de camino no coinciden"
    print(" -> PASÓ con éxito (Costo óptimo verificado).")



if __name__ == "__main__":
    print("=== INICIANDO PRUEBAS UNITARIAS ===")
    test_caso_base()
    test_caso_inalcanzable()
    test_caso_lineal()
    test_comparacion_cruzada_con_a_estrella()
    print("=== TODAS LAS PRUEBAS PASARON EXITOSAMENTE ===")
