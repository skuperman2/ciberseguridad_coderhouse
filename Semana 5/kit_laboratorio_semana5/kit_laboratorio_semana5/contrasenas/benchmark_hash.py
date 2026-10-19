#!/usr/bin/env python3
"""Mide cuántos intentos por segundo permite cada forma de guardar una contraseña.

Compara un hash rápido (SHA-256) con funciones diseñadas para ser lentas
(PBKDF2 y scrypt), que son las que usan los gestores de contraseñas.
"""
import hashlib
import os
import time

CLAVE = b"MiClaveDePrueba"
SAL = os.urandom(16)


def medir(nombre, funcion, segundos=2.0):
    n = 0
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < segundos:
        funcion()
        n += 1
    dt = time.perf_counter() - t0
    tasa = n / dt
    print(f"{nombre:34} {tasa:>14,.1f} intentos/s   ({1000 / tasa:,.3f} ms por intento)")
    return tasa


print("Midiendo durante ~2 s cada método (en esta máquina, con 1 núcleo)...\n")
r1 = medir("SHA-256 simple", lambda: hashlib.sha256(CLAVE).digest())
r2 = medir("PBKDF2-SHA256, 100.000 iteraciones", lambda: hashlib.pbkdf2_hmac("sha256", CLAVE, SAL, 100_000))
r3 = medir("PBKDF2-SHA256, 600.000 iteraciones", lambda: hashlib.pbkdf2_hmac("sha256", CLAVE, SAL, 600_000))
r4 = medir("scrypt (n=2^14, r=8, p=1)", lambda: hashlib.scrypt(CLAVE, salt=SAL, n=2**14, r=8, p=1))

print()
print(f"SHA-256 es {r1 / r3:,.0f} veces más rápido de atacar que PBKDF2 con 600.000 iteraciones.")
print(f"SHA-256 es {r1 / r4:,.0f} veces más rápido de atacar que scrypt.")
print("Eso es lo que compra una función lenta: cada intento del atacante cuesta lo mismo que cuesta a quien inicia sesión.")
