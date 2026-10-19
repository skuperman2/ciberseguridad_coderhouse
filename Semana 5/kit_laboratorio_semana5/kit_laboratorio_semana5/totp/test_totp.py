#!/usr/bin/env python3
"""Pruebas de totp.py con los vectores oficiales del RFC 6238 (apéndice B)."""
import hashlib
import unittest

from totp import hotp, totp, verificar

# Secreto de prueba del RFC 6238 para SHA-1: ASCII "12345678901234567890"
SECRETO = b"12345678901234567890"


class TestTOTP(unittest.TestCase):
    def test_vectores_rfc_6238_sha1_8_digitos(self):
        casos = {59: "94287082", 1111111109: "07081804", 1111111111: "14050471",
                 1234567890: "89005924", 2000000000: "69279037", 20000000000: "65353130"}
        for t, esperado in casos.items():
            self.assertEqual(totp(SECRETO, t, digitos=8), esperado, f"fallo en t={t}")

    def test_vectores_rfc_4226_hotp(self):
        esperados = ["755224", "287082", "359152", "969429", "338314", "254676", "287922", "162583", "399871", "520489"]
        for contador, esperado in enumerate(esperados):
            self.assertEqual(hotp(SECRETO, contador), esperado)

    def test_ventana_de_tolerancia(self):
        t = 1_700_000_000
        codigo = totp(SECRETO, t)
        self.assertTrue(verificar(SECRETO, codigo, instante=t))
        self.assertTrue(verificar(SECRETO, codigo, instante=t + 30))   # un paso después: aceptado
        self.assertFalse(verificar(SECRETO, codigo, instante=t + 120))  # cuatro pasos: rechazado

    def test_codigo_de_6_digitos(self):
        self.assertEqual(len(totp(SECRETO, 59)), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
