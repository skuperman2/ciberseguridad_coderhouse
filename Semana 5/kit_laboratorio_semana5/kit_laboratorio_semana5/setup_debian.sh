#!/usr/bin/env bash
# Prepara la estación Debian 13 (sin interfaz gráfica) para el laboratorio de la Semana 5.
# Requiere salida a internet (adaptador NAT) y un usuario con sudo.
set -euo pipefail

echo "[1/3] Actualizando índice de paquetes..."
sudo apt update

echo "[2/3] Instalando herramientas..."
sudo DEBIAN_FRONTEND=noninteractive apt install -y \
    keepassxc oathtool openssl python3 python3-cryptography \
    e2fsprogs unzip curl ca-certificates

echo "[3/3] Verificando..."
for c in keepassxc-cli oathtool openssl python3 curl unzip mkfs.ext4; do
    printf "%-16s " "$c"; command -v "$c" >/dev/null && echo OK || echo "FALTA"
done
printf "%-16s " "python3-cryptography"; python3 -c "import cryptography; print('OK', cryptography.__version__)" 2>/dev/null || echo "FALTA"
echo
echo "VeraCrypt no está en los repositorios de Debian: instalalo con  bash instalar_veracrypt.sh"
