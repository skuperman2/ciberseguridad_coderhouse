#!/usr/bin/env python3
"""Calcula los intervalos entre conexiones y detecta beaconing.

Entrada: una columna de tiempos (segundos) por stdin, p. ej. la salida de
    tshark -r beacon.pcap -Y "..." -T fields -e frame.time_relative | python3 intervalos.py
"""
import statistics
import sys

tiempos = sorted(float(l.strip()) for l in sys.stdin if l.strip())
if len(tiempos) < 3:
    sys.exit("Se necesitan al menos 3 conexiones para calcular intervalos.")

intervalos = [round(b - a, 3) for a, b in zip(tiempos, tiempos[1:])]
media = statistics.mean(intervalos)
desvio = statistics.pstdev(intervalos)
coef = desvio / media if media else float("inf")

print("Conexiones:", len(tiempos))
print("Intervalos (s):", intervalos)
print(f"Media: {media:.2f} s | Desvío: {desvio:.2f} s | Coef. de variación: {coef:.2f}")
if coef < 0.15:
    print("=> MUY REGULAR: patrón típico de beaconing.")
elif coef < 0.5:
    print("=> Regularidad moderada: puede ser beaconing con jitter. Investigar.")
else:
    print("=> Irregular: más parecido a tráfico humano.")
