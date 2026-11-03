import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.busqueda import bfs  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
