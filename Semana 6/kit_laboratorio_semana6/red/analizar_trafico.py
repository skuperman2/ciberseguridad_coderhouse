#!/usr/bin/env python3
"""Resumen de una captura de tráfico (pcap) desde el punto de vista de quien espía la red.

Uso: python3 analizar_trafico.py captura.pcap

Busca tres cosas:
  * HTTP en claro  : pedidos GET/POST, el sitio (Host) y, si hay formulario, USUARIO Y CLAVE legibles.
  * TLS (HTTPS)    : qué ve el espía de una conexión cifrada (el nombre del sitio en el SNI, la versión), pero NO el contenido.
  * WireGuard (VPN): datagramas UDP al puerto 51820; todo lo demás va dentro del túnel y no se ve.
Equivalentes con tshark:
  tshark -r captura.pcap -Y "http.request"                          (HTTP)
  tshark -r captura.pcap -Y "tls.handshake.type==1" -T fields -e tls.handshake.extensions_server_name
  tshark -r captura.pcap -q -z conv,udp                             (conversaciones UDP)
"""
import collections
import sys
import warnings
from urllib.parse import parse_qs

warnings.filterwarnings("ignore")
from scapy.all import IP, TCP, UDP, Raw, rdpcap  # noqa: E402


def sni_de_client_hello(datos: bytes):
    """Extrae el SNI de un TLS ClientHello (si el paquete lo es). Devuelve (version_registro, sni) o None."""
    try:
        if len(datos) < 50 or datos[0] != 0x16 or datos[5] != 0x01:   # 0x16 = handshake, 0x01 = ClientHello
            return None
        pos = 9 + 2 + 32                                              # cabecera + versión + random
        pos += 1 + datos[pos]                                         # session id
        pos += 2 + int.from_bytes(datos[pos:pos + 2], "big")          # cipher suites
        pos += 1 + datos[pos]                                         # compresión
        fin = pos + 2 + int.from_bytes(datos[pos:pos + 2], "big")
        pos += 2
        while pos + 4 <= fin:
            tipo = int.from_bytes(datos[pos:pos + 2], "big")
            largo = int.from_bytes(datos[pos + 2:pos + 4], "big")
            if tipo == 0:                                             # server_name
                n = int.from_bytes(datos[pos + 7:pos + 9], "big")
                return datos[pos + 9:pos + 9 + n].decode("ascii", "replace")
            pos += 4 + largo
    except Exception:
        return None
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    paquetes = rdpcap(sys.argv[1])
    http, tls, wg = [], [], collections.Counter()
    for p in paquetes:
        if not p.haslayer(IP):
            continue
        if p.haslayer(UDP) and 51820 in (p[UDP].sport, p[UDP].dport):
            wg[(p[IP].src, p[IP].dst)] += 1
        if p.haslayer(TCP) and p.haslayer(Raw):
            datos = bytes(p[Raw].load)
            sni = sni_de_client_hello(datos)
            if sni:
                tls.append((p[IP].src, p[IP].dst, sni))
            elif datos.split(b" ", 1)[0] in (b"GET", b"POST", b"PUT", b"HEAD"):
                http.append((p[IP].src, p[IP].dst, datos))

    print(f"Paquetes leídos: {len(paquetes)}\n")
    print("== HTTP EN CLARO (cualquiera en la red lo lee)")
    if not http:
        print("   (ninguno)")
    for src, dst, datos in http:
        cabecera, _, cuerpo = datos.partition(b"\r\n\r\n")
        lineas = cabecera.decode("latin-1").split("\r\n")
        host = next((l.split(":", 1)[1].strip() for l in lineas if l.lower().startswith("host:")), "?")
        ua = next((l.split(":", 1)[1].strip() for l in lineas if l.lower().startswith("user-agent:")), "?")
        print(f"   {src} -> {dst}  {lineas[0]}  Host={host}  User-Agent={ua}")
        if cuerpo:
            campos = parse_qs(cuerpo.decode("latin-1"))
            for k, v in campos.items():
                print(f"      [!] DATO EXPUESTO: {k} = {v[0]}")

    print("\n== TLS / HTTPS (el contenido va cifrado)")
    if not tls:
        print("   (ninguno)")
    for src, dst, sni in tls:
        print(f"   {src} -> {dst}  ClientHello  nombre del sitio (SNI) visible: {sni}")
    if tls:
        print("   El espía ve A QUÉ SITIO te conectás, pero no la ruta, ni los formularios, ni las contraseñas.")

    print("\n== WireGuard (VPN)")
    if not wg:
        print("   (ninguno)")
    for (src, dst), n in wg.items():
        print(f"   {src} -> {dst}  UDP/51820  {n} datagramas cifrados")
    if wg:
        print("   El espía solo ve que hay una VPN contra ese servidor: no ve sitios ni contenido.")


if __name__ == "__main__":
    main()
