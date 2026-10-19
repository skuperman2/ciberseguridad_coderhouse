#!/usr/bin/env python3
"""Mide la entropía de Shannon de un archivo (en bits por byte, de 0 a 8).

Un texto normal da ~4,5; un archivo comprimido, ~7,9; un contenedor cifrado o
datos aleatorios, ~8,0 (indistinguible del ruido).

Uso: python3 entropia_archivo.py archivo [archivo ...]
"""
import collections
import math
import sys


def entropia(datos: bytes) -> float:
    if not datos:
        return 0.0
    n = len(datos)
    return -sum((c / n) * math.log2(c / n) for c in collections.Counter(datos).values())


def clasificar(e: float) -> str:
    if e < 6.0:
        return "texto o datos con estructura (legible / compresible)"
    if e < 7.9:
        return "datos densos (posiblemente comprimidos)"
    return "indistinguible de ruido aleatorio (cifrado o comprimido)"


if len(sys.argv) < 2:
    sys.exit(__doc__)

for ruta in sys.argv[1:]:
    with open(ruta, "rb") as f:
        datos = f.read()
    e = entropia(datos)
    print(f"{ruta}")
    print(f"   tamaño   : {len(datos):,} bytes")
    print(f"   primeros 16 bytes (hex): {datos[:16].hex(' ')}")
    print(f"   entropía : {e:.4f} bits/byte -> {clasificar(e)}")
