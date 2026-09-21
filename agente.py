from enum import Enum
from enum import IntEnum

from algoritmos import Algoritmo
from mapa import Mapa

class EstadoAgente(IntEnum):
    ACTIVO = 1
    EVACUADO = 2
    BAJA = 3



class Accion(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    WAIT = (0, 0)



class Agente:
    def __init__(self, id_agente: int, pos_inicial: tuple[int, int]):
        self.id : int = id_agente
        self.pos : tuple[int, int] = pos_inicial
        self.estado : EstadoAgente = EstadoAgente.ACTIVO
        self.ruta_planeada : list[tuple[int, int]] = []
        self.acciones_planeadas: list[Accion] = []
        self.turnos_transcurridos = 0
        self.esta_esperando: bool = False
        self.contador_planificaciones = 0

    def es_activo(self) -> bool:
        return self.estado == EstadoAgente.ACTIVO

    def es_evacuado(self) -> bool:
        return self.estado == EstadoAgente.EVACUADO

    def es_baja(self) -> bool:
        return self.estado == EstadoAgente.BAJA

    def planificar_ruta(self, mapa: Mapa, ocupacion_celdas: dict[tuple[int, int], int]) -> None:
        if not self.es_activo():
            return

        x, y = self.pos

        if not mapa.es_celda_transitable(x, y) and self.pos != mapa.pos_salida:
            self.ruta_planeada = []
            return

        if self.pos == mapa.pos_salida:
            self.ruta_planeada = []
            return

        def es_meta(nodo: tuple[int, int]) -> bool:
            return nodo == mapa.pos_salida

        def expandir(nodo: tuple[int, int]) -> list[tuple[float, tuple[int, int]]]:
            vecinos = []
            nx, ny = nodo

            for nueva_pos in mapa.get_celdas_ortogonales(nx, ny):
                costo = mapa.funcion_costo_celda(nueva_pos, ocupacion_celdas)
                vecinos.append((costo, nueva_pos))

            return vecinos

        camino = Algoritmo.Busqueda_Costo_Uniforme(
            nodo_inicial=self.pos,
            es_meta=es_meta,
            expandir=expandir
        )

        if camino:
            self.ruta_planeada = list(camino)
            return
        else:
            self.ruta_planeada = []

    def ruta_bloqueada(self, mapa: Mapa) -> bool:
        for x, y in self.ruta_planeada:
            if not mapa.es_celda_transitable(x, y):
                return True
        return False

    def marcar_baja(self) -> None:
        self.estado = EstadoAgente.BAJA

    def marcar_evacuado(self) -> None:
        self.estado = EstadoAgente.EVACUADO

    def decidir_siguiente_movimiento(
        self, mapa: Mapa,
        ocupacion_celdas: dict[tuple[int, int], int]
    ) -> tuple[int, int]:
        
        # 1. Si no está activo o ya llegó a la salida, se queda en su posición
        if not self.es_activo() or self.pos == mapa.pos_salida:
            return self.pos
        
        # 2. Replanificar si no tiene ruta, está bloqueada por fuego o si estuvo esperando
        if len(self.ruta_planeada) == 0 or self.ruta_bloqueada(mapa) or (self.es_activo() and self.esta_esperando):
            self.planificar_ruta(mapa, ocupacion_celdas)
            self.contador_planificaciones += 1

        # 3. Si no hay camino posible hacia la salida (Obstruida por propagación del fuego)
        if not self.ruta_planeada:
            return self.pos
        
        # Retornar la intención de movimiento según su ruta
        return self.ruta_planeada[0]

    def aplicar_movimiento(self, nueva_pos: tuple[int, int]) -> None:
        self.turnos_transcurridos += 1

        # Si el movimiento validado coincide con el siguiente paso de la ruta planeada:
        if self.ruta_planeada and self.ruta_planeada[0] == nueva_pos:
            self.pos = nueva_pos
            self.ruta_planeada.pop(0)
            self.esta_esperando = False
        else:
            # Si tuvo que quedarse en su celda (para descongestionar paso o rechazo)
            self.esta_esperando = True
