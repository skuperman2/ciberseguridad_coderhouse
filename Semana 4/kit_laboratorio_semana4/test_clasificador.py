#!/usr/bin/env python3
import unittest
from clasificador_malware import clasificar_malware


class TestClasificador(unittest.TestCase):
    def test_ransomware(self):
        self.assertEqual(clasificar_malware("Cifra los archivos y pide un rescate en Bitcoin"), "ransomware")

    def test_spyware(self):
        self.assertEqual(clasificar_malware("Registra cada tecla que presiona el usuario"), "spyware")
        self.assertEqual(clasificar_malware("Un KEYLOGGER instalado con un crack"), "spyware")

    def test_rat(self):
        self.assertEqual(clasificar_malware("Permite el control remoto del equipo y activa la cámara"), "rat")

    def test_desconocido(self):
        self.assertEqual(clasificar_malware("Muestra publicidad en el navegador"), "desconocido")

    def test_mayusculas(self):
        self.assertEqual(clasificar_malware("PIDE RESCATE"), "ransomware")


if __name__ == "__main__":
    unittest.main(verbosity=2)
