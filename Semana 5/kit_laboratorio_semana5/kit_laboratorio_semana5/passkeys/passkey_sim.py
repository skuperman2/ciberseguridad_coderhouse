#!/usr/bin/env python3
"""Simulador didáctico de passkeys (WebAuthn / FIDO2) con criptografía real.

Modela tres actores:
  * Autenticador : tu dispositivo. Guarda la llave PRIVADA y firma desafíos.
  * Servidor     : el sitio real. Guarda solo la llave PÚBLICA.
  * Atacante     : un sitio de phishing que intenta robar el inicio de sesión.

Es una versión simplificada de WebAuthn: conserva las ideas que importan
(par de llaves por sitio, desafío aleatorio, firma, vinculación con el dominio,
contador anti-clonación) sin las codificaciones binarias del estándar real.

Requiere: python3-cryptography (apt install python3-cryptography)
Uso:      python3 passkey_sim.py
"""
import base64
import hashlib
import json
import os
import struct
from urllib.parse import urlparse

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

SITIO_REAL = "https://tiendanova.test"
SITIO_FALSO = "https://tiendanova-login.test"  # dominio parecido (técnica de la Semana 4)


def b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


def rp_id_de(origen: str) -> str:
    """El navegador deriva el 'rpId' del dominio REAL de la página que estás mirando."""
    return urlparse(origen).hostname


def hex_corto(datos: bytes, n: int = 8) -> str:
    return datos.hex()[: n * 2] + "…"


class Autenticador:
    """Tu teléfono/laptop/llave. La llave privada NUNCA sale de acá."""

    def __init__(self):
        self._credenciales = {}  # rp_id -> {id, privada, contador}

    def crear_credencial(self, rp_id: str):
        privada = ec.generate_private_key(ec.SECP256R1())
        cred_id = os.urandom(16)
        self._credenciales[rp_id] = {"id": cred_id, "privada": privada, "contador": 0}
        publica = privada.public_key().public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
        )
        return cred_id, publica

    def firmar(self, rp_id: str, origen: str, desafio: bytes):
        cred = self._credenciales.get(rp_id)
        if cred is None:
            raise LookupError(f"el dispositivo no tiene ninguna passkey para '{rp_id}'")
        cred["contador"] += 1
        client_data = json.dumps(
            {"type": "webauthn.get", "challenge": b64(desafio), "origin": origen}, separators=(",", ":")
        ).encode()
        auth_data = hashlib.sha256(rp_id.encode()).digest() + b"\x05" + struct.pack(">I", cred["contador"])
        # flags 0x05 = usuario presente + usuario verificado (huella, cara o PIN)
        firma = cred["privada"].sign(auth_data + hashlib.sha256(client_data).digest(), ec.ECDSA(hashes.SHA256()))
        return {"cred_id": cred["id"], "auth_data": auth_data, "client_data": client_data, "firma": firma}


class Servidor:
    """El sitio real. Si te lo hackean, el atacante obtiene solo llaves públicas."""

    def __init__(self, origen: str):
        self.origen = origen
        self.rp_id = rp_id_de(origen)
        self.usuarios = {}      # usuario -> {cred_id, publica, contador}
        self._desafios = set()  # desafíos emitidos y todavía no usados

    def registrar(self, usuario, cred_id, publica_bytes):
        self.usuarios[usuario] = {"cred_id": cred_id, "publica": publica_bytes, "contador": 0}

    def nuevo_desafio(self) -> bytes:
        d = os.urandom(32)
        self._desafios.add(d)
        return d

    def verificar(self, usuario, resp):
        u = self.usuarios.get(usuario)
        if not u:
            return False, "usuario desconocido"
        cd = json.loads(resp["client_data"])
        desafio = base64.urlsafe_b64decode(cd["challenge"] + "=" * (-len(cd["challenge"]) % 4))
        if desafio not in self._desafios:
            return False, "el desafío no existe o ya fue usado (anti-repetición)"
        self._desafios.discard(desafio)  # un desafío sirve UNA sola vez
        if cd["type"] != "webauthn.get":
            return False, "tipo de operación incorrecto"
        if cd["origin"] != self.origen:
            return False, f"origen incorrecto: la firma es para '{cd['origin']}', no para '{self.origen}'"
        if resp["auth_data"][:32] != hashlib.sha256(self.rp_id.encode()).digest():
            return False, "la firma no está vinculada a este dominio"
        contador = struct.unpack(">I", resp["auth_data"][33:37])[0]
        if contador <= u["contador"]:
            return False, "contador no creciente (posible clonación del autenticador)"
        publica = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), u["publica"])
        try:
            publica.verify(resp["firma"], resp["auth_data"] + hashlib.sha256(resp["client_data"]).digest(), ec.ECDSA(hashes.SHA256()))
        except InvalidSignature:
            return False, "firma inválida"
        u["contador"] = contador
        return True, "firma válida"


