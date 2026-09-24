from simulacion import Simulacion
from mapa import Mapa
from utilidades import Utilidades



# Definición manual del mapa 12x12 mediante una matriz 2D:
# 0 = VACIA, 1 = MURO, 2 = FUEGO, 3 = SALIDA
mapa_12x12 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Fila 0
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 1],  # Fila 1
    [1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1],  # Fila 2
    [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],  # Fila 3
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1],  # Fila 4
    [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],  # Fila 5
    [1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],  # Fila 6
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1],  # Fila 7
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],  # Fila 8
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],  # Fila 9
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 1],  # Fila 10
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]   # Fila 11
]

mapa = Mapa.desde_matriz(mapa_12x12)

print("Mapa 12x12 cargado desde matriz:")
print()

coords_agentes = [(1, 1), (1, 6), (6, 1), (1, 4), (6, 4)]
sim = Simulacion(mapa, coords_agentes, 2, 19, "BFS")

Utilidades.mostrar_simulacion(sim.mapa, sim.agentes, sim.turno_actual)
print()

print("=== SIMULACIÓN INICIADA ===")
print()

while not sim.esta_finalizada():
    sim.ejecutar_turno()
    Utilidades.mostrar_simulacion(sim.mapa, sim.agentes, sim.turno_actual)
    print()

print("=== SIMULACIÓN TERMINADA ===")
