#!/usr/bin/env bash
# Descarga e instala VeraCrypt (versión consola) para Debian 13 verificando su integridad.
# Descarga desde los lanzamientos oficiales del proyecto en GitHub y comprueba el hash SHA-256
# contra el archivo de sumas publicado por el proyecto Y contra un valor fijado en este script.
set -euo pipefail

VERSION="1.26.29"
BASE="https://github.com/veracrypt/VeraCrypt/releases/download/VeraCrypt_${VERSION}"
ARCH="$(dpkg --print-architecture)"            # amd64 o arm64
PAQUETE="veracrypt-console-${VERSION}-Debian-13-${ARCH}.deb"
SUMAS="veracrypt-${VERSION}-sha256sum.txt"
# Hash esperado del paquete amd64 (verificado al preparar el laboratorio)
HASH_AMD64="1663ec6e7645f7fddd4a9d725b8d283edcde6e1fcafdcfbdc116d737c0894e8d"

if [ -r /etc/os-release ] && ! grep -q '^VERSION_ID="13"' /etc/os-release; then
    echo "AVISO: este paquete es para Debian 13 y el sistema no parece serlo." >&2
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"

echo "[1/4] Descargando $PAQUETE ..."
curl -fsSL -O "$BASE/$PAQUETE"
curl -fsSL -O "$BASE/$SUMAS"

echo "[2/4] Verificando integridad ..."
obtenido="$(sha256sum "$PAQUETE" | cut -d' ' -f1)"
publicado="$(grep -i "$PAQUETE" "$SUMAS" | cut -d' ' -f1 | tr 'A-F' 'a-f')"
echo "   obtenido : $obtenido"
echo "   publicado: $publicado"
if [ "$obtenido" != "$publicado" ]; then
    echo "ERROR: el hash no coincide con el archivo de sumas. NO se instala." >&2
    exit 1
fi
if [ "$ARCH" = "amd64" ] && [ "$obtenido" != "$HASH_AMD64" ]; then
    echo "AVISO: el hash no coincide con el fijado en este script (¿versión nueva?). Revisá antes de seguir." >&2
    read -r -p "¿Continuar de todos modos? [s/N] " r
    [ "$r" = "s" ] || exit 1
fi
echo "   OK: el paquete coincide."

echo "[3/4] Instalando ..."
sudo apt install -y "./$PAQUETE"

echo "[4/4] Comprobando ..."
veracrypt --text --version
