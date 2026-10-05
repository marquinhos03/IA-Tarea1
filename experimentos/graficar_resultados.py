# ======================================
# MODULO GENERADO CON IA
# ======================================

"""
Módulo para generación de gráficas a partir de resultados_benchmark.csv.

Genera únicamente gráficos de barras agrupadas:
1. Una gráfica de barras por cada una de las 5 métricas de rendimiento (comparando los algoritmos por mapa).
2. Un dashboard resumen unificado que integra las 5 métricas en formato de barras.
"""

import os
import sys
import csv
import argparse
from typing import Dict, List, Any
import numpy as np

# Directorio raíz del proyecto
DIRECTORIO_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(DIRECTORIO_RAIZ)

import matplotlib.pyplot as plt

# Paleta de colores consistente para los algoritmos
COLOR_MAP = {
    "bfs": "#1f77b4",            # Azul clásico
    "costo_uniforme": "#ff7f0e", # Naranja
    "a_estrella": "#2ca02c",     # Verde
    "ida_estrella": "#d62728",   # Rojo
    "genetico": "#9467bd",       # Púrpura
}

NOMBRE_ALGORITMO = {
    "bfs": "BFS",
    "costo_uniforme": "Costo Uniforme",
    "a_estrella": "A*",
    "ida_estrella": "IDA*",
    "genetico": "Genético",
}

# Definición de las 5 métricas del benchmark
METRICAS = [
    {
        "columna": "tasa_supervivencia",
        "titulo": "Tasa de Supervivencia por Algoritmo y Mapa",
        "eje_y": "Tasa de Supervivencia (%)",
        "nombre_archivo": "1_tasa_supervivencia",
        "formato_y": "{:.1f}%",
        "limite_y": (0, 105),
    },
    {
        "columna": "tiempo_despeje_media",
        "titulo": "Tiempo Medio de Despeje por Algoritmo y Mapa",
        "eje_y": "Tiempo Medio (turnos)",
        "nombre_archivo": "2_tiempo_despeje_media",
        "formato_y": "{:.1f}",
        "limite_y": None,
    },
    {
        "columna": "tiempo_despeje_desv_est",
        "titulo": "Desviación Estándar del Tiempo de Despeje",
        "eje_y": "Desviación Estándar (turnos)",
        "nombre_archivo": "3_tiempo_despeje_desv_est",
        "formato_y": "{:.1f}",
        "limite_y": (0, None),
    },
    {
        "columna": "tiempo_despeje_min",
        "titulo": "Tiempo de Despeje Mínimo por Algoritmo y Mapa",
        "eje_y": "Tiempo Mínimo (turnos)",
        "nombre_archivo": "4_tiempo_despeje_min",
        "formato_y": "{:.0f}",
        "limite_y": (0, None),
    },
    {
        "columna": "tiempo_despeje_max",
        "titulo": "Tiempo de Despeje Máximo por Algoritmo y Mapa",
        "eje_y": "Tiempo Máximo (turnos)",
        "nombre_archivo": "5_tiempo_despeje_max",
        "formato_y": "{:.0f}",
        "limite_y": (0, None),
    },
]


