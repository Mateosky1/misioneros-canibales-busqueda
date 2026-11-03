"""Algoritmos de búsqueda sobre el espacio de estados.

Todas las búsquedas son de *grafo* (mantienen un conjunto de alcanzados), de
modo que cada estado se expande a lo sumo una vez. El test objetivo se aplica
al extraer el nodo de la frontera, con el mismo criterio en todos los
algoritmos para que el número de nodos expandidos sea comparable.

Definiciones usadas en las métricas:
* nodo expandido : nodo extraído de la frontera al que se le generan sucesores.
* nodo generado  : nodo hijo creado por la función de sucesores (válido).
* memoria máxima : máximo de |frontera| + |explorados| durante la búsqueda,
                   es decir, el número de nodos simultáneamente en memoria.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from .problema import Accion, Estado, MisionerosCanibales


@dataclass
class Nodo:
    estado: Estado
    padre: Optional["Nodo"] = None
    accion: Optional[Accion] = None
    profundidad: int = 0

    def camino(self) -> list["Nodo"]:
        nodos, n = [], self
        while n is not None:
            nodos.append(n)
            n = n.padre
        return nodos[::-1]


@dataclass
class Resultado:
    algoritmo: str
    solucion: Optional[Nodo] = None
    nodos_expandidos: int = 0
    nodos_generados: int = 0
    max_frontera: int = 0
    max_memoria: int = 0
    orden_expansion: list[Estado] = field(default_factory=list)

    @property
    def encontrada(self) -> bool:
        return self.solucion is not None

    @property
    def longitud(self) -> Optional[int]:
        return self.solucion.profundidad if self.solucion else None

    @property
    def acciones(self) -> list[tuple[Estado, Accion]]:
        if not self.solucion:
            return []
        nodos = self.solucion.camino()
        return [(nodos[i].estado, nodos[i + 1].accion) for i in range(len(nodos) - 1)]

    @property
    def estados(self) -> list[Estado]:
        return [n.estado for n in self.solucion.camino()] if self.solucion else []


def _hijo(padre: Nodo, accion: Accion, estado: Estado) -> Nodo:
    return Nodo(estado, padre, accion, padre.profundidad + 1)


# --------------------------------------------------------------------- BFS
def bfs(problema: MisionerosCanibales, registrar_orden: bool = False) -> Resultado:
    """Búsqueda en anchura: frontera FIFO (cola, collections.deque)."""
    r = Resultado("BFS")
    raiz = Nodo(problema.estado_inicial)
    frontera: deque[Nodo] = deque([raiz])
    alcanzados: set[Estado] = {raiz.estado}   # en frontera o ya expandidos

    while frontera:
        r.max_frontera = max(r.max_frontera, len(frontera))
        r.max_memoria = max(r.max_memoria, len(alcanzados))
        nodo = frontera.popleft()
        if problema.es_objetivo(nodo.estado):
            r.solucion = nodo
            return r
        r.nodos_expandidos += 1
        if registrar_orden:
            r.orden_expansion.append(nodo.estado)
        for accion, s2 in problema.sucesores(nodo.estado):
            if s2 not in alcanzados:
                alcanzados.add(s2)
                frontera.append(_hijo(nodo, accion, s2))
                r.nodos_generados += 1
    return r


# --------------------------------------------------------------------- DFS
def dfs(problema: MisionerosCanibales, registrar_orden: bool = False) -> Resultado:
    """Búsqueda en profundidad: frontera LIFO (pila, lista de Python).

    Se usa la versión de grafo con conjunto de explorados: sin él, DFS entra en
    ciclos infinitos (p. ej. ir y volver con el mismo caníbal). Los hijos se
    apilan en orden inverso para que se exploren en el orden de `acciones`.
    """
    r = Resultado("DFS")
    frontera: list[Nodo] = [Nodo(problema.estado_inicial)]
    explorados: set[Estado] = set()

    while frontera:
        r.max_frontera = max(r.max_frontera, len(frontera))
        r.max_memoria = max(r.max_memoria, len(frontera) + len(explorados))
        nodo = frontera.pop()
        if nodo.estado in explorados:          # duplicado ya expandido
            continue
        if problema.es_objetivo(nodo.estado):
            r.solucion = nodo
            return r
        explorados.add(nodo.estado)
        r.nodos_expandidos += 1
        if registrar_orden:
            r.orden_expansion.append(nodo.estado)
        hijos = [
            _hijo(nodo, accion, s2)
            for accion, s2 in problema.sucesores(nodo.estado)
            if s2 not in explorados
        ]
        r.nodos_generados += len(hijos)
        frontera.extend(reversed(hijos))
    return r
