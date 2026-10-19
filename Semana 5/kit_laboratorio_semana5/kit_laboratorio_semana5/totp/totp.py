#!/usr/bin/env python3
"""Generador y verificador de códigos TOTP (RFC 6238) escrito desde cero.

Uso:
    python3 totp.py JBSWY3DPEHPK3PXP                 # código actual (secreto en base32)
    python3 totp.py JBSWY3DPEHPK3PXP --verificar 123456
    python3 totp.py JBSWY3DPEHPK3PXP --en 1700000000 # código para un instante dado (segundos Unix)
"""
import argparse
import base64
import hashlib
import hmac
import struct
import time


def hotp(secreto: bytes, contador: int, digitos: int = 6, algoritmo=hashlib.sha1) -> str:
    """HOTP (RFC 4226): código a partir de un secreto y un contador."""
    mensaje = struct.pack(">Q", contador)                 # contador como entero de 8 bytes
    mac = hmac.new(secreto, mensaje, algoritmo).digest()  # HMAC del contador
    desplazamiento = mac[-1] & 0x0F                       # 4 bits finales: dónde cortar
    truncado = struct.unpack(">I", mac[desplazamiento:desplazamiento + 4])[0] & 0x7FFFFFFF
    return str(truncado % (10 ** digitos)).zfill(digitos)


def totp(secreto: bytes, instante=None, paso: int = 30, digitos: int = 6, algoritmo=hashlib.sha1) -> str:
    """TOTP (RFC 6238): el contador es el número de 'pasos' de 30 s desde 1970."""
    t = time.time() if instante is None else instante
    return hotp(secreto, int(t // paso), digitos, algoritmo)


def secreto_desde_base32(texto: str) -> bytes:
    texto = texto.replace(" ", "").upper()
    texto += "=" * (-len(texto) % 8)  # relleno base32
    return base64.b32decode(texto)


def verificar(secreto: bytes, codigo: str, ventana: int = 1, instante=None) -> bool:
    """Acepta el código del paso actual y +/- `ventana` pasos (tolera relojes desfasados)."""
    t = time.time() if instante is None else instante
    for desfase in range(-ventana, ventana + 1):
        if hmac.compare_digest(totp(secreto, t + desfase * 30), codigo):
            return True
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("secreto", help="secreto en base32")
    ap.add_argument("--verificar", metavar="CODIGO")
    ap.add_argument("--en", type=float, metavar="UNIX", help="instante en segundos Unix")
    a = ap.parse_args()
    s = secreto_desde_base32(a.secreto)
    t = a.en if a.en is not None else time.time()
    if a.verificar:
        print("VÁLIDO" if verificar(s, a.verificar, instante=t) else "INVÁLIDO")
    else:
        restante = 30 - int(t % 30)
        print(f"{totp(s, t)}   (cambia en {restante} s)")
