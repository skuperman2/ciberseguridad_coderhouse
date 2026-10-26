#!/usr/bin/env python3
"""Sitio web de laboratorio de TiendaNova (HTTP o HTTPS) para la Semana 6.

Rutas:
  GET  /        página con un formulario de inicio de sesión
  POST /login   recibe usuario y clave (el servidor NO los guarda; solo responde)
  GET  /ip      devuelve la dirección IP desde la que te ve el sitio
  GET  /huella  muestra lo que el navegador/cliente envía solo, calcula una "huella"
                y usa una cookie para reconocerte entre visitas

Uso:
  python3 servidor_sitio.py --puerto 80
  python3 servidor_sitio.py --puerto 443 --https --cert pki/tiendanova.test.crt --key pki/tiendanova.test.key
  python3 servidor_sitio.py --puerto 443 --https ... --hsts            (agrega Strict-Transport-Security)
  python3 servidor_sitio.py --puerto 80 --redirigir https://tiendanova.test   (HTTP responde 301 a HTTPS)

Todos los datos son ficticios. Solo escucha en la dirección que indiques (por defecto 0.0.0.0).
"""
import argparse
import hashlib
import http.server
import ssl
import uuid
from urllib.parse import parse_qs

ARGS = None

PAGINA = """<!doctype html><html lang="es"><meta charset="utf-8"><title>TiendaNova</title>
<h1>TiendaNova — ingresá a tu cuenta</h1>
<form method="POST" action="/login">
Usuario: <input name="usuario"><br>Clave: <input name="clave" type="password"><br>
<button>Entrar</button></form></html>"""


class Manejador(http.server.BaseHTTPRequestHandler):
    server_version = "TiendaNovaLab/1.0"

    def log_message(self, fmt, *args):
        print(f"[{self.client_address[0]}] {fmt % args}", flush=True)

    def _responder(self, codigo, cuerpo, tipo="text/plain; charset=utf-8", extra=None):
        datos = cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        if ARGS.hsts and ARGS.https:
            self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if ARGS.redirigir:
            self.send_response(301)
            self.send_header("Location", ARGS.redirigir + self.path)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path == "/ip":
            self._responder(200, f"El sitio te ve como: {self.client_address[0]}\n")
        elif self.path == "/huella":
            self._huella()
        else:
            self._responder(200, PAGINA, "text/html; charset=utf-8")

    def _huella(self):
        h = self.headers
        campos = ["User-Agent", "Accept", "Accept-Language", "Accept-Encoding"]
        valores = [h.get(c, "-") for c in campos]
        huella = hashlib.sha256("|".join(valores).encode()).hexdigest()[:16]
        cookie = h.get("Cookie", "")
        extra = {}
        if "visitante=" in cookie:
            saludo = "Te reconozco por la COOKIE: " + cookie
        else:
            vid = uuid.uuid4().hex[:8]
            extra["Set-Cookie"] = f"visitante={vid}; Path=/; Max-Age=3600"
            saludo = f"Visitante nuevo: te asigno la cookie visitante={vid}"
        lineas = [saludo, "", f"IP de origen : {self.client_address[0]}"]
        lineas += [f"{c:16}: {v}" for c, v in zip(campos, valores)]
        lineas += ["", f"Huella calculada (hash de esos campos): {huella}",
                   "(la huella NO usa cookies: es la misma si el cliente es el mismo)"]
        self._responder(200, "\n".join(lineas) + "\n", extra=extra)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        datos = parse_qs(self.rfile.read(n).decode("utf-8", "replace"))
        usuario = datos.get("usuario", ["?"])[0]
        # el servidor NO imprime la clave; el que espía la red sí podría verla si viaja en claro
        self._responder(200, f"Bienvenido, {usuario}. (sesión simulada)\n")


def main():
    global ARGS
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--puerto", type=int, default=80)
    ap.add_argument("--direccion", default="0.0.0.0")
    ap.add_argument("--https", action="store_true")
    ap.add_argument("--cert")
    ap.add_argument("--key")
    ap.add_argument("--hsts", action="store_true")
    ap.add_argument("--redirigir", help="URL base a la que responder 301 (simula http→https)")
    ARGS = ap.parse_args()
    srv = http.server.ThreadingHTTPServer((ARGS.direccion, ARGS.puerto), Manejador)
    if ARGS.https:
        if not (ARGS.cert and ARGS.key):
            ap.error("--https requiere --cert y --key")
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(ARGS.cert, ARGS.key)
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    esquema = "https" if ARGS.https else "http"
    print(f"Sitio de laboratorio en {esquema}://{ARGS.direccion}:{ARGS.puerto}  (Ctrl+C para salir)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
