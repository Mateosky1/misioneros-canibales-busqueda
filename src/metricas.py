"""Métricas teóricas auxiliares."""

from __future__ import annotations


def factor_ramificacion_efectivo(nodos: int, profundidad: int, tol: float = 1e-9) -> float:
    """Resuelve N + 1 = 1 + b* + b*^2 + ... + b*^d por bisección (Russell & Norvig).

    `nodos` es N, el número de nodos generados, y `profundidad` es d, la
    longitud de la solución encontrada.
    """
    if profundidad <= 0 or nodos <= 0:
        return 0.0
    if nodos == profundidad:          # camino sin ramificación
        return 1.0

    def total(b: float) -> float:
        return sum(b ** i for i in range(profundidad + 1))

    # Como N >= d, b* >= 1; se acota superiormente duplicando hasta superar N+1.
    lo, hi = 1.0, 2.0
    while total(hi) < nodos + 1:
        lo, hi = hi, hi * 2
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if total(mid) < nodos + 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def factor_ramificacion_promedio(nodos_generados: int, nodos_expandidos: int) -> float:
    """Número medio de hijos nuevos generados por nodo expandido."""
    return nodos_generados / nodos_expandidos if nodos_expandidos else 0.0
