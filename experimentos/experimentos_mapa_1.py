"""
Experimentos de Benchmarking para el Mapa 1.
Ejecuta el experimento para el Mapa 1 usando cada uno de los algoritmos de búsqueda.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from experimentos import ejecutar_experimentos_para_mapa, ALGORITMOS_BENCHMARK


def main() -> None:
    ejecutar_experimentos_para_mapa(
        num_mapa=1,
        algoritmos=ALGORITMOS_BENCHMARK,
        num_iteraciones=80,
        cantidad_agentes=80,
    )


if __name__ == "__main__":
    main()
