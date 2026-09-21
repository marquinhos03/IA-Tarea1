
from collections import Counter
from mapa import Mapa, TipoCelda
from agente import Agente, EstadoAgente

class Utilidades:

    @staticmethod
    def mostrar_simulacion(mapa: Mapa, agentes: list[Agente], turno: int) -> None:
        """
        Muestra el estado de la simulación visualmente por consola
        """
        simbolos = {
            TipoCelda.VACIA: " . ",
            TipoCelda.MURO: "###",
            TipoCelda.FUEGO: "[F]",
            TipoCelda.SALIDA: "[E]"
        }

        posiciones_agentes: dict[tuple[int, int], list[Agente]] = {}
        for agente in agentes:
            if agente.es_activo():
                posiciones_agentes.setdefault(agente.pos, []).append(agente)

        recuento_estados = Counter(a.estado for a in agentes)
        activos = recuento_estados[EstadoAgente.ACTIVO]
        evacuados = recuento_estados[EstadoAgente.EVACUADO]
        bajas = recuento_estados[EstadoAgente.BAJA]

        print(f"=== TURNO {turno} | Activos: {activos} | Evacuados: {evacuados} | Bajas: {bajas} ===")
        print()

        for x in range(mapa.filas):
            fila = []
            for y in range(mapa.columnas):
                pos  = (x, y)
                tipo_celda = mapa.get_tipo_celda(x, y)

                if pos in posiciones_agentes and not tipo_celda == TipoCelda.SALIDA:
                    lista_ag = posiciones_agentes[pos]
                    if len(lista_ag) == 1:
                        fila.append(f"A{lista_ag[0].id:<2}")
                    else:
                        fila.append(f"+{len(lista_ag):<2}")
                elif (tipo_celda == TipoCelda.FUEGO) and any((a.estado == EstadoAgente.BAJA and a.pos == pos) for a in agentes):
                    fila.append(" X ")
                else:
                    fila.append(simbolos[tipo_celda])

            print(" ".join(fila))

        