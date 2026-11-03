"""Formulación del problema de los Misioneros y Caníbales.

Un problema de búsqueda se define por la tupla (S, s0, A, T, G):

* S  : conjunto de estados (m_izq, c_izq, b) con 0 <= m_izq, c_izq <= N, b en {0, 1}.
* s0 : estado inicial (N, N, 1): todos y el bote en la orilla izquierda.
* A  : acciones (m, c) = personas que viajan en el bote, 1 <= m + c <= K.
* T  : modelo de transición. Si el bote está a la izquierda (b = 1) las personas
       salen de la izquierda; si está a la derecha (b = 0) regresan a ella:
           T((M, C, 1), (m, c)) = (M - m, C - c, 0)
           T((M, C, 0), (m, c)) = (M + m, C + c, 1)
* G  : test objetivo, s == (0, 0, 0).

El costo de cada cruce es 1, por lo que el costo de un camino es su longitud.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Iterator, Tuple

Estado = Tuple[int, int, int]   # (misioneros_izq, canibales_izq, bote_izq)
Accion = Tuple[int, int]        # (misioneros en el bote, caníbales en el bote)


@dataclass(frozen=True)
class MisionerosCanibales:
    """Instancia generalizada: N misioneros, N caníbales y bote de capacidad K."""

    n: int = 3
    k: int = 2

    def __post_init__(self) -> None:
        if self.n < 1 or self.k < 1:
            raise ValueError("N y K deben ser enteros positivos")

    # ------------------------------------------------------------------ s0, G
    @property
    def estado_inicial(self) -> Estado:
        return (self.n, self.n, 1)

    @property
    def estado_objetivo(self) -> Estado:
        return (0, 0, 0)

    def es_objetivo(self, s: Estado) -> bool:
        return s == self.estado_objetivo

    # ----------------------------------------------------------------- A
    @cached_property
    def acciones(self) -> tuple[Accion, ...]:
        """Todas las cargas posibles del bote, 1 <= m + c <= K.

        Se ordenan priorizando mover más personas y, a igualdad, más misioneros.
        El orden no afecta a la optimalidad de BFS, pero sí determina el camino
        concreto que encuentra DFS.
        """
        cargas = [
            (m, c)
            for m in range(self.k + 1)
            for c in range(self.k + 1)
            if 1 <= m + c <= self.k
        ]
        return tuple(sorted(cargas, key=lambda a: (-(a[0] + a[1]), -a[0])))

    # ----------------------------------------------------------- restricciones
    def es_valido(self, s: Estado) -> bool:
        """Restricción de seguridad en ambas orillas.

        En cada orilla, si hay al menos un misionero, no puede haber más
        caníbales que misioneros.
        """
        m_izq, c_izq, b = s
        if not (0 <= m_izq <= self.n and 0 <= c_izq <= self.n and b in (0, 1)):
            return False
        m_der, c_der = self.n - m_izq, self.n - c_izq
        seguro_izq = m_izq == 0 or m_izq >= c_izq
        seguro_der = m_der == 0 or m_der >= c_der
        return seguro_izq and seguro_der

    # ------------------------------------------------------------------ T
    def resultado(self, s: Estado, a: Accion) -> Estado:
        """Modelo de transición T(s, a). No valida el estado resultante."""
        m_izq, c_izq, b = s
        m, c = a
        if b == 1:
            return (m_izq - m, c_izq - c, 0)
        return (m_izq + m, c_izq + c, 1)

    def es_aplicable(self, s: Estado, a: Accion) -> bool:
        """Precondición: deben existir esas personas en la orilla del bote."""
        m_izq, c_izq, b = s
        m, c = a
        if b == 1:
            return m <= m_izq and c <= c_izq
        return m <= self.n - m_izq and c <= self.n - c_izq

    def sucesores(self, s: Estado) -> Iterator[tuple[Accion, Estado]]:
        """Genera (acción, estado) aplicables cuyo resultado es válido.

        La poda se hace en la generación (propagación de la restricción):
        un estado inseguro nunca entra en la frontera.
        """
        for a in self.acciones:
            if self.es_aplicable(s, a):
                s2 = self.resultado(s, a)
                if self.es_valido(s2):
                    yield a, s2

    # --------------------------------------------------------- utilidades
    def estados_validos(self) -> list[Estado]:
        return [
            (m, c, b)
            for m in range(self.n + 1)
            for c in range(self.n + 1)
            for b in (0, 1)
            if self.es_valido((m, c, b))
        ]


def describir_accion(s: Estado, a: Accion) -> str:
    m, c = a
    sentido = "izq -> der" if s[2] == 1 else "der -> izq"
    partes = []
    if m:
        partes.append(f"{m} misionero{'s' if m > 1 else ''}")
    if c:
        partes.append(f"{c} caníbal{'es' if c > 1 else ''}")
    return f"Cruzan {' y '.join(partes)} ({sentido})"