def navegador_pide_firma(autenticador, pagina_actual, desafio):
    """El navegador fija origen y rpId según la página en la que estás. La página no puede mentir sobre eso."""
    return autenticador.firmar(rp_id_de(pagina_actual), pagina_actual, desafio)


def titulo(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


def main():
    telefono = Autenticador()
    servidor = Servidor(SITIO_REAL)

    titulo("1) REGISTRO: se crea el par de llaves para tiendanova.test")
    cred_id, publica = telefono.crear_credencial(servidor.rp_id)
    servidor.registrar("laura", cred_id, publica)
    print(f"Llave privada : queda en el dispositivo (nunca se envía)")
    print(f"Llave pública : {hex_corto(publica, 12)}  -> se guarda en el servidor")

    titulo("2) INICIO DE SESIÓN LEGÍTIMO")
    desafio = servidor.nuevo_desafio()
    print(f"Desafío del servidor: {hex_corto(desafio)}")
    resp_ok = navegador_pide_firma(telefono, SITIO_REAL, desafio)
    ok, motivo = servidor.verificar("laura", resp_ok)
    print(f"Resultado: {'ACEPTADO' if ok else 'RECHAZADO'} — {motivo}")

    titulo("3) PHISHING: Laura cae en tiendanova-login.test y el atacante retransmite el desafío real")
    desafio = servidor.nuevo_desafio()
    try:
        navegador_pide_firma(telefono, SITIO_FALSO, desafio)
        print("El atacante obtuvo una firma (esto NO debería pasar)")
    except LookupError as e:
        print(f"RECHAZADO por el dispositivo — {e}")
    print("Laura no tuvo que 'darse cuenta' de nada: la passkey no existe para el dominio falso.")

    titulo("4) El atacante fabrica una respuesta con su propia llave")
    atacante = Autenticador()
    atacante.crear_credencial(servidor.rp_id)
    atacante._credenciales[servidor.rp_id]["contador"] = 50  # el atacante infla su contador para esquivar esa defensa
    desafio = servidor.nuevo_desafio()
    resp_falsa = atacante.firmar(servidor.rp_id, SITIO_REAL, desafio)
    ok, motivo = servidor.verificar("laura", resp_falsa)
    print(f"Resultado: {'ACEPTADO' if ok else 'RECHAZADO'} — {motivo}")

    titulo("5) REPETICIÓN: el atacante reenvía una respuesta válida que capturó antes")
    ok, motivo = servidor.verificar("laura", resp_ok)
    print(f"Resultado: {'ACEPTADO' if ok else 'RECHAZADO'} — {motivo}")

    titulo("6) BRECHA DEL SERVIDOR: el atacante roba la base de datos")
    print("Contenido robado (lo único que guarda el servidor):")
    for usuario, d in servidor.usuarios.items():
        print(f"  usuario={usuario}  llave_pública={hex_corto(d['publica'], 12)}  contador={d['contador']}")
    print("No hay contraseña ni hash que descifrar: con una llave pública no se puede firmar.")
    desafio = servidor.nuevo_desafio()
    intento = atacante.firmar(servidor.rp_id, SITIO_REAL, desafio)  # lo mejor que puede hacer: firmar con SU llave
    ok, motivo = servidor.verificar("laura", intento)
    print(f"Intento de ingreso con lo robado: {'ACEPTADO' if ok else 'RECHAZADO'} — {motivo}")

    titulo("7) USO LEGÍTIMO OTRA VEZ (para comprobar que todo sigue funcionando)")
    desafio = servidor.nuevo_desafio()
    ok, motivo = servidor.verificar("laura", navegador_pide_firma(telefono, SITIO_REAL, desafio))
    print(f"Resultado: {'ACEPTADO' if ok else 'RECHAZADO'} — {motivo}")


if __name__ == "__main__":
    main()
