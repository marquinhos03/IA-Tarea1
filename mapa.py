from enum import IntEnum
from collections import deque

class TipoCelda(IntEnum):
    VACIA = 0
    MURO = 1
    FUEGO = 2
    SALIDA = 3

DIRECCIONES = ((0, -1), (0, 1), (-1, 0), (1, 0))


class Mapa:
    DIRECCIONES = DIRECCIONES
    
    def __init__(self, 
        filas: int, 
        columnas: int, 
        muros: set[tuple[int, int]], 
        pos_salida: tuple[int, int], 
        fuego: set[tuple[int, int]], 
        capacidad_celda: int = 1
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


    def esta_dentro_de_limites(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        return (0 <= x < self.filas) and (0 <= y < self.columnas)


    def es_celda_muro(self, pos: tuple[int, int]) -> bool:
        """Indica si la posición es un muro o está fuera de los límites del mapa."""
        return not self.esta_dentro_de_limites(pos) or pos in self.muros


    def es_celda_fuego(self, pos: tuple[int, int]) -> bool:
        """Indica si la posición es una celda de fuego."""
        return pos in self.fuego


    def es_celda_salida(self, pos: tuple[int, int]) -> bool:
        """Indica si la posición es la celda de salida."""
        return self.pos_salida is not None and pos == self.pos_salida


    def es_celda_vacia(self, pos: tuple[int, int]) -> bool:
        """Indica si la posición es una celda transitable, sin fuego y no es la salida."""
        return (
            self.esta_dentro_de_limites(pos)
            and pos not in self.muros
            and pos not in self.fuego
            and pos != self.pos_salida
        )

    
    def es_celda_transitable(self, pos: tuple[int, int]) -> bool:
        """Indica si una celda está vacía (puede ser la salida)."""
        return (
            self.esta_dentro_de_limites(pos)
            and pos not in self.muros
            and pos not in self.fuego
        )


    def es_salida_obstruida(self, desde_pos: tuple[int, int] | None = None) -> bool:
        """
        Determina si la salida o sus accesos han sido obstruidos/consumidos por el fuego.
        - Si se especifica 'desde_pos', verifica si la salida es alcanzable desde esa posición.
        - Si no se especifica, verifica si la salida está aislada del resto del mapa transitable.
        """
        if self.pos_salida is None or self.es_celda_fuego(self.pos_salida):
            return True

        vecinos_salida = self.get_celdas_ortogonales(self.pos_salida)
        if not vecinos_salida:
            return True

        # Caso 1: Consulta particular desde la posición de un agente
        if desde_pos is not None:
            if desde_pos == self.pos_salida:
                return False
            if not self.es_celda_transitable(desde_pos):
                return True

            cola = deque([desde_pos])
            visitados = {desde_pos}
            while cola:
                curr = cola.popleft()
                if curr == self.pos_salida:
                    return False
                for vecino in self.get_celdas_ortogonales(curr):
                    if vecino not in visitados:
                        visitados.add(vecino)
                        cola.append(vecino)
            return True

        # Caso 2: Consulta global (usada por el simulador o main.py)
        cola = deque([self.pos_salida])
        visitados = {self.pos_salida}
        while cola:
            curr = cola.popleft()
            if len(visitados) >= 15:
                return False
            for vecino in self.get_celdas_ortogonales(curr):
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)

        return True


    def get_tipo_celda(self, pos: tuple[int, int]) -> TipoCelda:
        if self.es_celda_muro(pos):
            return TipoCelda.MURO
        if self.es_celda_fuego(pos):
            return TipoCelda.FUEGO
        if self.es_celda_salida(pos):
            return TipoCelda.SALIDA
        return TipoCelda.VACIA


    def get_celdas_ortogonales(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        permitidas = []

        x, y = pos
        for dx, dy in DIRECCIONES:
            vecino = (x + dx, y + dy)
            if self.es_celda_transitable(vecino):
                permitidas.append(vecino)

        return permitidas


    def propagar_fuego(self) -> None:
        nuevo_fuego = set()

        for fx, fy in list(self.fuego):
            for dx, dy in DIRECCIONES:
                vecino = (fx + dx, fy + dy)
                if self.es_celda_vacia(vecino):
                    nuevo_fuego.add(vecino)

        self.fuego.update(nuevo_fuego)


    def funcion_costo_celda(
        self,
        pos_objetivo: tuple[int, int],
        ocupacion_celdas: dict[tuple[int, int], int]
    ) -> float:
        
        costo_base = 1.0
        ocupacion_celda = ocupacion_celdas.get(pos_objetivo, 0)
        densidad_celda = ocupacion_celda / float(self.capacidad_celda)

        return costo_base + (densidad_celda ** 2)
