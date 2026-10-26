#!/usr/bin/env python3
"""Analiza una captura Wi-Fi (802.11) buscando señales de una red gemela maligna (evil twin) y de ataques de desautenticación.

Uso: python3 analizar_wifi.py cafe_wifi.pcap

Qué hace:
  1. Lista las redes que anuncian balizas (beacon): SSID, BSSID (MAC del punto de acceso), canal y si anuncian cifrado.
  2. Marca como SOSPECHOSO un SSID que aparece con más de un BSSID, sobre todo si uno es abierto y el otro protegido.
  3. Cuenta tramas de desautenticación por origen: una ráfaga alta es un intento de expulsar al cliente.
  4. Cuenta los mensajes EAPOL (apretón de manos WPA2).
Equivalente con tshark:  tshark -r cafe_wifi.pcap -Y "wlan.fc.type_subtype==8"
"""
import collections
import sys
import warnings

warnings.filterwarnings("ignore")
from scapy.all import Dot11, Dot11Beacon, Dot11Deauth, Dot11Elt, EAPOL, rdpcap  # noqa: E402

UMBRAL_DESAUTH = 10  # más de 10 desautenticaciones desde un mismo origen se considera ráfaga


def leer_beacon(p):
    ssid, canal, rsn = "", None, False
    elt = p.getlayer(Dot11Elt)
    while elt is not None and isinstance(elt, Dot11Elt):
        if elt.ID == 0:
            ssid = elt.info.decode("utf-8", "replace")
        elif elt.ID == 3 and elt.info:
            canal = elt.info[0]
        elif elt.ID == 48:
            rsn = True
        elt = elt.payload.getlayer(Dot11Elt)
    privacidad = bool(p[Dot11Beacon].cap & 0x10)
    return ssid, canal, rsn, privacidad


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    paquetes = rdpcap(sys.argv[1])
    redes = {}
    deauth = collections.Counter()
    eapol = 0
    for p in paquetes:
        if p.haslayer(Dot11Beacon):
            ssid, canal, rsn, priv = leer_beacon(p)
            redes[(ssid, p[Dot11].addr2)] = (canal, "WPA2/RSN" if rsn else ("WEP/privado" if priv else "ABIERTA"))
        elif p.haslayer(Dot11Deauth):
            deauth[p[Dot11].addr2] += 1
        if p.haslayer(EAPOL):
            eapol += 1

    print(f"Tramas leídas: {len(paquetes)}\n")
    print("REDES ANUNCIADAS")
    print(f"  {'SSID':22} {'BSSID':19} {'Canal':>5}  Seguridad")
    for (ssid, bssid), (canal, seg) in sorted(redes.items()):
        print(f"  {ssid:22} {bssid:19} {str(canal):>5}  {seg}")

    print("\nSOSPECHAS")
    por_ssid = collections.defaultdict(list)
    for (ssid, bssid), (canal, seg) in redes.items():
        por_ssid[ssid].append((bssid, canal, seg))
    hubo = False
    for ssid, lista in por_ssid.items():
        if len(lista) > 1:
            seguridades = {seg for _, _, seg in lista}
            hubo = True
            print(f"  [!] El SSID '{ssid}' lo anuncian {len(lista)} puntos de acceso distintos:")
            for bssid, canal, seg in lista:
                print(f"        {bssid}  canal {canal}  {seg}")
            if len(seguridades) > 1:
                print("      -> Misma red, distinta seguridad: señal clásica de RED GEMELA MALIGNA (evil twin).")
    for origen, n in deauth.items():
        if n > UMBRAL_DESAUTH:
            hubo = True
            print(f"  [!] {n} tramas de desautenticación desde {origen}: ráfaga para expulsar clientes (deauth flood).")
    if not hubo:
        print("  Sin hallazgos.")
    print(f"\nMensajes EAPOL (apretón de manos WPA2): {eapol}")


if __name__ == "__main__":
    main()
