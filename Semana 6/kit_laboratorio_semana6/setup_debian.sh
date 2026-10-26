#!/usr/bin/env bash
# Prepara una VM Debian 13 SIN interfaz gráfica para el laboratorio de la Semana 6.
# Requiere salida a internet (adaptador NAT) y un usuario con sudo.
set -euo pipefail

echo "[1/3] Actualizando índice de paquetes..."
sudo apt update

echo "[2/3] Instalando herramientas..."
# tshark pregunta si permite capturar a usuarios sin privilegios: respondemos que no (se usa sudo)
echo "wireshark-common wireshark-common/install-setuid boolean false" | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive apt install -y \
    iproute2 iputils-ping nftables tcpdump tshark wireguard-tools \
    openssl curl dnsutils python3 python3-scapy git ca-certificates unzip
# wireguard-go solo hace falta si el kernel no trae WireGuard (el kernel de Debian 13 sí lo trae)
sudo DEBIAN_FRONTEND=noninteractive apt install -y wireguard-go 2>/dev/null || true

echo "[3/3] Verificando..."
for c in ip ping nft tcpdump tshark wg openssl curl dig python3 git unzip; do
    printf "%-10s " "$c"; command -v "$c" >/dev/null && echo OK || echo "FALTA"
done
printf "%-10s " "scapy";  python3 -c "import scapy; print('OK', scapy.__version__)" 2>/dev/null || echo "FALTA"
printf "%-10s " "WireGuard"
if sudo ip link add wgprueba type wireguard 2>/dev/null; then sudo ip link del wgprueba; echo "OK (módulo del kernel)";
elif command -v wireguard-go >/dev/null; then echo "OK (wireguard-go en espacio de usuario)"; else echo "FALTA"; fi
echo
echo "Listo. Siguiente paso:  sudo bash red/lab_red.sh crear   y luego   sudo bash red/sitios.sh iniciar"
