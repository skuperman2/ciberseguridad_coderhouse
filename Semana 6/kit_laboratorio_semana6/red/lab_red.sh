#!/usr/bin/env bash
# Laboratorio de red virtual para la Semana 6 (todo dentro de UNA sola VM Debian, sin interfaz gráfica).
# Crea cuatro "computadoras" aisladas con namespaces de red:
#
#   laptop ──(Wi-Fi de la cafetería, 10.10.0.0/24)── cafe ──(internet, 203.0.113.0/24)── internet ──(198.51.100.0/24)── sitio
#   10.10.0.2                 10.10.0.1 | 203.0.113.2          203.0.113.10 | 198.51.100.1                    198.51.100.20
#
#   laptop   : tu equipo (el cliente)
#   cafe     : el router de la cafetería. Acá se "espía" el tráfico (punto de vista del atacante o del proveedor)
#   internet : un router de internet que además hace de servidor VPN (WireGuard 203.0.113.10:51820)
#   sitio    : el servidor web de destino (198.51.100.20)
#
# Uso:  sudo bash lab_red.sh crear | borrar | estado
#       sudo ip netns exec laptop <comando>      (ejecuta un comando "dentro" de la laptop)
set -euo pipefail

NS="laptop cafe internet sitio"

if [ "$(id -u)" -ne 0 ]; then echo "Ejecutá con sudo."; exit 1; fi

crear() {
  borrar quiet
  for n in $NS; do ip netns add "$n"; ip netns exec "$n" ip link set lo up; done

  # laptop <-> cafe (la red Wi-Fi de la cafetería)
  ip link add l0 type veth peer name c0
  ip link set l0 netns laptop; ip link set c0 netns cafe
  ip netns exec laptop ip addr add 10.10.0.2/24 dev l0; ip netns exec laptop ip link set l0 up
  ip netns exec cafe   ip addr add 10.10.0.1/24 dev c0; ip netns exec cafe   ip link set c0 up

  # cafe <-> internet
  ip link add c1 type veth peer name i0
  ip link set c1 netns cafe; ip link set i0 netns internet
  ip netns exec cafe     ip addr add 203.0.113.2/24  dev c1; ip netns exec cafe     ip link set c1 up
  ip netns exec internet ip addr add 203.0.113.10/24 dev i0; ip netns exec internet ip link set i0 up

  # internet <-> sitio
  ip link add i1 type veth peer name s0
  ip link set i1 netns internet; ip link set s0 netns sitio
  ip netns exec internet ip addr add 198.51.100.1/24  dev i1; ip netns exec internet ip link set i1 up
  ip netns exec sitio    ip addr add 198.51.100.20/24 dev s0; ip netns exec sitio    ip link set s0 up

  # rutas
  ip netns exec laptop   ip route add default via 10.10.0.1
  ip netns exec cafe     ip route add default via 203.0.113.10
  ip netns exec sitio    ip route add default via 198.51.100.1
  ip netns exec internet ip route add 10.10.0.0/24 via 203.0.113.2   # para respuestas hacia la laptop (sin NAT en internet)

  # reenvío de paquetes en los routers
  ip netns exec cafe     sysctl -qw net.ipv4.ip_forward=1
  ip netns exec internet sysctl -qw net.ipv4.ip_forward=1

  # La cafetería hace NAT: hacia internet todos salen con su IP pública (203.0.113.2)
  ip netns exec cafe nft -f - <<'NFT'
table ip nat {
  chain postrouting {
    type nat hook postrouting priority 100;
    oifname "c1" masquerade
  }
}
NFT
  # nombres de dominio de laboratorio (solo existen dentro de la laptop virtual)
  mkdir -p /etc/netns/laptop
  printf '127.0.0.1 localhost\n198.51.100.20 tiendanova.test tiendanova-login.test autofirmado.test sitio\n' > /etc/netns/laptop/hosts
  echo "Laboratorio creado. Verificación:"
  ip netns exec laptop ping -c1 -W2 198.51.100.20 >/dev/null && echo "  laptop -> sitio: OK" || echo "  laptop -> sitio: FALLA"
}

borrar() {
  bash "$(dirname "$0")/sitios.sh" detener quiet 2>/dev/null || true
  for n in $NS; do ip netns del "$n" 2>/dev/null || true; done
  rm -rf /etc/netns/laptop
  [ "${1:-}" = quiet ] || echo "Laboratorio borrado."
}

estado() {
  for n in $NS; do
    echo "== $n"; ip netns exec "$n" ip -br addr 2>/dev/null | grep -v "^lo" || echo "(no existe)"
  done
}

case "${1:-}" in
  crear) crear ;;
  borrar) borrar ;;
  estado) estado ;;
  *) echo "Uso: sudo bash $0 crear|borrar|estado"; exit 1 ;;
esac
