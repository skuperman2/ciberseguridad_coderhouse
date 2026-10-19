#!/usr/bin/env python3
"""Calcula la entropía teórica de una contraseña o de una frase de palabras.

Uso:
    python3 entropia.py "MiClave123"            # contraseña de caracteres
    python3 entropia.py --palabras 6            # frase con 6 palabras al azar (diceware)
    python3 entropia.py "MiClave123" --velocidad 1e10   # intentos por segundo del atacante
"""
import argparse
import math
import string

PALABRAS_DICEWARE = 7776  # lista EFF de 5 dados: 6^5 palabras


def tamano_alfabeto(clave):
    n = 0
    if any(c in string.ascii_lowercase for c in clave):
        n += 26
    if any(c in string.ascii_uppercase for c in clave):
        n += 26
    if any(c in string.digits for c in clave):
        n += 10
    if any(c in string.punctuation for c in clave):
        n += len(string.punctuation)  # 32
    if any(ord(c) > 127 for c in clave):
        n += 64  # estimación para letras acentuadas y otros símbolos
    return n


def formatear_tiempo(segundos):
    unidades = [("años", 31557600), ("días", 86400), ("horas", 3600), ("minutos", 60)]
    if segundos < 1:
        return "menos de 1 segundo"
    for nombre, valor in unidades:
        if segundos >= valor:
            q = segundos / valor
            if nombre == "años" and q >= 1e6:
                return f"{q:.2e} años"
            return f"{q:,.1f} {nombre}"
    return f"{segundos:.1f} segundos"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clave", nargs="?", help="contraseña a evaluar")
    ap.add_argument("--palabras", type=int, help="cantidad de palabras de una frase diceware")
    ap.add_argument("--velocidad", type=float, default=1e10, help="intentos por segundo del atacante (por defecto 1e10)")
    a = ap.parse_args()

    if a.palabras:
        bits = a.palabras * math.log2(PALABRAS_DICEWARE)
        detalle = f"{a.palabras} palabras x log2({PALABRAS_DICEWARE}) = {a.palabras} x {math.log2(PALABRAS_DICEWARE):.2f}"
    elif a.clave:
        n = tamano_alfabeto(a.clave)
        bits = len(a.clave) * math.log2(n)
        detalle = f"{len(a.clave)} caracteres x log2({n}) = {len(a.clave)} x {math.log2(n):.2f}"
    else:
        ap.error("indicá una contraseña o --palabras N")

    combinaciones = 2 ** bits
    # En promedio el atacante encuentra la clave a mitad del espacio de búsqueda
    segundos = combinaciones / 2 / a.velocidad
    print(f"Cálculo           : {detalle}")
    print(f"Entropía          : {bits:.1f} bits")
    print(f"Combinaciones     : {combinaciones:.3e}")
    print(f"Velocidad atacante: {a.velocidad:.1e} intentos/s")
    print(f"Tiempo promedio   : {formatear_tiempo(segundos)}")
    print("Aviso: es un máximo teórico. Si la clave es una palabra común o sigue un patrón, el atacante la encuentra mucho antes.")


if __name__ == "__main__":
    main()
