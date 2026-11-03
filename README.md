# Misioneros y Caníbales — Búsqueda ciega en espacios de estados

Tarea Individual **DG_S4** — Inteligencia Artificial, Escuela Politécnica Nacional.
Autor: Christopher Pulupa.

Modelado formal del problema clásico de los misioneros y caníbales como un
problema de búsqueda en espacio de estados, con implementación en Python puro
(sin interfaz gráfica) de:

- **BFS** (búsqueda en anchura, frontera FIFO / cola),
- **DFS** (búsqueda en profundidad, frontera LIFO / pila),
- **A\*** con una heurística admisible y consistente obtenida por relajación
  del problema (como referencia de búsqueda informada).

## Representación

Un estado es la tupla `(m_izq, c_izq, b)`:

| campo   | significado                                        |
|---------|----------------------------------------------------|
| `m_izq` | misioneros en la orilla izquierda (0..N)           |
| `c_izq` | caníbales en la orilla izquierda (0..N)            |
| `b`     | 1 si el bote está en la orilla izquierda, 0 si no  |

- Estado inicial: `(3, 3, 1)`. Estado objetivo: `(0, 0, 0)`.
- Acciones: `(m, c)` personas a bordo con `1 <= m + c <= K` (K = 2).
- Un estado es válido si en ninguna orilla los misioneros (cuando hay alguno)
  quedan en minoría frente a los caníbales.

El modelo está generalizado a `N` misioneros, `N` caníbales y bote de
capacidad `K` para el análisis de escalabilidad.

## Uso

Requiere Python 3.10+ y **ninguna** dependencia externa.

```bash
# Resolver la instancia clásica (3, 3, K=2) con BFS y DFS y mostrar los caminos
python3 main.py

# Elegir algoritmo e instancia
python3 main.py --algoritmo dfs
python3 main.py --algoritmo astar -n 5 -k 3

# Benchmark completo (tabla comparativa + CSV en resultados/)
python3 benchmark.py

# Pruebas unitarias
python3 -m unittest discover -s tests -v
```

## Estructura

```
src/problema.py   Formulación: estados, acciones, modelo de transición, validez
src/busqueda.py   BFS, DFS, A* y estructura de métricas
src/metricas.py   Factor de ramificación efectivo b*
main.py           CLI para resolver e imprimir la solución
benchmark.py      Experimentos y tabla comparativa
tests/            Pruebas unitarias
resultados/       Salida del benchmark (CSV / Markdown)
```
