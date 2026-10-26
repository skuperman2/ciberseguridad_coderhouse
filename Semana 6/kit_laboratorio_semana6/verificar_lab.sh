#!/usr/bin/env bash
# Prueba de humo del laboratorio completo. Úsala ANTES de la clase (docente) o si algo no responde (participante).
# Uso: sudo bash verificar_lab.sh      Crea el laboratorio, ejecuta las comprobaciones y lo deja armado.
set -uo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecutá con sudo."; exit 1; }
cd "$(dirname "$0")"
unset HTTPS_PROXY https_proxy HTTP_PROXY http_proxy ALL_PROXY all_proxy   # el laboratorio es local: sin proxies
OK=0; MAL=0
chk() { if eval "$2" >/dev/null 2>&1; then echo "  [OK]   $1"; OK=$((OK+1)); else echo "  [FALLA] $1"; MAL=$((MAL+1)); fi; }
L="ip netns exec laptop"

bash red/lab_red.sh crear >/dev/null 2>&1; bash tls/crear_pki_lab.sh >/dev/null 2>&1; bash red/sitios.sh iniciar >/dev/null 2>&1
chk "laptop llega al sitio (ping)"                  "$L ping -c1 -W2 198.51.100.20"
chk "HTTP: el sitio ve la IP pública de la cafetería" "[ \"\$($L curl -s --max-time 5 http://tiendanova.test/ip)\" = 'El sitio te ve como: 203.0.113.2' ]"
chk "HTTPS sin la CA de laboratorio falla"          "! $L curl -s --max-time 5 https://tiendanova.test/ip"
chk "HTTPS con la CA de laboratorio funciona"       "$L curl -s --max-time 5 --cacert tls/pki/ca.crt https://tiendanova.test/ip"
chk "Certificado del dominio parecido es válido (candado ≠ honestidad)" "$L curl -s --max-time 5 --cacert tls/pki/ca.crt https://tiendanova-login.test:8443/ip"
chk "Certificado autofirmado es rechazado"          "! $L curl -s --max-time 5 --cacert tls/pki/ca.crt https://autofirmado.test:9443/ip"

# Captura HTTP vs HTTPS
TMP="$(mktemp -d)"
ip netns exec cafe tcpdump -i c0 -U -w "$TMP/http.pcap" >/dev/null 2>&1 & TP=$!; sleep 1
$L curl -s --max-time 5 -d "usuario=laura&clave=Secreta123" http://tiendanova.test/login >/dev/null; sleep 1; kill $TP 2>/dev/null; wait $TP 2>/dev/null
chk "La captura HTTP contiene la clave en claro"    "[[ \"\$(python3 red/analizar_trafico.py $TMP/http.pcap)\" == *'clave = Secreta123'* ]]"
ip netns exec cafe tcpdump -i c0 -U -w "$TMP/https.pcap" >/dev/null 2>&1 & TP=$!; sleep 1
$L curl -s --max-time 5 --cacert tls/pki/ca.crt -d "usuario=laura&clave=Secreta123" https://tiendanova.test/login >/dev/null; sleep 1; kill $TP 2>/dev/null; wait $TP 2>/dev/null
chk "La captura HTTPS NO contiene la clave"         "[[ \"\$(python3 red/analizar_trafico.py $TMP/https.pcap)\" != *Secreta123* ]]"

# VPN
bash vpn/vpn_lab.sh subir >/dev/null 2>&1
chk "VPN: handshake establecido"                    "ip netns exec laptop wg show wgc0 latest-handshakes | grep -qv ' 0\$'"
chk "VPN: el sitio ve la IP del servidor VPN"       "[ \"\$($L curl -s --max-time 5 http://tiendanova.test/ip)\" = 'El sitio te ve como: 203.0.113.10' ]"
ip netns exec cafe tcpdump -i c0 -U -w "$TMP/vpn.pcap" >/dev/null 2>&1 & TP=$!; sleep 1
$L curl -s --max-time 5 -d "usuario=laura&clave=Secreta123" http://tiendanova.test/login >/dev/null; sleep 1; kill $TP 2>/dev/null; wait $TP 2>/dev/null
chk "VPN: la cafetería solo ve UDP/51820 (sin HTTP)" "R=\$(python3 red/analizar_trafico.py $TMP/vpn.pcap); [[ \"\$R\" == *UDP/51820* && \"\$R\" != *'DATO EXPUESTO'* ]]"
bash vpn/vpn_lab.sh killswitch >/dev/null 2>&1; ip netns exec laptop ip link del wgc0 2>/dev/null
chk "Kill switch: sin túnel no hay salida"          "! $L curl -s --max-time 3 http://tiendanova.test/ip"
bash vpn/vpn_lab.sh bajar >/dev/null 2>&1

# Wi-Fi
python3 wifi/generar_captura_wifi.py "$TMP/wifi.pcap" >/dev/null 2>&1
chk "Análisis Wi-Fi: detecta la red gemela"         "[[ \"\$(python3 wifi/analizar_wifi.py $TMP/wifi.pcap)\" == *'RED GEMELA'* ]]"
rm -rf "$TMP"
echo; echo "Resultado: $OK correctas, $MAL con falla."
[ "$MAL" -eq 0 ]
