#!/usr/bin/env bash
# Inicia o detiene los sitios web de laboratorio dentro del namespace "sitio" (198.51.100.20).
#   80   HTTP sin cifrar              tiendanova.test
#   443  HTTPS con certificado legítimo + HSTS (firmado por la CA de laboratorio)
#   8080 HTTP que redirige a HTTPS (301)
#   8443 HTTPS de tiendanova-login.test (dominio parecido, certificado válido de la misma CA)
#   9443 HTTPS autofirmado (autofirmado.test)
# Uso: sudo bash sitios.sh iniciar | detener
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecutá con sudo."; exit 1; }
DIR="$(cd "$(dirname "$0")" && pwd)"
PKI="$DIR/../tls/pki"
PIDS="$DIR/.pids"
SRV="$DIR/servidor_sitio.py"
iniciar() {
  [ -f "$PKI/ca.crt" ] || bash "$DIR/../tls/crear_pki_lab.sh" >/dev/null
  ip netns list | grep -qw sitio || { echo "Primero: sudo bash lab_red.sh crear"; exit 1; }
  detener quiet
  : > "$PIDS"
  arrancar() { (nohup ip netns exec sitio python3 "$SRV" "$@" >/dev/null 2>&1 & echo $! >> "$PIDS"); }
  arrancar --puerto 80
  arrancar --puerto 443  --https --cert "$PKI/tiendanova.test.crt"       --key "$PKI/tiendanova.test.key" --hsts
  arrancar --puerto 8080 --redirigir https://tiendanova.test
  arrancar --puerto 8443 --https --cert "$PKI/tiendanova-login.test.crt" --key "$PKI/tiendanova-login.test.key"
  arrancar --puerto 9443 --https --cert "$PKI/autofirmado.test.crt"      --key "$PKI/autofirmado.test.key"
  sleep 1.5
  echo "Sitios iniciados (80, 443, 8080, 8443, 9443)."
}
detener() {
  if [ -f "$PIDS" ]; then xargs -r kill 2>/dev/null < "$PIDS" || true; rm -f "$PIDS"; fi
  [ "${1:-}" = quiet ] || echo "Sitios detenidos."
}
case "${1:-}" in iniciar) iniciar ;; detener) detener ;; *) echo "Uso: sudo bash $0 iniciar|detener"; exit 1 ;; esac
