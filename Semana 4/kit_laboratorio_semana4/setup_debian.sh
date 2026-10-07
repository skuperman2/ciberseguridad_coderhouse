#!/usr/bin/env bash
# Prepara la estación de análisis Debian 13 (sin interfaz gráfica).
# Requiere salida a internet (adaptador NAT activo) y permisos sudo.
set -euo pipefail

echo "[1/4] Actualizando índice de paquetes..."
sudo apt update

echo "[2/4] Instalando herramientas..."
# tshark pregunta si usuarios no root pueden capturar: lo dejamos sin preguntar
echo "wireshark-common wireshark-common/install-setuid boolean false" | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive apt install -y \
    tcpdump tshark bind9-dnsutils whois python3 clamav unzip curl

echo "[3/4] Verificando versiones..."
for c in tcpdump tshark dig whois python3 clamscan unzip; do
    printf "%-10s " "$c"; command -v "$c" >/dev/null && echo OK || echo "FALTA"
done

echo "[4/4] Interfaces de red (anotá la IP Host-Only 192.168.56.x):"
ip -br address
echo
echo "Listo. Para actualizar la base de ClamAV: sudo systemctl stop clamav-freshclam && sudo freshclam"
