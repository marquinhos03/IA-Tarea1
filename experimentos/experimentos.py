"""
Módulo para Métricas de Benchmarking y Experimentos.
"""

import csv
import os
import sys
import statistics
from dataclasses import dataclass, asdict, fields
from typing import Callable

# Directorio raíz del proyecto en sys.path
DIRECTORIO_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(DIRECTORIO_RAIZ)

from mapa import Mapa
from simulacion import Simulacion
from mapas import (
    obtener_mapa_1_benchmark,
    obtener_mapa_2_benchmark,
    obtener_mapa_3_benchmark,
)

ALGORITMOS_BENCHMARK = [
    "BFS",
    "Costo Uniforme",
    "A*",
    "IDA*",
    #"Genético",
]

FABRICAS_MAPAS_BENCHMARK = {
    1: lambda: obtener_mapa_1_benchmark(capacidad_celda=1),
    2: lambda: obtener_mapa_2_benchmark(capacidad_celda=1),
    3: lambda: obtener_mapa_3_benchmark(capacidad_celda=1),
}

RUTA_CSV_DEFAULT = os.path.join(DIRECTORIO_RAIZ, "resultados_benchmark.csv")


@dataclass
class ResultadoIteracion:
    total_agentes: int
    sobrevivientes: int
    tasa_supervivencia: float
    tiempo_despeje: int
    turnos_totales: int


@dataclass
class ResultadoExperimento:
    mapa: int
    algoritmo: str
    iteraciones_ejecutadas: int
    iteraciones_con_evacuados: int
    tasa_supervivencia: float
    tiempo_despeje_media: float
    tiempo_despeje_desv_est: float
    tiempo_despeje_min: int
    tiempo_despeje_max: int


# Nivel 1
def ejecutar_iteracion(
    crear_mapa_fn: Callable[[], Mapa],
    algoritmo: str,
    posiciones_agentes: list[tuple[int, int]] | None = None,
    cantidad_agentes: int = 80,
    cantidad_fuego: int = 1,
    semilla_fuego: int | None = None,
    k_turnos_fuego: int | tuple[int, int] = (1, 4),
    replanificar_cada_turno: bool = True
) -> ResultadoIteracion:
    """
    Ejecuta una iteración completa de la simulación (sin interfaz) y recopila las métricas de dicha simulación.
    """

    # 1. Instanciar un mapa nuevo e inalterado
    mapa = crear_mapa_fn()

    # 2. Inicializar la simulación
    # Sin limite de turnos
    sim = Simulacion(
        mapa=mapa,
        k_turnos_fuego=k_turnos_fuego,
        algoritmo_busqueda=algoritmo,
        replanificar_cada_turno=replanificar_cada_turno
    )

    # 3. Posicionar agentes y fuego
    sim.agregar_agentes(posiciones=posiciones_agentes, cantidad=cantidad_agentes)
    sim.agregar_fuego_aleatorio(cantidad=cantidad_fuego, semilla=semilla_fuego)

    # 4. Iniciar la simulación hasta que termine finalización
    while not sim.esta_finalizada():
        sim.ejecutar_turno()

    # 5. Extraer métricas
    total_agentes = len(sim.agentes)
    sobrevivientes = [a for a in sim.agentes if a.es_evacuado()]
    num_sobrevivientes = len(sobrevivientes)
    
    # Tasa de supervivencia (0.0 a 1.0)
    tasa_supervivencia = num_sobrevivientes / float(total_agentes)       # N_sobrevivientes / N_total
    
    # Tiempo de despeje: turno en el que evacuó el último sobreviviente
    # -1 si no hubo sobrevivientes
    tiempo_despeje = max(a.turno_evacuacion for a in sobrevivientes) if num_sobrevivientes > 0 else -1

    return ResultadoIteracion(
        total_agentes=total_agentes,
        sobrevivientes=num_sobrevivientes,
        tasa_supervivencia=tasa_supervivencia,
        tiempo_despeje=tiempo_despeje,
        turnos_totales=sim.turno_actual
    )


# Nivel 2
def ejecutar_iteraciones(
    num_iteraciones: int,
    crear_mapa_fn: Callable[[], Mapa],
    algoritmo: str,
    **kwargs
) -> list[ResultadoIteracion]:
    """
    Ejecuta N iteraciones para una configuración dada, variando las condiciones estocásticas.
    """

    resultados_iteraciones = []
    for i in range(num_iteraciones):
        # Si no se fija semilla fija en kwargs, cada iteración tendrá fuego aleatorio diferente
        datos_simulacion = ejecutar_iteracion(
            crear_mapa_fn=crear_mapa_fn,
            algoritmo=algoritmo,
            **kwargs
        )
        resultados_iteraciones.append(datos_simulacion)

        # Seguimiento de iteraciones (Avisar cada 20 iteraciones)
        if (i + 1) % 20 == 0:
            print(f"  -> {i + 1}/{num_iteraciones} iteraciones completadas...")

    return resultados_iteraciones


