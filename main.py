"""Resuelve el problema de Misioneros y Caníbales e imprime la secuencia de acciones.

Ejemplos:
    python3 main.py                      # BFS y DFS en la instancia clásica
    python3 main.py --algoritmo astar
    python3 main.py -n 5 -k 3 --algoritmo dfs
"""

from __future__ import annotations

import argparse
import time

from src.busqueda import ALGORITMOS
from src.metricas import factor_ramificacion_efectivo
from src.problema import MisionerosCanibales, describir_accion


def orillas(p: MisionerosCanibales, s) -> str:
    m, c, b = s
    izq = "M" * m + "C" * c
    der = "M" * (p.n - m) + "C" * (p.n - c)
    bote_i, bote_d = ("[B]", "   ") if b else ("   ", "[B]")
    return f"{izq:>{2 * p.n}} {bote_i} ~~~~ {bote_d} {der:<{2 * p.n}}"


def resolver(p: MisionerosCanibales, nombre: str) -> None:
    t0 = time.perf_counter()
    r = ALGORITMOS[nombre](p)
    dt = time.perf_counter() - t0
    print(f"\n=== {r.algoritmo}  (N={p.n}, K={p.k}) ===")
    if not r.encontrada:
        print(f"Sin solución. Nodos expandidos: {r.nodos_expandidos}")
        return
    print(f"  0. {r.estados[0]}  {orillas(p, r.estados[0])}")
    for i, ((s, a), s2) in enumerate(zip(r.acciones, r.estados[1:]), start=1):
        print(f"{i:3d}. {s2}  {orillas(p, s2)}   <- {describir_accion(s, a)}")
    b = factor_ramificacion_efectivo(r.nodos_generados, r.longitud)
    print(
        f"Longitud: {r.longitud} | expandidos: {r.nodos_expandidos} | "
        f"generados: {r.nodos_generados} | memoria máx.: {r.max_memoria} nodos | "
        f"b*: {b:.3f} | tiempo: {dt:.6f} s"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, default=3, help="misioneros = caníbales (por defecto 3)")
    ap.add_argument("-k", type=int, default=2, help="capacidad del bote (por defecto 2)")
    ap.add_argument("--algoritmo", choices=[*ALGORITMOS, "ambos"], default="ambos")
    args = ap.parse_args()

    p = MisionerosCanibales(args.n, args.k)
    nombres = ["bfs", "dfs"] if args.algoritmo == "ambos" else [args.algoritmo]
    for nombre in nombres:
        resolver(p, nombre)


if __name__ == "__main__":
    main()
