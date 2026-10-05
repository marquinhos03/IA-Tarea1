# ======================================
# MODULO GENERADO CON IA
# ======================================

from collections import Counter
from mapa import Mapa
from agente import Agente, EstadoAgente
import sys
import time
import select


NOMBRES_ALGORITMOS_DASHBOARD: dict[str, str] = {
    "bfs": "BFS",
    "costo_uniforme": "Costo Uniforme",
    "a_estrella": "A*",
    "ida_estrella": "IDA*",
    "genetico": "Genético",
}

CANTIDAD_AGENTES_DEFAULT = 20
CANTIDAD_AGENTES_MIN = 1
CANTIDAD_AGENTES_MAX = 40


class Colores:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GRIS = "\033[90m"
    ROJO = "\033[91m"
    VERDE = "\033[92m"
    AMARILLO = "\033[93m"
    NARANJA = "\033[38;5;208m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BLANCO = "\033[97m"
    

class Modos:
    MANUAL = "MANUAL"
    AUTO = "AUTO"
    FINAL = "FINAL"

    
    @staticmethod
    def ejecutar_manual(delay: float) -> str:
        """Modo paso a paso: espera la acción explícita del usuario."""
        prompt = (
            f"{Colores.BOLD}[ENTER]{Colores.RESET} Avanzar turno │ "
            f"{Colores.CYAN}[A]{Colores.RESET} Modo automático │ "
            f"{Colores.VERDE}[F]{Colores.RESET} Avanzar al final │ "
            f"{Colores.ROJO}[Q]{Colores.RESET} Salir \n"
            f"{Colores.BOLD}> {Colores.RESET}"
        )
        try:
            opcion = input(prompt).strip().lower()
            if opcion in ("a", "auto"):
                return Modos.AUTO
            elif opcion in ("f", "fin"):
                return Modos.FINAL
            elif opcion in ("q", "quit", "exit"):
                print("\nSimulación finalizada por el usuario.")
                sys.exit(0)
            return Modos.MANUAL
        except (KeyboardInterrupt, EOFError):
            print("\nSimulación finalizada.")
            sys.exit(0)


    @staticmethod
    def ejecutar_final(delay: float) -> str:
        """Modo saltar simulación: salta directamente al final esperado de la simulación"""
        return Modos.FINAL


    @staticmethod
    def ejecutar_auto(delay: float) -> str:
        """Modo automático: avanza cada delay segundos con detección de pausa por tecla."""
        print(
            f"[AUTO] Avanzando cada {delay}s... \n"
            f"Presiona [ENTER] para pausar ",
            end="", 
            flush=True
        )
        
        try:
            if sys.stdin.isatty():
                rlist, _, _ = select.select([sys.stdin], [], [], delay)
                if rlist:
                    sys.stdin.readline()  # Limpia el buffer de entrada

                    sys.stdout.write("\033[1A\033[2K\033[1A\033[2K\r")
                    sys.stdout.flush()

                    print(f"{Colores.AMARILLO}>> Simulación pausada. <<{Colores.RESET}")
                    return Modos.ejecutar_manual(delay)
            else:
                time.sleep(delay)
            print()
            return Modos.AUTO
        except KeyboardInterrupt:
            sys.stdout.write("\033[1A\033[2K\033[1A\033[2K\r")
            sys.stdout.flush()
            
            print(f"\n{Colores.AMARILLO}>> Simulación pausada. <<{Colores.RESET}")
            return Modos.ejecutar_manual(delay)


class Utilidades:

    @staticmethod
    def _obtener_simbolo_muro(mapa: Mapa, pos: tuple[int, int]) -> str:
        """
        Determina dinámicamente el carácter de caja según las conexiones
        ortogonales con otros muros vecinos.
        """

        x, y = pos
        arriba = (x - 1, y) in mapa.muros
        abajo = (x + 1, y) in mapa.muros
        izq = (x, y - 1) in mapa.muros
        der = (x, y + 1) in mapa.muros

        # 1. Cruces e intersecciones en T
        if arriba and abajo and izq and der:
            simbolo = "─┼─"
        elif abajo and izq and der:
            simbolo = "─┬─"
        elif arriba and izq and der:
            simbolo = "─┴─"
        elif arriba and abajo and der:
            simbolo = " ├─"
        elif arriba and abajo and izq:
            simbolo = "─┤ "

        # 2. Esquinas
        elif abajo and der:
            simbolo = " ┌─"
        elif abajo and izq:
            simbolo = "─┐ "
        elif arriba and der:
            simbolo = " └─"
        elif arriba and izq:
            simbolo = "─┘ "

        # 3. Paredes rectas
        elif arriba and abajo:
            simbolo = " │ "    # Pared vertical continua (toca arriba y abajo)
        elif abajo:
            simbolo = " ╷ "    # Comienza hacia abajo (no invade el espacio superior)
        elif arriba:
            simbolo = " ╵ "    # Termina hacia arriba (no invade el espacio inferior)
        elif izq and der:
            simbolo = "───"    # Pared horizontal continua
        elif der:
            simbolo = " ──"    # Comienza la pared hacia la derecha (deja espacio a la izquierda)
        elif izq:
            simbolo = "── "    # Termina la pared hacia la izquierda (deja espacio a la derecha)
        else:
            simbolo = " ─ "    # Muro horizontal aislado

        return Colores.GRIS + simbolo + Colores.RESET


    @staticmethod
    def mostrar_mapa(numero_mapa: int, mapa: Mapa, agentes: list[Agente], turno: int, k_turnos_fuego: int) -> None:
        """
        Muestra el estado del mapa visualmente por consola
        """

        # Limpia la pantalla visible (\033[2J), limpia el scrollback buffer (\033[3J) y ubica el cursor al inicio (\033[H)
        sys.stdout.write("\033[2J\033[3J\033[H")

        posiciones_agentes: dict[tuple[int, int], list[Agente]] = {}
        for agente in agentes:
            if agente.es_activo():
                posiciones_agentes.setdefault(agente.pos, []).append(agente)

        recuento_estados = Counter(a.estado for a in agentes)
        activos = recuento_estados[EstadoAgente.ACTIVO]
        evacuados = recuento_estados[EstadoAgente.EVACUADO]
        bajas = recuento_estados[EstadoAgente.BAJA]

        # Dashboard
        algo_raw = agentes[0].algoritmo if agentes and hasattr(agentes[0], "algoritmo") else ""
        nombre_algoritmo = NOMBRES_ALGORITMOS_DASHBOARD.get(algo_raw.lower(), algo_raw)
        tag_algoritmo = f" [ ALGORITMO: {nombre_algoritmo} ] "
        tag_mapa = f" [ MAPA: {numero_mapa} ] "
        relleno = 53 - 2 - len(tag_algoritmo) - len(tag_mapa) - 2

        print(
            f"{Colores.BOLD}┌──"
            f"{Colores.AMARILLO}{tag_mapa}{Colores.RESET}"
            f"{Colores.BOLD}{'─' * max(0, relleno)}"
            f"{Colores.AZUL}{tag_algoritmo}{Colores.RESET}"
            f"{Colores.BOLD}──┐{Colores.RESET}"
        )
        
        # Fila 1
        print(
            f"{Colores.BOLD}│{Colores.RESET}"
            f" TURNO {turno:<3} "
            f"{Colores.BOLD}│{Colores.RESET}"
            f"{Colores.NARANJA}{Colores.BOLD} Propagación de fuego cada {k_turnos_fuego} turno(s)    {Colores.RESET}"
            f"{Colores.BOLD}│{Colores.RESET}"
        )
        print(f"{Colores.BOLD}├{'─' * 53}┤{Colores.RESET}")

        # Fila 2
        print(
            f"{Colores.BOLD}│{Colores.RESET}"
            f"{Colores.CYAN}  Activos: {activos:<3}   {Colores.RESET}"
            f"{Colores.BOLD}│{Colores.RESET}"
            f"{Colores.VERDE}  Evacuados: {evacuados:<3} {Colores.RESET}"
            f"{Colores.BOLD}│{Colores.RESET}"
            f"{Colores.ROJO}  Bajas: {bajas:<3}     {Colores.RESET}"
            f"{Colores.BOLD}│{Colores.RESET}"
        )
        print(f"{Colores.BOLD}└{'─' * 53}┘{Colores.RESET}")

        for x in range(mapa.filas):
            fila = []
            for y in range(mapa.columnas):
                pos = (x, y)
                if pos in posiciones_agentes and not mapa.es_celda_salida(pos):
                    lista_ag = posiciones_agentes[pos]
                    if len(lista_ag) == 1:
                        fila.append(f"{Colores.CYAN}{Colores.BOLD}A{lista_ag[0].id:<2}{Colores.RESET}")
                    else:
                        fila.append(f"{Colores.MAGENTA}{Colores.BOLD}+{len(lista_ag):<2}{Colores.RESET}")
                elif mapa.es_celda_fuego(pos) and any(agente.es_baja() and agente.pos == pos for agente in agentes):
                    # Si el agente es una baja
                    fila.append(f"{Colores.NARANJA}{Colores.BOLD} X {Colores.RESET}")
                elif mapa.es_celda_fuego(pos):
                    # Si es una celda de fuego
                    fila.append(f"{Colores.ROJO}{Colores.BOLD}[F]{Colores.RESET}")
                elif mapa.es_celda_muro(pos):
                    # Si es un muro
                    fila.append(Utilidades._obtener_simbolo_muro(mapa, pos))
                elif mapa.es_celda_salida(pos):
                    # Si es la salida
                    fila.append(f"{Colores.VERDE}{Colores.BOLD}[E]{Colores.RESET}")
                else:
                    # Si es una celda vacía
                    fila.append(f"{Colores.GRIS} . {Colores.RESET}")
            print("".join(fila))
        print()


    @staticmethod
    def esperar_interaccion(modo: str, delay: float) -> str:
        """
        Gestiona la interacción del usuario según el modo correspondiente.
        """
        seleccionables = {
            Modos.FINAL: Modos.ejecutar_final,
            Modos.AUTO: Modos.ejecutar_auto,
            Modos.MANUAL: Modos.ejecutar_manual,
        }
        # Si el modo no es reconocido, usar MANUAL por defecto
        seleccionado = seleccionables.get(modo, Modos.ejecutar_manual)

        return seleccionado(delay)


    @staticmethod
    def mostrar_mensaje_uso(error: str | None = None) -> None:
        """Muestra un mensaje de ayuda y ejemplos de uso por consola."""
        if error:
            print(f"\n[ERROR] {error}\n")

        print("=" * 68)
        print("  SIMULADOR DE EVACUACIÓN - CONTROL POR LÍNEA DE COMANDOS")
        print("=" * 68)
        print("Uso:")
        print("  python3 main.py <numero_mapa> <nombre_algoritmo> [cantidad_agentes]\n")
        print("Parámetros:")
        print("  <numero_mapa>        Número del mapa a cargar: 1, 2 o 3.")
        print("  <nombre_algoritmo>   Algoritmo de búsqueda:")
        print("                       - 'bfs' o 'BFS'")
        print("                       - 'costo_uniforme' o 'Costo Uniforme'")
        print("                       - 'a_estrella' o 'A*'")
        print("                       - 'ida_estrella' o 'IDA*'")
        print("                       - 'genetico' o 'Genético'")
        print("  [cantidad_agentes]   (Opcional) Número de agentes.")
        print(f"                       Valor por defecto : {CANTIDAD_AGENTES_DEFAULT}")
        print(f"                       Rango permitido   : [{CANTIDAD_AGENTES_MIN}, {CANTIDAD_AGENTES_MAX}]\n")
        print("Ejemplos de ejecución:")
        print("  python3 main.py 1 \"A*\"")
        print("  python3 main.py 1 \"A*\" 25")
        print("  python3 main.py 2 \"Costo Uniforme\"")
        print("  python3 main.py 2 \"Costo Uniforme\" 35")
        print("  python3 main.py 3 BFS 15")
        print("  python3 main.py 1 \"IDA*\"")
        print("  python3 main.py 1 Genético 30")
        print("=" * 68)


    @staticmethod
    def procesar_argumentos() -> tuple[int, str, int]:
        """
        Valida y extrae el número de mapa, el nombre del algoritmo y la cantidad de agentes desde sys.argv.
        Si faltan argumentos o son inválidos, imprime la ayuda y termina la ejecución.
        """
        if len(sys.argv) < 3:
            es_ayuda = len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help", "help")
            Utilidades.mostrar_mensaje_uso()
            sys.exit(0 if es_ayuda else 1)

        # 1. Validar número de mapa
        try:
            num_mapa = int(sys.argv[1])
            if num_mapa not in (1, 2, 3):
                raise ValueError
            # Utilidades.numero_mapa_actual = num_mapa
        except ValueError:
            Utilidades.mostrar_mensaje_uso(f"Número de mapa inválido: '{sys.argv[1]}'. Debe ser 1, 2 o 3.")
            sys.exit(1)

        # 2. Extraer cantidad de agentes (opcional) y nombre del algoritmo
        args_restantes = list(sys.argv[2:])
        cant_agentes = CANTIDAD_AGENTES_DEFAULT

        # Comprobar si se usó flag --agentes o -a
        if "--agentes" in args_restantes or "-a" in args_restantes:
            flag = "--agentes" if "--agentes" in args_restantes else "-a"
            idx = args_restantes.index(flag)
            if idx + 1 >= len(args_restantes):
                Utilidades.mostrar_mensaje_uso(f"Debe especificar un valor numérico tras '{flag}'.")
                sys.exit(1)
            valor_str = args_restantes.pop(idx + 1)
            args_restantes.pop(idx)
            try:
                cant_agentes = int(valor_str)
            except ValueError:
                Utilidades.mostrar_mensaje_uso(f"Cantidad de agentes inválida: '{valor_str}'. Debe ser un número entero.")
                sys.exit(1)
        # O si el último argumento es un entero posicional
        elif len(args_restantes) > 1 and (
            args_restantes[-1].isdigit()
            or (args_restantes[-1].startswith("-") and args_restantes[-1][1:].isdigit())
        ):
            valor_str = args_restantes.pop()
            try:
                cant_agentes = int(valor_str)
            except ValueError:
                Utilidades.mostrar_mensaje_uso(f"Cantidad de agentes inválida: '{valor_str}'. Debe ser un número entero.")
                sys.exit(1)

        # Validar rango de agentes
        if not (CANTIDAD_AGENTES_MIN <= cant_agentes <= CANTIDAD_AGENTES_MAX):
            Utilidades.mostrar_mensaje_uso(
                f"Cantidad de agentes fuera de rango: {cant_agentes}. "
                f"Debe estar entre {CANTIDAD_AGENTES_MIN} y {CANTIDAD_AGENTES_MAX}."
            )
            sys.exit(1)

        # 3. Validar nombre de algoritmo (soporta con o sin comillas)
        algoritmo_arg = " ".join(args_restantes).strip()
        clave_algoritmo = algoritmo_arg.lower()

        # Permitir tanto las claves directas como los nombres del dashboard
        nombres_inversos = {v.lower(): k for k, v in NOMBRES_ALGORITMOS_DASHBOARD.items()}
        if clave_algoritmo in nombres_inversos:
            clave_algoritmo = nombres_inversos[clave_algoritmo]

        if clave_algoritmo not in NOMBRES_ALGORITMOS_DASHBOARD:
            opciones = ", ".join(f"'{k}' / '{v}'" for k, v in NOMBRES_ALGORITMOS_DASHBOARD.items())
            Utilidades.mostrar_mensaje_uso(
                f"Algoritmo '{algoritmo_arg}' no reconocido. Opciones válidas: {opciones}"
            )
            sys.exit(1)

        return num_mapa, clave_algoritmo, cant_agentes