# Nivel 3
def ejecutar_experimento(
    num_mapa: int,
    crear_mapa_fn: Callable[[], Mapa],
    nombre_algoritmo: str,
    num_iteraciones: int = 80,
    **kwargs
) -> ResultadoExperimento:
    """
    Ejecuta el experimento completo y reporta las métricas descriptivas:
    - Tasa de supervivencia
    - Tiempos de despeje (media, desviación estandar, min, max)
    """

    print(f"-> Iniciando experimento: Mapa {num_mapa} | Algoritmo: {nombre_algoritmo} ({num_iteraciones} iteraciones)...")
    
    iteraciones = ejecutar_iteraciones(
        num_iteraciones=num_iteraciones,
        crear_mapa_fn=crear_mapa_fn,
        algoritmo=nombre_algoritmo,
        **kwargs
    )

    # 1. Estadísticas de supervivencia

    # Tasas de supervivencia de cada una de las iteraciones
    tasas_superviviencia = [i.tasa_supervivencia for i in iteraciones]
    # Media de todas las iteraciones
    media_supervivencia = statistics.mean(tasas_superviviencia)
    porcentaje_tasa_supervivencia = media_supervivencia * 100.0

    # 2. Estadísticas de tiempo de despeje (turnos)

    tiempos_despeje = [i.tiempo_despeje for i in iteraciones if i.tiempo_despeje != -1]

    # ¿tiempos_despeje podria devolver []?

    iteraciones_con_evacuados = len(tiempos_despeje)

    media_tiempo = statistics.mean(tiempos_despeje)
    desviacion_estandar_tiempo = statistics.stdev(tiempos_despeje) if len(tiempos_despeje) > 1 else 0.0
    min_tiempo = min(tiempos_despeje)
    max_tiempo = max(tiempos_despeje)

    return ResultadoExperimento(
        mapa=num_mapa,
        algoritmo=nombre_algoritmo,
        iteraciones_ejecutadas=num_iteraciones,
        iteraciones_con_evacuados=iteraciones_con_evacuados,
        tasa_supervivencia=porcentaje_tasa_supervivencia,
        tiempo_despeje_media=media_tiempo,
        tiempo_despeje_desv_est=desviacion_estandar_tiempo,
        tiempo_despeje_min=min_tiempo,
        tiempo_despeje_max=max_tiempo
    )
    

def exportar_resumen_csv(
    resumen: ResultadoExperimento | list[ResultadoExperimento],
    ruta_archivo: str = RUTA_CSV_DEFAULT
) -> None:
    """
    Exporta el resúmen de los experimentos a un archivo CSV.
    """

    resumenes = [resumen] if isinstance(resumen, ResultadoExperimento) else resumen

    columnas = [f.name for f in fields(ResultadoExperimento)]
    
    # Verificar si el archivo ya existe antes de abrirlo
    archivo_existe = os.path.exists(ruta_archivo)

    with open(ruta_archivo, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        if not archivo_existe:
            writer.writeheader()

        for r in resumenes:
            # 1. Convertir el dataclass en un diccionario de pares clave-valor
            datos_experimento = asdict(r)

            # 2. Construir fila
            fila = {}
            for clave, valor in datos_experimento.items():
                if isinstance(valor, float):
                    fila[clave] = round(valor, 2)
                else:
                    fila[clave] = valor

            # 3. Escribir la fila formateada en el archivo CSV
            writer.writerow(fila)

    print(f"-> Resumen exportado con éxito a: '{ruta_archivo}'")


def ejecutar_experimentos_para_mapa(
    num_mapa: int,
    algoritmos: list[str] = ALGORITMOS_BENCHMARK,
    num_iteraciones: int = 80,
    cantidad_agentes: int = 80,
    guardar_csv: bool = True,
    ruta_archivo: str = RUTA_CSV_DEFAULT,
    **kwargs
) -> list[ResultadoExperimento]:
    """
    Ejecuta el experimento de benchmarking para un mapa dado probando cada uno de los algoritmos especificados.
    """
    crear_mapa_fn = FABRICAS_MAPAS_BENCHMARK[num_mapa]
    resultados: list[ResultadoExperimento] = []

    print(f"\n=======================================================")
    print(f" INICIANDO BENCHMARK PARA MAPA {num_mapa} ({len(algoritmos)} ALGORITMOS)")
    print(f"=======================================================")

    for algo in algoritmos:
        res = ejecutar_experimento(
            num_mapa=num_mapa,
            crear_mapa_fn=crear_mapa_fn,
            nombre_algoritmo=algo,
            num_iteraciones=num_iteraciones,
            cantidad_agentes=cantidad_agentes,
            **kwargs
        )
        if guardar_csv:
            exportar_resumen_csv(res, ruta_archivo=ruta_archivo)
        resultados.append(res)

    return resultados


def imprimir_resumen_experimento(resultado: ResultadoExperimento) -> None:
    """
    Imprime en consola los resultados formateados de un experimento.
    """
    print("\n=== RESULTADOS DEL BENCHMARK ===")
    print(f"Mapa: {resultado.mapa}")
    print(f"Algoritmo: {resultado.algoritmo}")
    print(f"Iteraciones ejecutadas: {resultado.iteraciones_ejecutadas}")
    print(f"Iteraciones con evacuados: {resultado.iteraciones_con_evacuados}")
    print(f"Tasa de supervivencia: {resultado.tasa_supervivencia:.2f}%")
    print(f"Tiempo de despeje (turnos):")
    print(f"  - Media: {resultado.tiempo_despeje_media:.2f}")
    print(f"  - Desviación Estándar: {resultado.tiempo_despeje_desv_est:.2f}")
    print(f"  - Mínimo: {resultado.tiempo_despeje_min}")
    print(f"  - Máximo: {resultado.tiempo_despeje_max}\n")
