from simulacion import Simulacion
from utilidades import Utilidades, Modos
from mapas import obtener_mapa


# El fuego se expandirá cada k turnos random entre [1, 4] por cada vez que hagamos una simulación
INTERVALO_TURNOS_PROPAGACION_FUEGO = (1, 4)
# Intervalo de segundos para cada turno en el modo automático
INTERVALO_SEGUNDOS_MODO_AUTO = 1.0


def main() -> None:
    num_mapa, nombre_algoritmo, cantidad_agentes = Utilidades.procesar_argumentos()

    # 1. Crear mapa
    m = obtener_mapa(numero=num_mapa, benchmark=False)

    # 2. Inicializar la simulación con el algoritmo seleccionado
    sim = Simulacion(
        mapa=m,
        k_turnos_fuego=INTERVALO_TURNOS_PROPAGACION_FUEGO,
        nombre_algoritmo=nombre_algoritmo,
        replanificar_cada_turno=True
    )
    
    # 3. Agregar agentes y fuego a la simulación
    sim.agregar_agentes(cantidad=cantidad_agentes)
    sim.agregar_fuego_aleatorio(cantidad=1, semilla=None)

    modo = Modos.MANUAL
    while True:
        Utilidades.mostrar_mapa(num_mapa, sim.mapa, sim.agentes, sim.turno_actual, sim.k_turnos_fuego)

        if sim.esta_finalizada():
            break
        if sim.mapa.es_salida_obstruida():
            modo = Modos.FINAL

        modo = Utilidades.esperar_interaccion(modo, delay=INTERVALO_SEGUNDOS_MODO_AUTO)
        sim.ejecutar_turno()

    print("=== SIMULACIÓN TERMINADA ===")


if __name__ == "__main__":
    main()
