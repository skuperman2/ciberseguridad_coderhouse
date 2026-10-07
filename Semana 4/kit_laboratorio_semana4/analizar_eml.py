#!/usr/bin/env python3
"""Muestra las cabeceras y enlaces mas importantes de un correo .eml.
Uso: python3 analizar_eml.py correos/correo_A.eml
"""
import re
import sys
from email import policy
from email.parser import BytesParser

CAMPOS = ["From", "Reply-To", "Return-Path", "To", "Subject", "Date"]


def dominio(valor):
    m = re.search(r"@([\w.-]+)", valor or "")
    return m.group(1).lower() if m else None


def main(ruta):
    with open(ruta, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    print(f"=== {ruta} ===")
    for campo in CAMPOS:
        print(f"{campo:12}: {msg.get(campo, '(no presente)')}")

    print("\n-- Cabeceras Received (de abajo hacia arriba = recorrido real) --")
    for r in reversed(msg.get_all("Received", [])):
        print(" ", " ".join(str(r).split()))

    print("\n-- Autenticacion --")
    auth = " ".join(str(msg.get("Authentication-Results", "(no presente)")).split())
    for clave in ("spf", "dkim", "dmarc"):
        m = re.search(rf"{clave}=(\w+)", auth)
        print(f"{clave.upper():6}: {m.group(1) if m else 'no informado'}")

    print("\n-- Dominios involucrados --")
    doms = {
        "From": dominio(msg.get("From")),
        "Reply-To": dominio(msg.get("Reply-To")),
        "Return-Path": dominio(msg.get("Return-Path")),
    }
    for k, v in doms.items():
        print(f"{k:12}: {v or '(no presente)'}")
    distintos = {v for v in doms.values() if v}
    print(f"Dominios distintos: {len(distintos)}")

    print("\n-- Enlaces (texto visible -> destino real) --")
    cuerpo = msg.get_body(preferencelist=("html", "plain"))
    texto = cuerpo.get_content() if cuerpo else ""
    enlaces = re.findall(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', texto, re.S)
    if not enlaces:
        print("(sin enlaces HTML)")
    for destino, visible in enlaces:
        alerta = "  <-- NO COINCIDEN" if dominio("@" + re.sub(r"^https?://", "", visible).split("/")[0]) != dominio("@" + re.sub(r"^https?://", "", destino).split("/")[0]) else ""
        print(f"visible: {visible}\n destino: {destino}{alerta}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
