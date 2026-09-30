# IA Tarea 1: Escape de la Torre

## 🚀 Ejecución de la Simulación

El programa principal se encuentra en `main.py`, el cual recibe como argumentos el número del mapa, el nombre del algoritmo de búsqueda a utilizar y, opcionalmente, la cantidad de agentes:

```bash
python3 main.py <numero_mapa> <nombre_algoritmo> [cantidad_agentes]
```

### 1. Parámetros

| Parámetro | Tipo | Opciones válidas | Descripción |
| :--- | :--- | :--- | :--- |
| `<numero_mapa>` | Entero | `1`, `2`, `3` | Identificador del mapa a simular (1: Alta densidad, 2: Densidad media, 3: Baja densidad). |
| `<nombre_algoritmo>` | Texto | `"BFS"`, `"Costo Uniforme"`, `"A*"`, `"IDA*"`, `"Genético"` | Estrategia de búsqueda y planificación de rutas. |
| `[cantidad_agentes]` | Entero | `1` a `40` *(Opcional)* | Cantidad de agentes en la simulación. **Valor por defecto: 20**. |

> **Notas de sintaxis:**
> - Se recomienda utilizar comillas en aquellos nombres que incluyan espacios o caracteres especiales (como `"A*"`, `"IDA*"` o `"Costo Uniforme"`).
> - La cantidad de agentes puede indicarse de forma posicional al final (ej. `30`) o mediante las opciones `--agentes 30` / `-a 30`.

---

### 2. Ejemplos de Uso

```bash
# Ver mensaje de ayuda y sintaxis:
python3 main.py

# Mapa 1 con algoritmo A* (20 agentes por defecto):
python3 main.py 1 "A*"

# Mapa 1 con A* especificando 25 agentes:
python3 main.py 1 "A*" 25

# Mapa 2 con Costo Uniforme (35 agentes):
python3 main.py 2 "Costo Uniforme" 35

# Mapa 3 con BFS (15 agentes):
python3 main.py 3 BFS 15

# Mapa 1 con IDA* y 30 agentes mediante flag:
python3 main.py 1 "IDA*" --agentes 30

# Mapa 1 con Algoritmo Genético:
python3 main.py 1 Genético
```

---

## 🎮 Controles de Interacción en Consola

Durante la ejecución en consola, la simulación permite las siguientes acciones:

- **`[ENTER]`**: Avanza un turno paso a paso.
- **`a` + `[ENTER]`**: Activa el **Modo Automático**, donde los turnos avanzan secuencialmente con un intervalo de tiempo (1seg. por defecto).
- **`f` + `[ENTER]`**: Salta hasta el **Final**, ejecutando la simulación sin pausas hasta que termine (no hay agentes activos o salidas bloqueadas por fuego).
- **`q` + `[ENTER]`**: Detiene y sale inmediatamente de la simulación.

---

## 🗺️ Leyenda del Mapa

El tablero visualiza en tiempo real el estado de cada celda y los agentes:

| Símbolo | Color | Significado |
| :---: | :--- | :--- |
| **`A#`** | Cian | Agente activo individual con su número identificador (ej. `A0`, `A5`). |
| **`+#`** | Magenta | Celda con más de un agente (ej. `+2`). |
| **`[E]`** | Verde | Salida de emergencia (*Exit*). |
| **`[F]`** | Rojo | Celda en llamas. |
| **`X`** | Naranja | Agente alcanzado por el fuego (baja). |
| **`.`** | Gris | Espacio transitable vacío. |
