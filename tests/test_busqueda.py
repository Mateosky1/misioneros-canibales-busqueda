import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.busqueda import astar, bfs, bfs_arbol, dfs, dfs_arbol, heuristica_relajada  # noqa: E402
from src.problema import MisionerosCanibales  # noqa: E402


def es_camino_valido(p, res):
    estados = res.estados
    if estados[0] != p.estado_inicial or not p.es_objetivo(estados[-1]):
        return False
    for (s, a), s2 in zip(res.acciones, estados[1:]):
        if not (p.es_aplicable(s, a) and p.resultado(s, a) == s2 and p.es_valido(s2)):
            return False
    return True


class TestBFS(unittest.TestCase):
    def test_bfs_clasico_optimo(self):
        p = MisionerosCanibales(3, 2)
        r = bfs(p)
        self.assertTrue(r.encontrada)
        self.assertEqual(r.longitud, 11)
        self.assertTrue(es_camino_valido(p, r))

    def test_sin_solucion(self):
        # Con K = 2 el problema no tiene solución para N >= 4
        r = bfs(MisionerosCanibales(4, 2))
        self.assertFalse(r.encontrada)


class TestDFS(unittest.TestCase):
    def test_dfs_encuentra_camino_valido(self):
        p = MisionerosCanibales(3, 2)
        r = dfs(p)
        self.assertTrue(r.encontrada)
        self.assertTrue(es_camino_valido(p, r))
        self.assertGreaterEqual(r.longitud, bfs(p).longitud)

    def test_dfs_no_cicla_sin_solucion(self):
        self.assertFalse(dfs(MisionerosCanibales(4, 2)).encontrada)


class TestArbol(unittest.TestCase):
    def test_bfs_arbol_mismo_optimo_mas_memoria(self):
        p = MisionerosCanibales(3, 2)
        g, a = bfs(p), bfs_arbol(p)
        self.assertEqual(a.longitud, g.longitud)
        self.assertGreater(a.max_frontera, 100 * g.max_frontera)

    def test_dfs_arbol_valido(self):
        p = MisionerosCanibales(3, 2)
        self.assertTrue(es_camino_valido(p, dfs_arbol(p)))


class TestAStar(unittest.TestCase):
    INSTANCIAS = [(3, 2), (5, 3), (10, 4), (30, 5)]

    def test_optimo_igual_a_bfs(self):
        for n, k in self.INSTANCIAS:
            p = MisionerosCanibales(n, k)
            a, b = astar(p), bfs(p)
            self.assertEqual(a.longitud, b.longitud, (n, k))
            self.assertTrue(es_camino_valido(p, a))
            self.assertLessEqual(a.nodos_expandidos, b.nodos_expandidos)

    def test_heuristica_admisible_y_consistente(self):
        for n, k in self.INSTANCIAS:
            p = MisionerosCanibales(n, k)
            # Consistencia h(s) <= c(s, a, s') + h(s') en toda arista, junto con
            # h(objetivo) = 0, implica admisibilidad.
            for s in p.estados_validos():
                h = heuristica_relajada(p, s)
                for _, s2 in p.sucesores(s):
                    self.assertLessEqual(h, 1 + heuristica_relajada(p, s2))
            self.assertEqual(heuristica_relajada(p, (0, 0, 0)), 0)


if __name__ == "__main__":
    unittest.main()