def cargar_datos(ruta_csv: str) -> List[Dict[str, Any]]:
    """
    Carga y procesa el archivo CSV con los resultados del benchmark.
    """
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo CSV en: {ruta_csv}")

    filas = []
    with open(ruta_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            procesado = {
                "mapa": int(fila["mapa"]),
                "algoritmo": fila["algoritmo"].strip(),
                "iteraciones_ejecutadas": int(fila.get("iteraciones_ejecutadas", 0)),
                "iteraciones_con_evacuados": int(fila.get("iteraciones_con_evacuados", 0)),
                "tasa_supervivencia": float(fila.get("tasa_supervivencia", 0.0)),
                "tiempo_despeje_media": float(fila.get("tiempo_despeje_media", 0.0)),
                "tiempo_despeje_desv_est": float(fila.get("tiempo_despeje_desv_est", 0.0)),
                "tiempo_despeje_min": float(fila.get("tiempo_despeje_min", 0.0)),
                "tiempo_despeje_max": float(fila.get("tiempo_despeje_max", 0.0)),
            }
            filas.append(procesado)

    return filas


def organizar_por_algoritmo_y_mapa(filas: List[Dict[str, Any]]):
    """
    Organiza los registros en estructuras listas para graficar:
    - mapas_ordenados: lista de números de mapa [1, 2, 3]
    - algoritmos: lista de nombres de algoritmos ordenados
    - datos_por_algoritmo: dict[algo -> dict[mapa -> fila]]
    """
    mapas_set = set()
    algoritmos_vistos = set()
    datos_por_algoritmo: Dict[str, Dict[int, Dict[str, Any]]] = {}

    for fila in filas:
        mapa = fila["mapa"]
        algo = fila["algoritmo"]
        mapas_set.add(mapa)
        algoritmos_vistos.add(algo)

        if algo not in datos_por_algoritmo:
            datos_por_algoritmo[algo] = {}
        # En caso de ejecuciones duplicadas para el mismo mapa y algoritmo, se conserva la más reciente
        datos_por_algoritmo[algo][mapa] = fila

    mapas_ordenados = sorted(list(mapas_set))

    # Orden preferente de algoritmos
    orden_preferido = ["bfs", "costo_uniforme", "a_estrella", "ida_estrella", "genetico"]
    algoritmos_ordenados = [a for a in orden_preferido if a in algoritmos_vistos]
    for a in sorted(algoritmos_vistos):
        if a not in algoritmos_ordenados:
            algoritmos_ordenados.append(a)

    return mapas_ordenados, algoritmos_ordenados, datos_por_algoritmo


def aplicar_estilo_base():
    """Configura el estilo visual base de matplotlib."""
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8


def graficar_metrica_barras(
    metrica: Dict[str, Any],
    mapas: List[int],
    algoritmos: List[str],
    datos: Dict[str, Dict[int, Dict[str, Any]]],
    ruta_guardado: str,
):
    """
    Genera y guarda una gráfica de barras agrupadas por mapa para una métrica específica.
    Eje X: Mapas (1, 2, 3, ...)
    Eje Y: Valor de la métrica
    Barras: Una barra de color por cada algoritmo con su valor numérico en el tope.
    """
    aplicar_estilo_base()
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    col = metrica["columna"]
    etiquetas_mapas = [f"Mapa {m}" for m in mapas]
    n_algos = len(algoritmos)
    ancho_barra = 0.8 / max(n_algos, 1)

    x_indices = np.arange(len(mapas))
    valores_maximos = []

    for i, algo in enumerate(algoritmos):
        color = COLOR_MAP.get(algo, None)
        nombre = NOMBRE_ALGORITMO.get(algo, algo.capitalize())
        offset = (i - (n_algos - 1) / 2) * ancho_barra

        y_vals = []
        for m in mapas:
            val = datos.get(algo, {}).get(m, {}).get(col, 0.0)
            y_vals.append(val)
            valores_maximos.append(val)

        barras = ax.bar(
            x_indices + offset,
            y_vals,
            width=ancho_barra,
            label=nombre,
            color=color,
            edgecolor="white",
            linewidth=1.2,
            alpha=0.92,
        )

        # Anotación numérica sobre cada barra
        for bar in barras:
            h = bar.get_height()
            if h > 0:
                ax.annotate(
                    metrica["formato_y"].format(h),
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8.5,
                    fontweight="bold",
                )

    ax.set_xticks(x_indices)
    ax.set_xticklabels(etiquetas_mapas, fontsize=11, fontweight="bold")
    ax.set_xlabel("Escenario (Mapa)", fontsize=12, labelpad=10)
    ax.set_ylabel(metrica["eje_y"], fontsize=12, labelpad=10)
    ax.set_title(metrica["titulo"], fontsize=13.5, fontweight="bold", pad=15)

    # Ajuste de límites verticales con margen superior para etiquetas
    if metrica.get("limite_y"):
        ymin, ymax = metrica["limite_y"]
        if ymax is None and valores_maximos:
            ymax = max(valores_maximos) * 1.15
        ax.set_ylim(bottom=ymin, top=ymax)
    elif valores_maximos:
        max_h = max(valores_maximos)
        ax.set_ylim(bottom=0, top=max_h * 1.18 if max_h > 0 else 10)

    ax.grid(True, linestyle="--", alpha=0.45, axis="y", color="#888888")
    ax.set_axisbelow(True)

    ax.legend(
        title="Algoritmos",
        title_fontsize=10.5,
        fontsize=9.5,
        loc="best",
        frameon=True,
        facecolor="#f9f9f9",
        edgecolor="#cccccc",
    )

    plt.tight_layout()
    fig.savefig(ruta_guardado, dpi=300)
    plt.close(fig)
    print(f"  [✓] Gráfica de barras guardada: {ruta_guardado}")


def graficar_dashboard_barras(
    metricas: List[Dict[str, Any]],
    mapas: List[int],
    algoritmos: List[str],
    datos: Dict[str, Dict[int, Dict[str, Any]]],
    ruta_guardado: str,
):
    """
    Genera un panel integrado (dashboard) de 5 subplots en formato de barras.
    """
    aplicar_estilo_base()
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 10), dpi=300)
    axes_flat = axes.flatten()

    etiquetas_mapas = [f"Mapa {m}" for m in mapas]
    x_indices = np.arange(len(mapas))
    n_algos = len(algoritmos)
    ancho_barra = 0.8 / max(n_algos, 1)

    for idx, metrica in enumerate(metricas):
        ax = axes_flat[idx]
        col = metrica["columna"]
        valores_subplot = []

        for i, algo in enumerate(algoritmos):
            color = COLOR_MAP.get(algo, None)
            nombre = NOMBRE_ALGORITMO.get(algo, algo.capitalize())
            offset = (i - (n_algos - 1) / 2) * ancho_barra

            y_vals = []
            for m in mapas:
                val = datos.get(algo, {}).get(m, {}).get(col, 0.0)
                y_vals.append(val)
                valores_subplot.append(val)

            barras = ax.bar(
                x_indices + offset,
                y_vals,
                width=ancho_barra,
                label=nombre,
                color=color,
                edgecolor="white",
                linewidth=0.8,
                alpha=0.92,
            )

            # Anotación sobre barras en el dashboard
            for bar in barras:
                h = bar.get_height()
                if h > 0:
                    ax.annotate(
                        metrica["formato_y"].format(h),
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 2),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=6.5,
                        fontweight="bold",
                    )

        ax.set_xticks(x_indices)
        ax.set_xticklabels(etiquetas_mapas, fontsize=9.5, fontweight="bold")
        ax.set_title(metrica["titulo"], fontsize=10.5, fontweight="bold")
        ax.set_ylabel(metrica["eje_y"], fontsize=9.0)
        ax.grid(True, linestyle="--", alpha=0.45, axis="y")
        ax.set_axisbelow(True)

        if metrica.get("limite_y"):
            ymin, ymax = metrica["limite_y"]
            if ymax is None and valores_subplot:
                ymax = max(valores_subplot) * 1.18
            ax.set_ylim(bottom=ymin, top=ymax)
        elif valores_subplot:
            max_h = max(valores_subplot)
            ax.set_ylim(bottom=0, top=max_h * 1.20 if max_h > 0 else 10)

    # Subplot 6: Leyenda global
    ax_vacio = axes_flat[5]
    ax_vacio.axis("off")

    handles, labels = axes_flat[0].get_legend_handles_labels()
    if handles:
        ax_vacio.legend(
            handles,
            labels,
            loc="center",
            title="Algoritmos de Búsqueda",
            title_fontsize=12,
            fontsize=11,
            frameon=True,
            facecolor="#f5f5f5",
            edgecolor="#cccccc",
            labelspacing=1.2,
            borderpad=1.5,
        )

    fig.suptitle("Dashboard Comparativo de Rendimiento (Barras) - Benchmark de Evacuación", fontsize=15, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(ruta_guardado, dpi=300)
    plt.close(fig)
    print(f"  [✓] Dashboard de barras guardado: {ruta_guardado}")


def generar_todas_las_graficas(
    ruta_csv: str = os.path.join(DIRECTORIO_RAIZ, "resultados_benchmark.csv"),
    directorio_salida: str = os.path.join(DIRECTORIO_RAIZ, "experimentos", "graficos"),
    generar_dashboard: bool = True,
):
    """
    Función principal que coordina la carga de datos y la generación de las gráficas de barras.
    """
    os.makedirs(directorio_salida, exist_ok=True)
    print(f"\n[+] Cargando datos desde: '{ruta_csv}'...")
    filas = cargar_datos(ruta_csv)
    print(f"    Total de registros leídos: {len(filas)}")

    mapas, algoritmos, datos = organizar_por_algoritmo_y_mapa(filas)
    print(f"    Mapas identificados: {mapas}")
    print(f"    Algoritmos identificados: {[NOMBRE_ALGORITMO.get(a, a) for a in algoritmos]}")

    print(f"\n[+] Generando las 5 gráficas de barras por métrica...")
    for metrica in METRICAS:
        nombre_arch = f"{metrica['nombre_archivo']}.png"
        ruta_arch = os.path.join(directorio_salida, nombre_arch)
        graficar_metrica_barras(metrica, mapas, algoritmos, datos, ruta_arch)

    if generar_dashboard:
        print(f"\n[+] Generando dashboard resumen de barras (5 en 1)...")
        ruta_dashboard = os.path.join(directorio_salida, "dashboard_resumen_metricas.png")
        graficar_dashboard_barras(METRICAS, mapas, algoritmos, datos, ruta_dashboard)

    print(f"\n[✓] ¡Proceso completado exitosamente! Gráficas generadas en: '{directorio_salida}'\n")


def main():
    parser = argparse.ArgumentParser(description="Generador de gráficas de barras para el benchmark de algoritmos.")
    parser.add_argument(
        "--csv",
        type=str,
        default=os.path.join(DIRECTORIO_RAIZ, "resultados_benchmark.csv"),
        help="Ruta al archivo CSV de resultados.",
    )
    parser.add_argument(
        "--salida",
        type=str,
        default=os.path.join(DIRECTORIO_RAIZ, "experimentos", "graficos"),
        help="Directorio de destino para guardar las imágenes de las gráficas.",
    )
    parser.add_argument(
        "--sin-dashboard",
        action="store_true",
        help="Deshabilita la generación del dashboard unificado.",
    )

    args = parser.parse_args()
    generar_todas_las_graficas(
        ruta_csv=args.csv,
        directorio_salida=args.salida,
        generar_dashboard=not args.sin_dashboard,
    )


if __name__ == "__main__":
    main()
