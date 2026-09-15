import numpy as np
from enum import IntEnum

class TipoCelda(IntEnum):
    LIBRE = 0
    MURO = 1
    SALIDA = 2
    FUEGO = 3

class Mapa:
    def __init__(self, tipo_mapa, k_turnos):
        self.grid = np.array(tipo_mapa)
        self.filas, self.columnas = self.grid.shape

        self.k_turnos = k_turnos
        self.turno_actual = 0

        # Diccionario para ubicar a los agentes: {(x, y): cantidad}
        self.posicion_agentes = {}

    def propagar_fuego(self):
        self.turno_actual += 1
        
        # Propagar cada k turnos: (turno actual) mod (k turnos) = 0
        if self.turno_actual % self.k_turnos == 0:
            coords_fuego = np.argwhere(self.grid == TipoCelda.FUEGO)

            movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for fx, fy in coords_fuego:
                for mx, my in movimientos:
                    nuevo_x, nuevo_y = fx + mx, fy + my

                    if (0 <= nuevo_x and nuevo_x < self.filas) and (0 <= nuevo_y and nuevo_y < self.columnas):
                        if self.grid[nuevo_x, nuevo_y] == TipoCelda.LIBRE:
                            self.grid[nuevo_x, nuevo_y] = TipoCelda.FUEGO

    def mostrar_mapa(self):
        """Imprime el mapa por consola con caracteres legibles."""
        # Diccionario de traducción visual
        simbolos = {
            TipoCelda.LIBRE: ".",
            TipoCelda.MURO: "█",
            TipoCelda.SALIDA: "E",
            TipoCelda.FUEGO: "F"
        }

        print(f"=== Turno: {self.turno_actual} ===")
        for x in range(self.filas):
            fila_visual = []
            for y in range(self.columnas):
                # Si hay agentes en la celda, mostramos una 'A' en lugar del suelo
                if (x, y) in self.posicion_agentes and self.posicion_agentes[(x, y)]:
                    fila_visual.append("A")
                else:
                    valor_celda = self.grid[x, y]
                    fila_visual.append(simbolos[valor_celda])
            
            # Imprimir la fila uniendo los caracteres con un espacio
            print(" ".join(fila_visual))
        print("-" * 25)

# --- SCRIPT DE PRUEBA ---

# Mapa 1: Cuello de botella (12x12)
# 0: Libre, 1: Muro, 2: Salida, 3: Fuego
mapa_cuello_botella = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1], # Aquí inicia el embudo
    [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1], # Cuello de botella severo
    [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1], # Única salida disponible
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Instanciamos el mapa (el fuego se propaga cada 1 turno)
mi_mapa = Mapa(mapa_cuello_botella, k_turnos=1)

# Simulamos que hay 3 agentes ubicados en posiciones iniciales
mi_mapa.posicion_agentes = {
    (1, 2): 1,
    (2, 3): 1,
    (4, 5): 1
}

# Mostramos el mapa por consola
mi_mapa.mostrar_mapa()
for _ in range(4):
    mi_mapa.propagar_fuego()
    mi_mapa.mostrar_mapa()