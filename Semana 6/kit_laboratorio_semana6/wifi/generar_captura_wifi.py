#!/usr/bin/env python3
"""Genera una captura Wi-Fi (802.11) FICTICIA para practicar el análisis forense de una cafetería.

Una VM sin adaptador Wi-Fi no puede capturar aire real, así que este script fabrica con Scapy una captura
con el aspecto que tendría. Escenario inventado (todo ficticio, direcciones MAC de ejemplo):

  * "CafeNova_Gratis"  legítima  : BSSID aa:bb:cc:00:00:01, canal 6,  protegida con WPA2 (RSN)
  * "CafeNova_Gratis"  gemela    : BSSID de:ad:be:ef:00:66, canal 11, ABIERTA (sin cifrado)   <- evil twin
  * "Libreria_WiFi" y "Taller_Mecanico_5G": redes vecinas normales
  * Una ráfaga de tramas de DESAUTENTICACIÓN falsificadas con la MAC de la red legítima hacia un cliente
  * Un apretón de manos WPA2 (4 mensajes EAPOL) de un cliente con la red legítima

Uso: python3 generar_captura_wifi.py [salida.pcap]
"""
import sys
import warnings

warnings.filterwarnings("ignore")
from scapy.all import (Dot11, Dot11Beacon, Dot11Deauth, Dot11Elt, EAPOL, LLC, RadioTap, SNAP, Raw, wrpcap)
from scapy.layers.dot11 import Dot11Auth

SALIDA = sys.argv[1] if len(sys.argv) > 1 else "cafe_wifi.pcap"

LEGIT = "aa:bb:cc:00:00:01"
GEMELA = "de:ad:be:ef:00:66"
CLIENTE = "11:22:33:44:55:66"
BROADCAST = "ff:ff:ff:ff:ff:ff"


def rsn_wpa2():
    """Elemento RSN mínimo: grupo CCMP, par CCMP, autenticación PSK (WPA2-Personal)."""
    datos = (b"\x01\x00" b"\x00\x0f\xac\x04" b"\x01\x00" b"\x00\x0f\xac\x04" b"\x01\x00" b"\x00\x0f\xac\x02" b"\x00\x00")
    return Dot11Elt(ID=48, info=datos)


def beacon(bssid, ssid, canal, protegida, t):
    cap = "ESS+privacy" if protegida else "ESS"
    trama = RadioTap() / Dot11(
        type=0, subtype=8, addr1=BROADCAST, addr2=bssid, addr3=bssid
    ) / Dot11Beacon(cap=cap, beacon_interval=100) / Dot11Elt(ID=0, info=ssid.encode()) \
        / Dot11Elt(ID=3, info=bytes([canal]))
    if protegida:
        trama = trama / rsn_wpa2()
    trama.time = t
    return trama


def main():
    paquetes = []
    t = 1000.0
    redes = [
        (LEGIT, "CafeNova_Gratis", 6, True),
        (GEMELA, "CafeNova_Gratis", 11, False),
        ("aa:bb:cc:00:00:02", "Libreria_WiFi", 1, True),
        ("aa:bb:cc:00:00:03", "Taller_Mecanico_5G", 6, True),
    ]
    for i in range(10):                        # ~1 segundo de balizas
        for bssid, ssid, canal, prot in redes:
            paquetes.append(beacon(bssid, ssid, canal, prot, t))
            t += 0.01

    # Apretón de manos WPA2 del cliente con la red legítima (4 mensajes EAPOL, simplificados)
    for n, (origen, destino) in enumerate([(LEGIT, CLIENTE), (CLIENTE, LEGIT), (LEGIT, CLIENTE), (CLIENTE, LEGIT)], 1):
        p = RadioTap() / Dot11(type=2, subtype=0, addr1=destino, addr2=origen, addr3=LEGIT, FCfield="from-DS" if origen == LEGIT else "to-DS") \
            / LLC(dsap=0xAA, ssap=0xAA, ctrl=3) / SNAP(OUI=0, code=0x888E) / EAPOL(version=2, type=3) \
            / Raw(bytes([n]) * 8)
        p.time = t
        paquetes.append(p)
        t += 0.005

    # Ráfaga de desautenticación falsificada: "la red legítima te expulsa" (reason 7), 60 tramas
    for _ in range(60):
        p = RadioTap() / Dot11(type=0, subtype=12, addr1=CLIENTE, addr2=LEGIT, addr3=LEGIT) / Dot11Deauth(reason=7)
        p.time = t
        paquetes.append(p)
        t += 0.002

    # El cliente, sin su red legítima, se asocia a la gemela (abierta): autenticación abierta
    p = RadioTap() / Dot11(type=0, subtype=11, addr1=GEMELA, addr2=CLIENTE, addr3=GEMELA) / Dot11Auth(algo=0, seqnum=1, status=0)
    p.time = t
    paquetes.append(p)

    wrpcap(SALIDA, paquetes)
    print(f"Captura generada: {SALIDA}  ({len(paquetes)} tramas)")


if __name__ == "__main__":
    main()
