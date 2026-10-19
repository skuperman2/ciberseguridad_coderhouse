#!/usr/bin/env python3
import unittest
from automatizar_veracrypt import comando_crear, comando_montar, comando_desmontar


class TestComandos(unittest.TestCase):
    def test_montar(self):
        c = comando_montar("caja.hc", "/mnt/x", "secreta")
        self.assertEqual(c[0], "veracrypt")
        self.assertIn("--text", c)
        self.assertIn("--mount", c)
        self.assertIn("caja.hc", c)
        self.assertIn("/mnt/x", c)
        self.assertIn("--password=secreta", c)
        self.assertIn("--non-interactive", c)

    def test_desmontar(self):
        c = comando_desmontar("/mnt/x")
        self.assertEqual(c[0], "veracrypt")
        self.assertIn("--text", c)
        self.assertTrue("--unmount" in c or "--dismount" in c)
        self.assertIn("/mnt/x", c)

    def test_crear(self):
        c = comando_crear("caja.hc", 20, "secreta")
        self.assertEqual(c[0], "veracrypt")
        self.assertIn("--create", c)
        self.assertIn("caja.hc", c)
        self.assertIn("--size=20M", c)
        self.assertIn("--password=secreta", c)
        self.assertIn("--non-interactive", c)

    def test_las_listas_no_son_cadenas(self):
        # Una lista de argumentos evita problemas con espacios y con inyección de comandos
        self.assertIsInstance(comando_montar("a b.hc", "/mnt/x", "c"), list)
        self.assertIn("a b.hc", comando_montar("a b.hc", "/mnt/x", "c"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
