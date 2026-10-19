#!/usr/bin/env python3
"""Audita un archivo de hashes de un sistema ficticio (TiendaNova) con un diccionario.

Simula lo que hace un atacante que obtiene una base de datos de contraseñas SIN sal
y guardadas con SHA-256. Solo se usa sobre los datos ficticios del laboratorio.

Uso:
    python3 auditar_hashes.py hashes_tiendanova.txt diccionario_lab.txt
Formato de hashes: usuario:hash_sha256_en_hexadecimal
"""
import hashlib
import sys
import time

if len(sys.argv) != 3:
    sys.exit(__doc__)

ruta_hashes, ruta_dic = sys.argv[1], sys.argv[2]

usuarios = {}
with open(ruta_hashes, encoding="utf-8") as f:
    for linea in f:
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            usuario, h = linea.split(":", 1)
            usuarios[usuario] = h.lower()

with open(ruta_dic, encoding="utf-8") as f:
    palabras = [l.rstrip("\n") for l in f if l.strip()]

# Tabla precalculada: hash -> contraseña (se calcula UNA vez; sin sal sirve para todos los usuarios)
t0 = time.perf_counter()
tabla = {hashlib.sha256(p.encode()).hexdigest(): p for p in palabras}
dt = time.perf_counter() - t0

print(f"Usuarios a auditar : {len(usuarios)}")
print(f"Palabras en el diccionario: {len(palabras)}  (hasheadas en {dt * 1000:.1f} ms)\n")

rotas = 0
for usuario, h in usuarios.items():
    if h in tabla:
        rotas += 1
        print(f"[ROTA]  {usuario:12} contraseña = {tabla[h]}")
    else:
        print(f"[ok]    {usuario:12} no está en el diccionario")

print(f"\nResultado: {rotas} de {len(usuarios)} contraseñas recuperadas con un diccionario de {len(palabras)} palabras.")
print("Moraleja: un hash rápido y sin sal no protege contraseñas comunes ni repetidas.")
