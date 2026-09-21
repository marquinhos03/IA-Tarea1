
from mapa import Mapa, TipoCelda
from agente import Agente

class Simulacion:
    def __init__(
        self, 
        mapa: Mapa, 
        posiciones_agentes: list[tuple[int, int]], 
        k_turnos_fuego: int, 
        max_turnos: int
    ):
        self.mapa = mapa
        self.k_turnos = k_turnos_fuego
        self.max_turnos = max_turnos

        # Instanciar agentes
        self.agentes: list[Agente] = []
        for i, pos in enumerate(posiciones_agentes):
            self.agentes.append(Agente(id_agente=i, pos_inicial=pos))

        self.turno_actual = 0

    def get_ocupacion_celdas(self) -> dict[tuple[int, int], int]:
        """Calcula cuántos agentes ocupan actualmente cada celda."""
        ocupacion = {}

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

            # DEBUG
            print(f"[{agente.id}] Ruta elegida: {agente.ruta_planeada}")
            print(f"[{agente.id}]Total planificaciones: {agente.contador_planificaciones}")
            print(f"[{agente.id}]Estado de espera: {agente.esta_esperando}")
            print()

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
                if pos_destino == self.mapa.pos_salida:
                    continue
                # La capacidad física de la celda destino no puede ser superada, por lo que aplicamos unas restricciones de prioridad:
                # 1. El agente que ya estaba en esa celda (residente) tiene prioridad sobre los visitantes.
                # 2. En empate entre visitantes, desempatar por orden de llegada / ID.
                if len(reclamantes) > self.mapa.capacidad_celda:
                    residentes : list[Agente] = []
                    visitantes : list[Agente] = []

                    for agente in reclamantes:
                        if agente.pos == pos_destino:
                            residentes.append(agente)
                        else:
                            visitantes.append(agente)

                    def obtener_id(agente):
                        return agente.id

                    residentes.sort(key=obtener_id)
                    visitantes.sort(key=obtener_id)

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
        if siguiente_turno % self.k_turnos == 0:
            self.mapa.propagar_fuego()

        # 5. Fase de Actualización de Estados: Verificar si hubo evacuados y bajas
        for agente in self.agentes:
            if agente.es_activo() and agente.pos in self.mapa.fuego:
                agente.marcar_baja()
            elif agente.es_activo() and agente.pos == self.mapa.pos_salida:
                agente.marcar_evacuado()

        self.turno_actual = siguiente_turno

    def esta_finalizada(self) -> bool:
        """
        Determina si la simulación ha terminado.
        """
        if self.turno_actual >= self.max_turnos:
            return True
        # Retorna True si no hay ningún agente activo
        return all(not a.es_activo() for a in self.agentes)

    