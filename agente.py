from enum import Enum
from enum import IntEnum

from algoritmos import Algoritmo
from mapa import Mapa

class EstadoAgente(IntEnum):
    ACTIVO = 1
    EVACUADO = 2
    BAJA = 3



class Agente:
    def __init__(
        self,
        id_agente: int,
        pos_inicial: tuple[int, int],
        algoritmo: str
    ):
        self.id : int = id_agente
        self.pos : tuple[int, int] = pos_inicial
        self.estrategia_busqueda = Algoritmo.busqueda(algoritmo)

        self.estado : EstadoAgente = EstadoAgente.ACTIVO
        self.ruta_planeada : list[tuple[int, int]] = []
        self.costo_ruta: float = 0.0
        self.turnos_transcurridos = 0
        self.esta_esperando: bool = False
        self.contador_planificaciones = 0

    def es_activo(self) -> bool:
        return self.estado == EstadoAgente.ACTIVO

    def es_evacuado(self) -> bool:
        return self.estado == EstadoAgente.EVACUADO

    def es_baja(self) -> bool:
        return self.estado == EstadoAgente.BAJA



    def get_vecinos(
        self,
        nodo: tuple[int, int],
        mapa: Mapa,
        ocupacion_celdas: dict[tuple[int, int], int]
    ) -> list[tuple[float, tuple[int, int]]]:
        """
        Obtiene los movimientos ortogonales válidos desde una celda (nodo) y sus costos de paso.
        """

        vecinos: list[tuple[float, tuple[int, int]]] = []
        nx, ny = nodo

        for nueva_pos in mapa.get_celdas_ortogonales(nx, ny):
            costo = mapa.funcion_costo_celda(nueva_pos, ocupacion_celdas)
            vecinos.append((costo, nueva_pos))

        return vecinos



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

        # Función puente
        def expandir(nodo: tuple[int, int]):
            return self.get_vecinos(nodo, mapa, ocupacion_celdas)

        costo, camino = self.estrategia_busqueda(
            nodo_inicial=self.pos,
            nodo_objetivo=mapa.pos_salida,
            expandir=expandir
        )

        self.costo_ruta = costo
        self.ruta_planeada = camino

        # if camino:
        #     self.ruta_planeada = list(camino)
        #     self.costo_ruta = costo
        #     return
        # else:
        #     self.ruta_planeada = []
        #     self.costo_ruta = float('inf')



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
        self,
        mapa: Mapa,
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
