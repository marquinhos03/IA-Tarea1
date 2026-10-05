from mapa import Mapa
from agente import Agente
import random

SIN_LIMITE = 0

class Simulacion:
    def __init__(
        self, 
        mapa: Mapa, 
        k_turnos_fuego: int | tuple[int, int], 
        nombre_algoritmo: str, 
        max_turnos: int = SIN_LIMITE,
        replanificar_cada_turno: bool = True
    ):
        self.mapa = mapa
        self.nombre_algoritmo = nombre_algoritmo
        self.max_turnos = max_turnos
        self.replanificar_cada_turno = replanificar_cada_turno

        # Si se entrega un intervalo (k_min, k_max), sortea un k fijo para la simulación
        if isinstance(k_turnos_fuego, tuple):
            k_min, k_max = k_turnos_fuego
            self.k_turnos_fuego = random.randint(k_min, k_max)
        else:
            self.k_turnos_fuego = k_turnos_fuego
            
        self.agentes: list[Agente] = []
        self.turno_actual = 0


    # ======================================
    # GENERADO CON IA
    # ======================================
    def _obtener_posiciones_random(
        self,
        cantidad: int,
        distancia_min_salida: int = 10
    ) -> list[tuple[int, int]]:
        """
        Genera una lista de coordenadas aleatorias válidas para los agentes,
        manteniendo una distancia mínima con respecto a la salida.

        Parámetros:
        - cantidad: Número de agentes a agregar.
        - distancia_min_salida: Distancia mínima de casillas respecto a la salida.
        """

        candidatas = []
        candidatas_con_distancia = []
        salida = self.mapa.pos_salida
        for x in range(self.mapa.filas):
            for y in range(self.mapa.columnas):
                pos = (x, y)
                # Validar que la celda este vacía
                if self.mapa.es_celda_vacia(pos):
                    candidatas.append(pos)
                    dist = abs(x - salida[0]) + abs(y - salida[1])      # Uso de distancia manhattan
                    if dist >= distancia_min_salida:
                        candidatas_con_distancia.append(pos)
        # Si hay suficientes celdas respetando la distancia, las usamos;
        # si no, recurrimos a todas las transitables como salvavidas.
        pozo_elegible = candidatas_con_distancia if len(candidatas_con_distancia) >= cantidad else candidatas
        if not pozo_elegible:
            return []
        # Asegurar no pedir más de las disponibles
        cantidad_a_tomar = min(cantidad, len(pozo_elegible))
        return random.sample(pozo_elegible, cantidad_a_tomar)


    def agregar_agentes(
        self, 
        posiciones: list[tuple[int, int]] | None = None, 
        cantidad: int = 1
    ) -> None:
        """
        Agrega agentes a la simulación recibiendo una lista de posiciones o una cantidad para ubicarlos aleatoriamente.
        """

        posiciones_agentes = list(posiciones) if posiciones else self._obtener_posiciones_random(cantidad)
        for i, pos in enumerate(posiciones_agentes):
            nuevo_agente = Agente(
                id_agente=i,
                pos_inicial=pos,
                nombre_algoritmo=self.nombre_algoritmo,
                replanificar_cada_turno=self.replanificar_cada_turno
            )
            self.agentes.append(nuevo_agente)

        
    def agregar_fuego_aleatorio(
        self,
        cantidad: int = 1,
        semilla: int | None = None
    ) -> None:
        """
        Agrega aleatoriamente focos de fuego en celdas transitables vacías y actualiza el conjunto de fuego del mapa (self.mapa.fuego).
        
        Parámetros:
        - cantidad: Número de celdas a incendiar.
        - semilla: Semilla opcional para las posiciones del fuego (Por ej. si semilla=1, los focos aparecerán siempre en las mismas casillas).
        """

        if semilla is not None:
            random.seed(semilla)

        excluir_posiciones = {agente.pos for agente in self.agentes}

        celdas_candidatas = []
        for x in range(self.mapa.filas):
            for y in range(self.mapa.columnas):
                pos = (x, y)
                if self.mapa.es_celda_vacia(pos) and pos not in excluir_posiciones:
                    celdas_candidatas.append(pos)

        cantidad_a_colocar = min(cantidad, len(celdas_candidatas))
        fuego_inicial = random.sample(celdas_candidatas, cantidad_a_colocar) if cantidad_a_colocar > 0 else []
        self.mapa.fuego.update(fuego_inicial)


    def get_ocupacion_celdas(self) -> dict[tuple[int, int], int]:
        """
        Calcula cuántos agentes ocupan actualmente cada celda.
        """
        ocupacion: dict[tuple[int, int], int] = {}

        for agente in self.agentes:
            if agente.es_activo():
                ocupacion_actual = ocupacion.get(agente.pos, 0)
                ocupacion[agente.pos] = ocupacion_actual + 1
        
        return ocupacion


    def ejecutar_turno(self) -> None:
        agentes_activos = [agente for agente in self.agentes if agente.es_activo()]
        ocupacion_celdas = self.get_ocupacion_celdas()
        
        # 1. Fase de Propuesta: Obtener el movimiento propuesto por cada agente activo
        movimientos_tentativos: dict[int, tuple[int, int]] = {}
        for agente in agentes_activos:
            pos_objetivo = agente.decidir_siguiente_movimiento(self.mapa, ocupacion_celdas)
            movimientos_tentativos[agente.id] = pos_objetivo

        # 2. Fase de Resolución de Conflictos: Resolución de sobreocupación de celdas
        fue_rechazado = True
        while fue_rechazado:
            fue_rechazado = False

            # Agrupar donde terminarían los agentes en cada celda según el plan tentativo
            ocupacion_tentativa : dict[tuple[int, int], list[Agente]] = {}
            for agente in agentes_activos:
                destino = movimientos_tentativos[agente.id]
                ocupacion_tentativa.setdefault(destino, []).append(agente)

            for pos_destino, reclamantes in ocupacion_tentativa.items():
                # La salida permite cualquier cantidad de evacuados simultáneos
                if self.mapa.es_celda_salida(pos_destino):
                    continue
                
                # La capacidad física de la celda destino no puede ser superada, por lo que aplicamos unas restricciones de prioridad:
                # 1. El agente que ya estaba en esa celda (residente) tiene prioridad sobre los visitantes.
                # 2. En empate entre visitantes, desempatar por orden de llegada / ID.
                if len(reclamantes) > self.mapa.capacidad_celda:
                    residentes: list[Agente] = []
                    visitantes: list[Agente] = []

                    for agente in reclamantes:
                        if agente.pos == pos_destino:
                            residentes.append(agente)
                        else:
                            visitantes.append(agente)

                    residentes.sort(key=lambda agente: agente.id)
                    visitantes.sort(key=lambda agente: agente.id)

                    # Prioridad: Los residentes van primero, seguidos de los visitantes
                    reclamantes_ordenados = residentes + visitantes
    
                    # Los que no pudieron entrar son rechadazos y vuelven a la posición actual
                    rechazados = reclamantes_ordenados[self.mapa.capacidad_celda:]
                    for agente in rechazados:
                        if movimientos_tentativos[agente.id] != agente.pos:
                            movimientos_tentativos[agente.id] = agente.pos
                            fue_rechazado = True
        
        # 3. Fase de Actualización: Ejecutar los movimientos efectivos ya validados
        for agente in agentes_activos:
            agente.aplicar_movimiento(movimientos_tentativos[agente.id])
        
        # 4. Fase de Propagación de Fuego: Propagar fuego cada k turnos: (siguiente_turno) mod (k turnos) = 0
        siguiente_turno = self.turno_actual + 1
        if siguiente_turno % self.k_turnos_fuego == 0:
            self.mapa.propagar_fuego()

        # 5. Fase de Actualización de Estados: Verificar si hubo evacuados y bajas
        for agente in self.agentes:
            if agente.es_activo() and self.mapa.es_celda_fuego(agente.pos):
                agente.marcar_baja()
            elif agente.es_activo() and self.mapa.es_celda_salida(agente.pos):
                agente.marcar_evacuado(self.turno_actual)

        self.turno_actual = siguiente_turno


    def esta_finalizada(self) -> bool:
        """
        Determina si la simulación ha terminado.
        """

        if self.max_turnos > 0 and self.turno_actual >= self.max_turnos:
            return True
        # Retorna True si no hay ningún agente activo
        return all(not a.es_activo() for a in self.agentes)
