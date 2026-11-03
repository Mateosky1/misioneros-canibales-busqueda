import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.problema import MisionerosCanibales  # noqa: E402


class TestFormulacion(unittest.TestCase):
    def setUp(self):
        self.p = MisionerosCanibales(3, 2)

    def test_estados_inicial_y_objetivo(self):
        self.assertEqual(self.p.estado_inicial, (3, 3, 1))
        self.assertTrue(self.p.es_objetivo((0, 0, 0)))
        self.assertFalse(self.p.es_objetivo((0, 0, 1)))

    def test_acciones_capacidad_dos(self):
        self.assertEqual(set(self.p.acciones), {(2, 0), (1, 1), (0, 2), (1, 0), (0, 1)})

    def test_validez(self):
        self.assertTrue(self.p.es_valido((3, 3, 1)))
        self.assertTrue(self.p.es_valido((0, 3, 1)))   # sin misioneros a la izq
        self.assertFalse(self.p.es_valido((1, 2, 1)))  # 1M < 2C a la izquierda
        self.assertFalse(self.p.es_valido((2, 1, 0)))  # a la derecha 1M < 2C

    def test_transicion(self):
        self.assertEqual(self.p.resultado((3, 3, 1), (1, 1)), (2, 2, 0))
        self.assertEqual(self.p.resultado((2, 2, 0), (1, 0)), (3, 2, 1))

    def test_sucesores_iniciales(self):
        hijos = {s for _, s in self.p.sucesores((3, 3, 1))}
        # (3,1,0), (2,2,0), (3,2,0); (1,3,0) y (2,3,0) son inseguros
        self.assertEqual(hijos, {(3, 1, 0), (2, 2, 0), (3, 2, 0)})

    def test_espacio_de_estados(self):
        # 10 pares (m, c) seguros x 2 posiciones del bote = 20 estados válidos
        self.assertEqual(len(self.p.estados_validos()), 20)


if __name__ == "__main__":
    unittest.main()
