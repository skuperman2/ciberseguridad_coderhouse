#!/usr/bin/env bash
# VPN WireGuard de laboratorio entre la "laptop" y el servidor VPN (namespace "internet").
# Requiere haber creado antes el laboratorio:  sudo bash ../red/lab_red.sh crear
#
#   laptop (wgc0 10.99.0.2) ══ túnel cifrado UDP/51820 ══ internet (wgs0 10.99.0.1, 203.0.113.10)
#
# Uso:  sudo bash vpn_lab.sh subir       crea claves, levanta el túnel y envía TODO el tráfico por él
#       sudo bash vpn_lab.sh bajar       baja el túnel y restaura las rutas normales
#       sudo bash vpn_lab.sh estado      muestra el estado (wg show) en ambos extremos
#       sudo bash vpn_lab.sh killswitch  activa el "interruptor de pánico" en la laptop
#       sudo bash vpn_lab.sh sinkill     quita el interruptor de pánico
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecutá con sudo."; exit 1; }
DIR="$(cd "$(dirname "$0")" && pwd)"
CLAVES="$DIR/claves_lab"          # claves de laboratorio, se generan acá y no se reutilizan en la vida real
EP_IP=203.0.113.10; EP_PORT=51820

crear_interfaz() {   # crear_interfaz <namespace> <nombre>
  local ns="$1" nom="$2"
  if ip netns exec "$ns" ip link add "$nom" type wireguard 2>/dev/null; then
    echo "  [$ns] WireGuard en el kernel ($nom)"
  elif command -v wireguard-go >/dev/null; then
    # Alternativa en espacio de usuario si el kernel no trae el módulo
    (nohup ip netns exec "$ns" wireguard-go -f "$nom" >/dev/null 2>&1 &)
    for _ in $(seq 1 50); do [ -S "/var/run/wireguard/$nom.sock" ] && break; sleep 0.1; done
    echo "  [$ns] WireGuard en espacio de usuario ($nom, wireguard-go)"
  else
    echo "No hay soporte de WireGuard (ni módulo del kernel ni wireguard-go)."; exit 1
  fi
}

subir() {
  mkdir -p "$CLAVES"; umask 077
  [ -f "$CLAVES/srv.key" ] || wg genkey > "$CLAVES/srv.key"
  [ -f "$CLAVES/cli.key" ] || wg genkey > "$CLAVES/cli.key"
  wg pubkey < "$CLAVES/srv.key" > "$CLAVES/srv.pub"
  wg pubkey < "$CLAVES/cli.key" > "$CLAVES/cli.pub"

  echo "[1/4] Servidor VPN (namespace internet)"
  crear_interfaz internet wgs0
  ip netns exec internet wg set wgs0 listen-port $EP_PORT private-key "$CLAVES/srv.key" \
      peer "$(cat "$CLAVES/cli.pub")" allowed-ips 10.99.0.2/32
  ip netns exec internet ip addr add 10.99.0.1/24 dev wgs0
  ip netns exec internet ip link set wgs0 up
  # El servidor reenvía y hace NAT: el sitio verá la IP del servidor VPN, no la de la laptop
  ip netns exec internet nft -f - <<'NFT'
table ip vpnnat {
  chain post {
    type nat hook postrouting priority 100;
    ip saddr 10.99.0.0/24 oifname "i1" snat to 203.0.113.10
  }
}
NFT

  echo "[2/4] Cliente VPN (namespace laptop)"
  crear_interfaz laptop wgc0
  ip netns exec laptop wg set wgc0 private-key "$CLAVES/cli.key" \
      peer "$(cat "$CLAVES/srv.pub")" endpoint $EP_IP:$EP_PORT allowed-ips 0.0.0.0/0 persistent-keepalive 5
  ip netns exec laptop ip addr add 10.99.0.2/24 dev wgc0
  ip netns exec laptop ip link set wgc0 up

  echo "[3/4] Rutas: todo el tráfico por el túnel (menos el que lleva al propio servidor VPN)"
  ip netns exec laptop ip route add $EP_IP/32 via 10.10.0.1
  ip netns exec laptop ip route add 0.0.0.0/1 dev wgc0
  ip netns exec laptop ip route add 128.0.0.0/1 dev wgc0

  echo "[4/4] Verificación"
  ip netns exec laptop ping -c2 -W2 10.99.0.1 >/dev/null && echo "  túnel: OK (laptop llega a 10.99.0.1)" || echo "  túnel: FALLA"
}

bajar() {
  ip netns exec laptop nft delete table inet killswitch 2>/dev/null || true
  ip netns exec laptop ip route del 0.0.0.0/1 2>/dev/null || true
  ip netns exec laptop ip route del 128.0.0.0/1 2>/dev/null || true
  ip netns exec laptop ip route del $EP_IP/32 2>/dev/null || true
  ip netns exec laptop ip link del wgc0 2>/dev/null || true
  ip netns exec internet ip link del wgs0 2>/dev/null || true
  ip netns exec internet nft delete table ip vpnnat 2>/dev/null || true
  pkill -x wireguard-go 2>/dev/null || true
  rm -f /var/run/wireguard/wgc0.sock /var/run/wireguard/wgs0.sock
  echo "VPN apagada."
}

estado() {
  echo "== cliente (laptop)"; ip netns exec laptop wg show 2>/dev/null || echo "(sin túnel)"
  echo "== servidor (internet)"; ip netns exec internet wg show 2>/dev/null || echo "(sin túnel)"
}

killswitch() {
  # Política: solo se permite salir por el túnel, o hablar con el servidor VPN para (re)conectar.
  ip netns exec laptop nft -f - <<'NFT'
table inet killswitch {
  chain output {
    type filter hook output priority 0; policy drop;
    oifname "lo" accept
    oifname "wgc0" accept
    ip daddr 203.0.113.10 udp dport 51820 accept
  }
}
NFT
  echo "Kill switch ACTIVO: sin túnel, la laptop no puede salir a internet."
}
sinkill() { ip netns exec laptop nft delete table inet killswitch 2>/dev/null || true; echo "Kill switch desactivado."; }

case "${1:-}" in
  subir) subir ;; bajar) bajar ;; estado) estado ;; killswitch) killswitch ;; sinkill) sinkill ;;
  *) echo "Uso: sudo bash $0 subir|bajar|estado|killswitch|sinkill"; exit 1 ;;
esac
