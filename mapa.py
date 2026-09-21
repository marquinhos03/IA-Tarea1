from enum import Enum
from enum import IntEnum
from collections import deque

class TipoCelda(IntEnum):
    VACIA = 0
    MURO = 1
    FUEGO = 2
    SALIDA = 3



class Mapa:
    def __init__(self, 
        filas: int, 
        columnas: int, 
        muros: set[tuple[int, int]], 
        pos_salida: tuple[int, int], 
        fuego: set[tuple[int, int]], 
        capacidad_celda=1
    ):
        self.filas = filas
        self.columnas = columnas
        self.muros = set(muros)
        self.pos_salida = pos_salida
        self.fuego = set(fuego)
        self.capacidad_celda = capacidad_celda

    @classmethod
    def desde_matriz(cls, matriz: list[list[int]], capacidad_celda=1):
        """Crea una instancia de Mapa a partir de una matriz 2D de enteros."""
        filas = len(matriz)
        columnas = len(matriz[0]) if filas > 0 else 0
        muros = set()
        fuego = set()
        pos_salida = None

        for x in range(filas):
            for y in range(columnas):
                valor = matriz[x][y]
                if valor == TipoCelda.MURO:
                    muros.add((x, y))
                elif valor == TipoCelda.FUEGO:
                    fuego.add((x, y))
                elif valor == TipoCelda.SALIDA:
                    pos_salida = (x, y)

        return cls(
            filas=filas,
            columnas=columnas,
            muros=muros,
            pos_salida=pos_salida,
            fuego=fuego,
            capacidad_celda=capacidad_celda
        )

    def esta_en_limites(self, x: int, y: int) -> bool:
        return (0 <= x < self.filas) and (0 <= y < self.columnas)

    def get_tipo_celda(self, x: int, y: int) -> TipoCelda:
        if not self.esta_en_limites(x, y) or (x, y) in self.muros:
            return TipoCelda.MURO
        if (x, y) in self.fuego:
            return TipoCelda.FUEGO
        if (x, y) == self.pos_salida:
            return TipoCelda.SALIDA
        return TipoCelda.VACIA

    def es_celda_transitable(self, x: int, y: int) -> bool:
        """Devuelve True si (x, y) es una celda VACIA o la SALIDA """
        return self.get_tipo_celda(x, y) in (TipoCelda.VACIA, TipoCelda.SALIDA)

    def get_celdas_ortogonales(self, x, y) -> list[tuple[int, int]]:
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        permitidas = []

        for dx, dy in direcciones:
            px, py = x + dx, y + dy
            if self.es_celda_transitable(px, py):
                permitidas.append((px, py))

        return permitidas

    def propagar_fuego(self) -> None:
        nuevo_fuego = set()
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for fx, fy in list(self.fuego):
            for dx, dy in direcciones:
                nx, ny = fx + dx, fy + dy
                if self.esta_en_limites(nx, ny) and (nx, ny) not in self.muros and (nx, ny) not in self.fuego and (nx, ny) != self.pos_salida:
                    nuevo_fuego.add((nx, ny))

        self.fuego.update(nuevo_fuego)
    
    def get_ocupacion_celda(self, pos: tuple[int, int], ocupacion_celdas: dict[tuple[int, int], int]) -> int:
        return ocupacion_celdas.get(pos, 0)

    def funcion_costo_celda(
        self,
        pos_objetivo: tuple[int, int],
        ocupacion_celdas: dict[tuple[int, int], int]
    ) -> float:
        costo_base = 1.0
        ocupacion_celda = ocupacion_celdas.get(pos_objetivo, 0)
        densidad_celda = ocupacion_celda / float(self.capacidad_celda)

        return costo_base + (densidad_celda ** 2)

    
