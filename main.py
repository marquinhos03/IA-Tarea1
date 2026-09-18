import numpy as np
from enum import Enum
from enum import IntEnum
import heapq
from collections import deque

class TipoCelda(IntEnum):
    LIBRE = 0
    MURO = 1
    SALIDA = 2
    FUEGO = 3

class EstadoAgente(IntEnum):
    ACTIVO = 1
    EVACUADO = 2
    BAJA = 3

class Movimiento(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    STAY = (0, 0)



class Mapa:
    def __init__(self, tipo_mapa, k_turnos, max_capacidad_celda=1):
        self.grid = np.array(tipo_mapa)
        self.filas, self.columnas = self.grid.shape
        self.max_capacidad_celda = max_capacidad_celda

        # Diccionario para ubicar a los agentes: {(x, y): cantidad}
        self.ubicacion_agentes = {}

        # Variables para la propagación del fuego
        self.k_turnos = k_turnos
        self.turno_actual = 0

    def cargar_agentes(self, posicion_agentes):
        """Actualiza la cantidad de personas en cada celda."""
        self.ubicacion_agentes.clear()
        for pos in posicion_agentes:
            self.ubicacion_agentes[pos] = self.ubicacion_agentes.get(pos, 0) + 1

    def mover_agente(self, pos_origen, pos_destino):
        if pos_origen in self.ubicacion_agentes:
            self.ubicacion_agentes[pos_origen] -= 1
            if self.ubicacion_agentes[pos_origen] <= 0:
                del self.ubicacion_agentes[pos_origen]

        self.ubicacion_agentes[pos_destino] = self.ubicacion_agentes.get(pos_destino, 0) + 1

    def remover_agente(self, pos):
        if pos in self.ubicacion_agentes:
            self.ubicacion_agentes[pos] -= 1
            if self.ubicacion_agentes[pos] <= 0:
                del self.ubicacion_agentes[pos]

    def es_celda_disponible(self, pos):
        """Verifica si una celda tiene capacidad física para recibir a otro agente."""
        x, y = pos
        # La salida siempre permite ingresar a los agentes para evacuar
        if self.grid[x, y] == TipoCelda.SALIDA:
            return True
        return self.ubicacion_agentes.get((x, y), 0) < self.max_capacidad_celda
    
    def propagar_fuego(self):
        self.turno_actual += 1

        # Propagar cada k turnos: (turno actual) mod (k turnos) = 0
        if self.turno_actual % self.k_turnos == 0:
            coords_fuego = np.argwhere(self.grid == TipoCelda.FUEGO)

            movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for fx, fy in coords_fuego:
                for mx, my in movimientos:
                    nuevo_x, nuevo_y = fx + mx, fy + my

                    # Nota: el fuego se desplaza de manera ortogonal actualmente
                    if (0 <= nuevo_x and nuevo_x < self.filas) and (0 <= nuevo_y and nuevo_y < self.columnas):
                        if self.grid[nuevo_x, nuevo_y] == TipoCelda.LIBRE:
                            self.grid[nuevo_x, nuevo_y] = TipoCelda.FUEGO

    def funcion_costo_celda(self, x, y):
        if self.grid[x, y] == TipoCelda.MURO or self.grid[x, y] == TipoCelda.FUEGO:
            return float('inf')

        ocupacion_celda = self.ubicacion_agentes.get((x, y), 0)
        costo_base = 1

        return costo_base + (ocupacion_celda ** 2)
    
    def es_meta(self, nodo):
        x, y = nodo
        return self.grid[x, y] == TipoCelda.SALIDA

    def expandir(self, nodo):
        hijos = []
        x, y = nodo

        for mov in Movimiento:
            mx, my = mov.value
            nx, ny = x + mx, y + my

            # 1. Límites del mapa
            if 0 <= nx < self.filas and 0 <= ny < self.columnas:
                # 2. Consultar el costo dinámico al mapa 
                # (Asume que funcion_costo_ocupacion retorna float('inf') si es Fuego o Muro)
                costo = self.funcion_costo_celda(nx, ny)
                if costo != float('inf'):
                    # Retornamos la tupla (estado_hijo, costo_arista) que espera el algoritmo
                    hijos.append((costo, (nx, ny)))

        return hijos

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
        for i in range(self.filas):
            fila_visual = []
            for j in range(self.columnas):
                cantidad = self.ubicacion_agentes.get((i, j), 0)

                if cantidad == 1:
                    fila_visual.append("A")
                elif cantidad > 1:
                    # Muestra el número de personas si hay congestión (o '+' si son 10 o más)
                    fila_visual.append(str(cantidad) if cantidad < 10 else "+")
                else:
                    valor_celda = self.grid[i, j]
                    fila_visual.append(simbolos[valor_celda])
            
            # Imprimir la fila uniendo los caracteres con un espacio
            print(" ".join(fila_visual))
        print("-" * 25)



class Agente:
    def __init__(self, id_ag, pos_inicial):
        self.id = id_ag
        self.pos_actual = pos_inicial
        self.estado = EstadoAgente.ACTIVO
        self.ruta = deque()

    def actualizar_estado(self, mapa):
        # Caso base: el agente no está activo
        if self.estado != EstadoAgente.ACTIVO:
            return

        x, y = self.pos_actual

        if mapa.grid[x, y] == TipoCelda.FUEGO:
            self.estado = EstadoAgente.BAJA
            mapa.remover_agente(self.pos_actual)
        elif mapa.grid[x, y] == TipoCelda.SALIDA:
            self.estado = EstadoAgente.EVACUADO
            mapa.remover_agente(self.pos_actual)

    def planificar_ruta(self, mapa):
        """Planifica la ruta de evacuación con respecto el algoritmo elegido."""
        if self.estado == EstadoAgente.ACTIVO:
            camino = Algoritmo.Busqueda_Costo_Uniforme(
                nodo_inicial=self.pos_actual,
                es_meta=mapa.es_meta,
                expandir=mapa.expandir
            )
            self.ruta = deque(camino)

    def ejecutar_movimiento(self, mapa):
        """Si el agente está activo y tiene una ruta, ejecuta el siguiente movimiento y lo actualiza en el mapa."""
        if self.estado == EstadoAgente.ACTIVO and self.ruta:
            siguiente_posicion = self.ruta[0]
            if mapa.es_celda_disponible(siguiente_posicion):
                self.ruta.popleft()
                mapa.mover_agente(self.pos_actual, siguiente_posicion)
                self.pos_actual = siguiente_posicion
            else:
                pass

    

class Algoritmo:

    # Usualmente visto con PriorityQueue(), pero aqui se usa HeapQ
    @staticmethod
    def Busqueda_Costo_Uniforme(nodo_inicial, es_meta, expandir):
        frontera = []
        heapq.heappush(frontera, (0, nodo_inicial))

        costos_minimos = {nodo_inicial: 0}
        padres = {nodo_inicial: None}

        nodo_objetivo = None

        while frontera:
            costo_g, nodo_actual = heapq.heappop(frontera)

            if es_meta(nodo_actual):
                nodo_objetivo = nodo_actual
                break

            if costo_g > costos_minimos[nodo_actual]:
                continue

            for (costo_arista, hijo) in expandir(nodo_actual):
                nuevo_costo = costo_g + costo_arista

                if hijo not in costos_minimos or nuevo_costo < costos_minimos[hijo]:
                    costos_minimos[hijo] = nuevo_costo
                    padres[hijo] = nodo_actual
                    heapq.heappush(frontera, (nuevo_costo, hijo))

        if nodo_objetivo:
            camino_encontrado = []
            nodo_paso = nodo_objetivo

            while padres[nodo_paso] is not None:
                camino_encontrado.append(nodo_paso)
                nodo_paso = padres[nodo_paso]

            camino_encontrado.reverse()
            return camino_encontrado

        return []
    

# --- MOTOR DE SIMULACIÓN PRINCIPAL ---

# Mapa 1: Cuello de botella (12x12)
mapa_cuello_botella = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Instanciamos el mapa
mi_mapa = Mapa(mapa_cuello_botella, k_turnos=1)

# Instanciamos a los agentes
agentes = [
    Agente(id_ag=1, pos_inicial=(1, 2)),
    Agente(id_ag=2, pos_inicial=(2, 3)),
    Agente(id_ag=3, pos_inicial=(4, 5)),
    Agente(id_ag=4, pos_inicial=(1, 4)),
    Agente(id_ag=5, pos_inicial=(2, 1)),
    Agente(id_ag=6, pos_inicial=(2, 7)),
    Agente(id_ag=7, pos_inicial=(3, 7))
]

mi_mapa.cargar_agentes([ag.pos_actual for ag in agentes])

print("=== INICIANDO SIMULACIÓN ===")

# Simularemos hasta 9 turnos (o hasta que todos terminen)
for turno in range(10):
    # Mostrar estado inicial del mapa
    if turno == 0:
        mi_mapa.mostrar_mapa()
        continue

    # 1. El entorno dinámico actúa primero (el fuego se propaga)
    mi_mapa.propagar_fuego()
    
    # 2. Los agentes reaccionan al entorno (verifican si el fuego los alcanzó)
    for ag in agentes:
        ag.actualizar_estado(mi_mapa)
        
    # 3. Fase de planificación y movimiento coordinado con el mapa actualmente
    for ag in agentes:
        if ag.estado == EstadoAgente.ACTIVO:
            # Recalcula ruta y se desplaza informando al mapa en tiempo real
            # Nota 1: actualmente se recalcula la ruta por cada turno, llamando al algoritmo muchas veces
            # Nota 2: los agentes eligen su ruta por orden de llegada
            ag.planificar_ruta(mi_mapa)
            ag.ejecutar_movimiento(mi_mapa)
            ag.actualizar_estado(mi_mapa) 

    # 4. Renderizamos la terminal
    mi_mapa.mostrar_mapa()
    
    # 5. Reporte de estado para el turno actual
    activos = sum(1 for ag in agentes if ag.estado == EstadoAgente.ACTIVO)
    evacuados = sum(1 for ag in agentes if ag.estado == EstadoAgente.EVACUADO)
    bajas = sum(1 for ag in agentes if ag.estado == EstadoAgente.BAJA)
    
    print(f"Sobrevivientes en tránsito: {activos} | Evacuados a salvo: {evacuados} | Bajas: {bajas}")
    
    # Condición de término temprano: si ya no queda nadie activo, terminamos simulación
    if activos == 0:
        print("\n=== SIMULACIÓN FINALIZADA ===")
        break