"""Benchmarking empírico de BFS, DFS y A* en Misioneros y Caníbales.

Experimentos:
  E1  Instancia clásica (N=3, K=2): búsquedas de grafo y de árbol.
  E2  Sensibilidad de DFS al orden de las acciones (todas las permutaciones).
  E3  Escalabilidad con N y K (búsquedas de grafo).

Los tiempos son la mediana de R repeticiones con time.perf_counter(); la
memoria en bytes es el pico medido con tracemalloc en una ejecución aparte
(para no contaminar el tiempo). Salida: resultados/*.csv, resultados.json y
tablas LaTeX en resultados/tablas/.

    python3 benchmark.py            # todo
    python3 benchmark.py --rapido   # menos repeticiones
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
import platform
import statistics
import sys
import time
import tracemalloc
from collections import Counter

from src.busqueda import astar, bfs, bfs_arbol, dfs, dfs_arbol
from src.metricas import factor_ramificacion_efectivo, factor_ramificacion_promedio
from src.problema import MisionerosCanibales

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


def alcanzables(p: MisionerosCanibales) -> int:
    vistos, pila = {p.estado_inicial}, [p.estado_inicial]
    while pila:
        s = pila.pop()
        for _, s2 in p.sucesores(s):
            if s2 not in vistos:
                vistos.add(s2)
                pila.append(s2)
    return len(vistos)


def medir(fn, p: MisionerosCanibales, repeticiones: int) -> dict:
    r = fn(p)
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        fn(p)
        tiempos.append(time.perf_counter() - t0)
    tracemalloc.start()
    fn(p)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    d = r.longitud
    return {
        "algoritmo": r.algoritmo,
        "N": p.n,
        "K": p.k,
        "solucion": r.encontrada,
        "longitud": d,
        "expandidos": r.nodos_expandidos,
        "generados": r.nodos_generados,
        "max_frontera": r.max_frontera,
        "max_memoria_nodos": r.max_memoria,
        "pico_bytes": pico,
        "tiempo_mediana_s": statistics.median(tiempos),
        "tiempo_desv_s": statistics.pstdev(tiempos) if len(tiempos) > 1 else 0.0,
        "repeticiones": repeticiones,
        "b_efectivo": factor_ramificacion_efectivo(r.nodos_generados, d) if d else None,
        "b_promedio": factor_ramificacion_promedio(r.nodos_generados, r.nodos_expandidos),
        "camino": r.estados,
    }


# ------------------------------------------------------------------ experimentos
def e1_clasica(rep: int) -> list[dict]:
    p = MisionerosCanibales(3, 2)
    filas = [medir(f, p, rep) for f in (bfs, dfs, astar)]
    filas += [medir(f, p, max(3, rep // 200)) for f in (bfs_arbol,)]
    filas += [medir(f, p, rep) for f in (dfs_arbol,)]
    return filas


def e2_ordenes(n: int, k: int) -> dict:
    p0 = MisionerosCanibales(n, k)
    longitudes, expandidos = Counter(), []
    for orden in itertools.permutations(p0.acciones):
        r = dfs(MisionerosCanibales(n, k, orden))
        longitudes[r.longitud] += 1
        expandidos.append(r.nodos_expandidos)
    optimo = bfs(p0).longitud
    return {
        "N": n,
        "K": k,
        "permutaciones": sum(longitudes.values()),
        "longitud_optima": optimo,
        "distribucion_longitudes": dict(sorted(longitudes.items())),
        "fraccion_optima": longitudes[optimo] / sum(longitudes.values()),
        "expandidos_min": min(expandidos),
        "expandidos_max": max(expandidos),
        "expandidos_media": statistics.mean(expandidos),
    }


INSTANCIAS_E3 = [(3, 2), (5, 3), (10, 4), (25, 4), (50, 5), (100, 5), (200, 6), (500, 6)]


def e3_escalabilidad(rep: int) -> list[dict]:
    filas = []
    for n, k in INSTANCIAS_E3:
        p = MisionerosCanibales(n, k)
        reps = max(5, rep // max(1, n // 5))
        for f in (bfs, dfs, astar):
            fila = medir(f, p, reps)
            fila["alcanzables"] = alcanzables(p)
            fila["validos"] = len(p.estados_validos())
            filas.append(fila)
    return filas


# ---------------------------------------------------------------- tablas LaTeX
def fmt_t(s: float) -> str:
    return f"{s * 1e3:.4f}"


def tabla_e1(filas: list[dict]) -> str:
    lineas = [
        r"\begin{tabular}{@{}lrrrrrrrr@{}}",
        r"\toprule",
        r"Algoritmo & Exp. & Gen. & $|F|_{\max}$ & Mem. (nodos) & Mem. (KiB) & Tiempo (ms) & $d$ & $b^*$ \\",
        r"\midrule",
    ]
    for i, f in enumerate(filas):
        if i == 3:
            lineas.append(r"\midrule")
        nombre = f["algoritmo"].replace("*", "$^*$").replace("-árbol", " (árbol)")
        lineas.append(
            f"{nombre} & {f['expandidos']:,} & {f['generados']:,} & {f['max_frontera']:,} & "
            f"{f['max_memoria_nodos']:,} & {f['pico_bytes'] / 1024:,.1f} & {fmt_t(f['tiempo_mediana_s'])} & "
            f"{f['longitud']} & {f['b_efectivo']:.3f} \\\\".replace(",", "\\,")
        )
    lineas += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lineas)


def tabla_principal(filas: list[dict]) -> str:
    """Tabla que pide el enunciado: expandidos, tiempo (s) y longitud."""
    lineas = [
        r"\begin{tabular}{@{}lrrr@{}}",
        r"\toprule",
        r"Algoritmo & Nodos expandidos & Tiempo de ejecución (s) & Longitud del camino \\",
        r"\midrule",
    ]
    for f in filas[:2]:
        lineas.append(
            f"{f['algoritmo']} (cola) & {f['expandidos']} & {f['tiempo_mediana_s']:.2e} & {f['longitud']} \\\\"
            if f["algoritmo"] == "BFS"
            else f"{f['algoritmo']} (pila) & {f['expandidos']} & {f['tiempo_mediana_s']:.2e} & {f['longitud']} \\\\"
        )
    lineas += [r"\bottomrule", r"\end{tabular}"]
    t = "\n".join(lineas)
    # 1.23e-05 -> $1.23\times10^{-5}$
    import re
    return re.sub(r"(\d\.\d+)e-0?(\d+)", r"$\1\\times10^{-\2}$", t)


def tabla_e3(filas: list[dict]) -> str:
    lineas = [
        r"\begin{tabular}{@{}rrr|rrr|rrr|rrr@{}}",
        r"\toprule",
        r" & & & \multicolumn{3}{c|}{BFS} & \multicolumn{3}{c|}{DFS} & \multicolumn{3}{c}{A$^*$} \\",
        r"$N$ & $K$ & $|S_r|$ & Exp. & $d$ & ms & Exp. & $d$ & ms & Exp. & $d$ & ms \\",
        r"\midrule",
    ]
    for i in range(0, len(filas), 3):
        b, d, a = filas[i : i + 3]
        lineas.append(
            f"{b['N']} & {b['K']} & {b['alcanzables']} & "
            + " & ".join(
                f"{x['expandidos']} & {x['longitud']} & {x['tiempo_mediana_s'] * 1e3:.3f}" for x in (b, d, a)
            )
            + r" \\"
        )
    lineas += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lineas)


def tabla_memoria(filas: list[dict]) -> str:
    lineas = [
        r"\begin{tabular}{@{}rr|rr|rr@{}}",
        r"\toprule",
        r" & & \multicolumn{2}{c|}{BFS} & \multicolumn{2}{c}{DFS} \\",
        r"$N$ & $K$ & $|F|_{\max}$ & Mem. (KiB) & $|F|_{\max}$ & Mem. (KiB) \\",
        r"\midrule",
    ]
    for i in range(0, len(filas), 3):
        b, d, _ = filas[i : i + 3]
        lineas.append(
            f"{b['N']} & {b['K']} & {b['max_frontera']} & {b['pico_bytes'] / 1024:.1f} & "
            f"{d['max_frontera']} & {d['pico_bytes'] / 1024:.1f} \\\\"
        )
    lineas += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lineas)


def guardar_csv(nombre: str, filas: list[dict]) -> None:
    campos = [c for c in filas[0] if c != "camino"]
    with open(os.path.join(SALIDA, nombre), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--repeticiones", type=int, default=2000)
    args = ap.parse_args()
    rep = 50 if args.rapido else args.repeticiones

    os.makedirs(os.path.join(SALIDA, "tablas"), exist_ok=True)
    entorno = {
        "python": sys.version.split()[0],
        "plataforma": platform.platform(),
        "procesador": platform.processor() or platform.machine(),
        "repeticiones": rep,
    }
    print("Entorno:", entorno)

    e1 = e1_clasica(rep)
    e2 = [e2_ordenes(3, 2), e2_ordenes(5, 3)]
    e3 = e3_escalabilidad(rep)

    print("\nE1 — Instancia clásica (N=3, K=2)")
    print(f"{'Algoritmo':<11}{'Exp':>8}{'Gen':>9}{'|F|max':>9}{'Mem(n)':>9}{'KiB':>9}{'t (s)':>12}{'d':>4}{'b*':>7}")
    for f in e1:
        print(
            f"{f['algoritmo']:<11}{f['expandidos']:>8}{f['generados']:>9}{f['max_frontera']:>9}"
            f"{f['max_memoria_nodos']:>9}{f['pico_bytes'] / 1024:>9.1f}{f['tiempo_mediana_s']:>12.2e}"
            f"{f['longitud']:>4}{f['b_efectivo']:>7.3f}"
        )
    print("\nE2 — DFS frente al orden de las acciones")
    for e in e2:
        print(e)
    print("\nE3 — Escalabilidad")
    for f in e3:
        print(
            f"N={f['N']:<4} K={f['K']} {f['algoritmo']:<4} |Sr|={f['alcanzables']:<5} exp={f['expandidos']:<5} "
            f"d={f['longitud']:<5} |F|max={f['max_frontera']:<5} t={f['tiempo_mediana_s']:.2e}s"
        )

    guardar_csv("e1_clasica.csv", e1)
    guardar_csv("e3_escalabilidad.csv", e3)
    with open(os.path.join(SALIDA, "resultados.json"), "w", encoding="utf-8") as fh:
        json.dump({"entorno": entorno, "e1": e1, "e2": e2, "e3": e3}, fh, indent=2, ensure_ascii=False)
    tablas = {
        "tabla_principal.tex": tabla_principal(e1),
        "tabla_e1.tex": tabla_e1(e1),
        "tabla_e3.tex": tabla_e3(e3),
        "tabla_memoria.tex": tabla_memoria(e3),
    }
    for nombre, contenido in tablas.items():
        with open(os.path.join(SALIDA, "tablas", nombre), "w", encoding="utf-8") as fh:
            fh.write(contenido + "\n")
    print(f"\nResultados guardados en {SALIDA}/")


if __name__ == "__main__":
    main()
