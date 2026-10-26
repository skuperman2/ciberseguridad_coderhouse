#!/usr/bin/env bash
# Resume lo esencial de la conexión TLS a un sitio: versión, cifrado, certificado y autoridad que lo firmó.
# Uso (dentro de la laptop virtual):
#   sudo ip netns exec laptop bash inspeccionar_tls.sh tiendanova.test 443 pki/ca.crt
# Uso contra un sitio real (con internet y CAs del sistema):
#   bash inspeccionar_tls.sh example.com 443
set -euo pipefail
HOST="${1:?Uso: $0 host [puerto] [ca.crt]}"; PUERTO="${2:-443}"; CA="${3:-}"
OPC=(-connect "$HOST:$PUERTO" -servername "$HOST")
[ -n "$CA" ] && OPC+=(-CAfile "$CA")
SALIDA="$(openssl s_client "${OPC[@]}" </dev/null 2>/dev/null || true)"
echo "$SALIDA" | grep -E "^(New,|Verification|Verify return code)" || true
echo "$SALIDA" | grep -E "Server certificate|^ *[0-9] s:|subject=|issuer=" | head -6 || true
echo "--- Datos del certificado"
echo "$SALIDA" | openssl x509 -noout -subject -issuer -dates -ext subjectAltName 2>/dev/null || echo "(no se pudo leer el certificado)"
