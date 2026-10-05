# IA Tarea 1: Escape de la Torre

Simulador de evacuación de emergencia ante la propagación de fuego en una torre, implementado con diferentes algoritmos de búsqueda y planificación de rutas para agentes autónomos.

> ℹ️ **Nota:** El código ha sido ejecutado y probado únicamente en **Linux**.

---

## 🚀 Ejecución de la Simulación

El programa principal se encuentra en `main.py`, el cual recibe como argumentos el número del mapa, el nombre del algoritmo de búsqueda y, opcionalmente, la cantidad de agentes:

```bash
python3 main.py <numero_mapa> <nombre_algoritmo> [cantidad_agentes]
```

### 1. Parámetros

| Parámetro | Tipo | Opciones válidas | Descripción |
| :--- | :--- | :--- | :--- |
| `<numero_mapa>` | Entero | `1`, `2`, `3` | Identificador del mapa a simular (1: Alta densidad, 2: Densidad media, 3: Baja densidad). |
| `<nombre_algoritmo>` | Texto | `bfs`, `costo_uniforme`, `a_estrella`, `ida_estrella`, `genetico`<br>*(o `"BFS"`, `"Costo Uniforme"`, `"A*"`, `"IDA*"`, `"Genético"`)* | Estrategia de búsqueda y planificación de rutas. |
| `[cantidad_agentes]` | Entero | `1` a `40` *(Opcional)* | Cantidad de agentes en la simulación. **Valor por defecto: 20**. |

> **Notas de sintaxis:**
> - Se pueden utilizar directamente las **claves técnicas** (`bfs`, `costo_uniforme`, `a_estrella`, `ida_estrella`, `genetico`), lo cual evita la necesidad de colocar comillas o escapar caracteres como el asterisco (`*`) en la terminal.
> - Si se utilizan los nombres con espacios o asteriscos (`"A*"`, `"IDA*"`, `"Costo Uniforme"`), se recomienda encerrarlos entre comillas.
> - La cantidad de agentes puede indicarse de forma posicional al final (ej. `30`) o mediante las opciones `--agentes 30` / `-a 30`.

---

### 2. Ejemplos de Uso

```bash
# Ver mensaje de ayuda y sintaxis:
python3 main.py

# --- Uso con claves técnicas (recomendado en terminal) ---
# Mapa 1 con A* (20 agentes por defecto):
python3 main.py 1 a_estrella

# Mapa 1 con A* especificando 25 agentes:
python3 main.py 1 a_estrella 25

# Mapa 2 con Costo Uniforme (35 agentes):
python3 main.py 2 costo_uniforme 35

# Mapa 3 con BFS (15 agentes):
python3 main.py 3 bfs 15

# Mapa 1 con IDA* y 30 agentes mediante flag:
python3 main.py 1 ida_estrella --agentes 30

# Mapa 1 con Algoritmo Genético:
python3 main.py 1 genetico

# --- Uso con nombres formateados (con comillas) ---
python3 main.py 1 "A*" 25
python3 main.py 2 "Costo Uniforme" 35
python3 main.py 1 "IDA*"
```

---

## 🎮 Controles de Interacción en Consola

Durante la ejecución en consola, la simulación permite las siguientes acciones:

- **`[ENTER]`**: Avanza un turno paso a paso.
- **`a` + `[ENTER]`**: Activa el **Modo Automático**, donde los turnos avanzan secuencialmente con un intervalo de tiempo (1 seg. por defecto).
- **`f` + `[ENTER]`**: Salta hasta el **Final**, ejecutando la simulación sin pausas hasta que termine (no queden agentes activos o las salidas estén bloqueadas por fuego).
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

---

## Declaración de Uso Ético de Herramientas de IA Generativa

Se declara que se han utilizado herramientas de inteligencia artificial generativa, como [ChatGPT, Claude Code...], de manera ética y responsable para apoyar la realización de este trabajo. A continuación, se detalla específicamente el uso otorgado:

[✅] Redacción, Estructuración, Mejora del Texto y Corrección Ortográfica: Uso de IA para reescribir ideas originales, organizar secciones, mejorar la coherencia, claridad, estilo, corregir errores gramaticales y ortográficos.

[ ] Traducción: Uso de IA para traducir textos a distintos idiomas.

[✅] Generación de Ideas: Uso de la IA como fuente de inspiración o para explorar enfoques novedosos en el desarrollo del trabajo. Siempre que se han utilizado ideas específicas provenientes de la IA, se ha citado adecuadamente su origen.

[✅] Asesoría Técnica o Conceptual: Consulta sobre conceptos técnicos o metodológicos complejos. La información proporcionada por la IA ha sido revisada, contrastada y validada con fuentes académicas o científicas adecuadas para asegurar su precisión y pertinencia.

Se declara que todo contenido generado o asistido por IA ha sido revisado, adaptado y validado para asegurar su originalidad y pertinencia. Los autores son los únicos responsables del trabajo presentado y se comprometen a que las fuentes utilizadas sean debidamente citadas.
