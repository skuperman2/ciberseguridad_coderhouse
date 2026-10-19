#!/usr/bin/env python3
"""Reto de la unidad: automatizar el acceso a una bóveda VeraCrypt (versión Linux, consola).

Completá las funciones `comando_crear`, `comando_montar` y `comando_desmontar`.
El programa NO ejecuta nada por defecto: solo muestra los comandos (modo simulación).
Con --ejecutar corre los comandos de verdad (necesita VeraCrypt instalado y sudo).

Nota de seguridad: pasar la contraseña con --password deja la clave en el historial
y en la lista de procesos. Acá se hace para practicar; en la vida real se pide por
teclado o se lee del gestor de contraseñas.
"""
import argparse
import shlex
import subprocess
import sys

# ---- Datos de prueba ---------------------------------------------------------
CONTENEDOR = "datos_confidenciales.hc"
PUNTO_DE_MONTAJE = "/mnt/boveda"
CLAVE = "MiPasswordSuperSecreto"  # ficticia: NO usar una clave real en este ejercicio


def comando_crear(ruta, tamano_mb, clave):
    """Devuelve la lista de argumentos para CREAR un contenedor normal de `tamano_mb` MB.

    Pistas (opciones de veracrypt):
      --text                  modo consola
      --create RUTA           crea un volumen
      --size=NM               tamaño, por ejemplo 20M
      --volume-type=normal
      --encryption=AES   --hash=SHA-512   --filesystem=ext4
      --password=CLAVE   --pim=0   --keyfiles=""
      --random-source=/dev/urandom   --non-interactive
    """
    # TODO: completar con una lista de argumentos que empiece con "veracrypt"
    return []


def comando_montar(ruta, punto, clave):
    """Devuelve la lista de argumentos para MONTAR el contenedor en `punto`.

    Pista: veracrypt --text --mount RUTA PUNTO --password=CLAVE --pim=0 --keyfiles="" --protect-hidden=no --non-interactive
    """
    # TODO
    return []


def comando_desmontar(punto):
    """Devuelve la lista de argumentos para DESMONTAR (la llave se borra de la memoria).

    Pista: veracrypt --text --unmount PUNTO   (en versiones anteriores: --dismount)
    """
    # TODO
    return []


def mostrar_o_ejecutar(argumentos, ejecutar):
    if not argumentos:
        print("  (comando sin completar)")
        return 1
    # Para mostrar el comando sin exponer la clave en pantalla
    visible = [("--password=********" if a.startswith("--password=") else a) for a in argumentos]
    print("  $ " + " ".join(shlex.quote(a) for a in visible))
    if ejecutar:
        return subprocess.run(["sudo"] + argumentos).returncode
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["crear", "montar", "desmontar", "ciclo"])
    ap.add_argument("--ejecutar", action="store_true", help="ejecutar de verdad (por defecto solo simula)")
    a = ap.parse_args()

    print(f"Modo: {'EJECUCIÓN REAL' if a.ejecutar else 'simulación (no se ejecuta nada)'}")
    codigo = 0
    if a.accion in ("crear",):
        codigo |= mostrar_o_ejecutar(comando_crear(CONTENEDOR, 20, CLAVE), a.ejecutar)
    if a.accion in ("montar", "ciclo"):
        codigo |= mostrar_o_ejecutar(comando_montar(CONTENEDOR, PUNTO_DE_MONTAJE, CLAVE), a.ejecutar)
    if a.accion in ("desmontar", "ciclo"):
        codigo |= mostrar_o_ejecutar(comando_desmontar(PUNTO_DE_MONTAJE), a.ejecutar)
    sys.exit(codigo)


if __name__ == "__main__":
    main()
