#!/usr/bin/env bash
# Crea una mini infraestructura de certificados (PKI) de laboratorio en ./pki
#   - TiendaNova Lab CA            : una "autoridad certificadora" propia (solo sirve en el laboratorio)
#   - tiendanova.test              : certificado legítimo firmado por la CA
#   - tiendanova-login.test        : certificado de un dominio PARECIDO (phishing), firmado por la MISMA CA
#   - autofirmado.test             : certificado autofirmado (nadie lo avala)
# Lección: una CA firma certificados para cualquier dominio que le pidan y cuyo control se compruebe;
#          el candado dice "la conexión es privada", no "el sitio es honesto".
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p pki && cd pki
rm -f *.crt *.key *.csr *.srl *.cnf

echo "[1/4] Autoridad certificadora de laboratorio"
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 365 \
  -subj "/O=TiendaNova Lab/CN=TiendaNova Lab CA" -keyout ca.key -out ca.crt 2>/dev/null

emitir() {  # emitir <dominio>
  local d="$1"
  cat > "$d.cnf" <<CNF
subjectAltName = DNS:$d
extendedKeyUsage = serverAuth
CNF
  openssl req -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -subj "/CN=$d" \
    -keyout "$d.key" -out "$d.csr" 2>/dev/null
  openssl x509 -req -in "$d.csr" -CA ca.crt -CAkey ca.key -CAcreateserial -days 90 \
    -extfile "$d.cnf" -out "$d.crt" 2>/dev/null
}
echo "[2/4] Certificado legítimo: tiendanova.test";           emitir tiendanova.test
echo "[3/4] Certificado del dominio parecido: tiendanova-login.test"; emitir tiendanova-login.test
echo "[4/4] Certificado autofirmado: autofirmado.test"
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 90 \
  -subj "/CN=autofirmado.test" -addext "subjectAltName=DNS:autofirmado.test" \
  -keyout autofirmado.test.key -out autofirmado.test.crt 2>/dev/null
rm -f *.csr *.cnf *.srl
echo; ls -1 *.crt *.key
