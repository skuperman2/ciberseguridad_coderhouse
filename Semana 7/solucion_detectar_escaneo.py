#!/usr/bin/env python3
"""Solución del desafío de la Semana 7: detectar un barrido de puertos en una captura.

Idea: un cliente normal habla con pocos puertos de un servidor; un escáner prueba MUCHOS puertos distintos
(y casi todos reciben RST). Contamos, por origen y destino, cuántos puertos distintos recibieron un SYN inicial.

Uso:  sudo tcpdump -nn -r captura.pcap | python3 solucion_detectar_escaneo.py [umbral]
"""
import re
import sys
from collections import defaultdict

# Línea típica de tcpdump -nn:  IP 10.20.0.10.53529 > 10.20.0.20.22: Flags [S], seq ...
PATRON = re.compile(r"IP (\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+): Flags \[S\],")


def detectar_escaneos(lineas, umbral=15):
    """Devuelve {(origen, destino): cantidad_de_puertos_distintos} para los pares que superan el umbral.

    Solo cuenta SYN "puros" (Flags [S]), es decir, intentos de abrir una conexión; los SYN/ACK de las respuestas
    llevan Flags [S.] y no entran en la cuenta.
    """
    puertos = defaultdict(set)
    for linea in lineas:
        m = PATRON.search(linea)
        if m:
            origen, _, destino, pdst = m.groups()
            puertos[(origen, destino)].add(int(pdst))
    return {par: len(p) for par, p in puertos.items() if len(p) >= umbral}


if __name__ == "__main__":
    umbral = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    hallazgos = detectar_escaneos(sys.stdin, umbral)
    if not hallazgos:
        print("Sin barridos de puertos (umbral:", umbral, "puertos distintos).")
    for (o, d), n in sorted(hallazgos.items(), key=lambda x: -x[1]):
        print(f"[!] POSIBLE ESCANEO: {o} probó {n} puertos distintos en {d}")
