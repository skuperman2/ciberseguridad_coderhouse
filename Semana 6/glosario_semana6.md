# Glosario de términos y fórmulas — Semana 6

## Seguridad en la web y conectividad

---

## 1. Términos

### 1.1 Huella digital y navegación privada

| Término | Definición | Ejemplo / nota |
|---|---|---|
| **Huella digital (rastro)** | Conjunto de datos que dejás al usar internet: IP, historial, cookies, huella del navegador, cuentas. | Visitar un sitio deja rastro en tu equipo, en tu red y en el sitio. |
| **Dirección IP** | Identificador de tu conexión en la red; el sitio la necesita para responderte. | Sin VPN, el sitio ve la IP de la cafetería (en el lab, 203.0.113.2). |
| **Cookie** | Archivo pequeño que el sitio guarda en tu navegador para recordarte. | Sesión iniciada, carrito, seguimiento publicitario. |
| **Cookie de terceros** | Cookie colocada por un dominio distinto del que visitás (publicidad, métricas). | Permite seguirte entre sitios. |
| **Fingerprinting (huella del navegador)** | Identificación por la combinación de atributos que el navegador entrega (User-Agent, idioma, zona horaria, pantalla, fuentes, canvas). No se guarda en tu equipo: se recalcula en cada visita. | Borrar cookies no la cambia. |
| **Conjunto de anonimato** | Grupo de personas con la misma huella; cuanto más chico, más identificable sos. | Con 34 bits, el grupo ronda 1 persona. |
| **Modo incógnito / navegación privada** | Función **local** del navegador: no guarda historial, cookies ni formularios al cerrar la ventana. | No oculta nada a la red, al proveedor, a la escuela ni al sitio. |
| **Rastreo entre sitios** | Seguimiento del mismo usuario en distintos sitios mediante cookies de terceros, huella o cuentas. | |

### 1.2 HTTP, HTTPS y TLS

| Término | Definición | Ejemplo / nota |
|---|---|---|
| **HTTP** | Protocolo de la web **sin cifrado**. | Como una postal: lo lee quien la transporta. |
| **HTTPS** | HTTP dentro de un canal cifrado con TLS. | Como una caja cerrada. |
| **TLS** | Protocolo que da confidencialidad, integridad y autenticación del servidor. Versión vigente: 1.3. | Sucesor de SSL (obsoleto). |
| **Handshake (saludo) TLS** | Negociación inicial: el cliente envía ClientHello, el servidor responde y presenta su certificado, ambos derivan una clave de sesión. | |
| **SNI** | Extensión que indica el nombre del sitio en el ClientHello; viaja sin cifrar (salvo ECH). | El espía ve *tiendanova.test* aunque no vea el contenido. |
| **ECH (Encrypted Client Hello)** | Mejora de TLS que cifra el SNI. | Adopción todavía parcial. |
| **Certificado digital (X.509)** | Documento que vincula una clave pública con un nombre de dominio, firmado por una CA. | Campos: subject, issuer, vigencia, SAN. |
| **CA (autoridad certificadora)** | Entidad de confianza que firma certificados. | Let's Encrypt; en el lab, *TiendaNova Lab CA*. |
| **SAN (Subject Alternative Name)** | Lista de nombres para los que el certificado es válido; es lo que se compara con el dominio. | |
| **Certificado autofirmado** | Certificado firmado por quien lo emite; nadie externo lo avala. | curl: `self-signed certificate`. |
| **HSTS** | Encabezado `Strict-Transport-Security` que ordena al navegador usar solo HTTPS durante `max-age` segundos. | Evita el *SSL stripping*. |
| **HSTS preload** | Lista incluida en el navegador de sitios que siempre usan HTTPS, incluso en la primera visita. | |
| **SSL stripping** | Ataque que elimina la redirección de HTTP a HTTPS para mantener a la víctima en HTTP. | |
| **Candado ≠ honestidad** | El candado indica conexión cifrada con el titular del dominio, no que el sitio sea legítimo. | Un sitio de phishing también puede tener HTTPS. |
| **Phishing** | Suplantación de un sitio o mensaje para robar datos. | `tiendanova-login.test` en el lab. |
| **ACME** | Protocolo para emitir y renovar certificados automáticamente. | Certbot, Let's Encrypt. |
| **Ataque de intermediario (MITM)** | El atacante se interpone entre cliente y servidor para leer o alterar el tráfico. | |

### 1.3 VPN

| Término | Definición | Ejemplo / nota |
|---|---|---|
| **VPN** | Red privada virtual: un túnel cifrado entre tu equipo y un servidor VPN. | Cambia quién te ve: pasás de la red local al proveedor VPN. |
| **Túnel** | Canal que encapsula y cifra el tráfico dentro de otro. | |
| **WireGuard** | Protocolo VPN moderno, ligero, en el kernel de Linux desde la 5.6. UDP, puerto por defecto 51820. | |
| **OpenVPN** | VPN clásica, flexible; UDP/TCP 1194. | |
| **IPsec / IKEv2** | Familia de protocolos VPN estándar; puertos UDP 500 y 4500. | |
| **Kill switch** | Mecanismo que corta el tráfico si cae la VPN, evitando fugas. | En el lab: tabla `inet killswitch` de nftables. |
| **Fuga (leak)** | Tráfico que sale fuera del túnel: IP, DNS o IPv6. | |
| **Fuga de DNS** | Las consultas DNS salen sin pasar por el túnel. | |
| **AllowedIPs** | En WireGuard, qué destinos se enrutan por el túnel; `0.0.0.0/0` envía todo. | |
| **MTU** | Tamaño máximo de paquete en un enlace. | WireGuard: 1420 por defecto. |
| **Política no-logs** | Promesa del proveedor de no registrar actividad; solo verificable con auditorías independientes. | |
| **VPN gratuita** | Servicio sin costo visible; suele financiarse con datos o publicidad. | Riesgo: vos sos el producto. |
| **TunnelVision (CVE-2024-3661)** | Técnica que usa opciones DHCP para desviar tráfico fuera de la VPN; CVSS 7,6. Android no se ve afectado. | |
| **Superficie de ataque** | Conjunto de puntos expuestos que un atacante puede intentar vulnerar. | Las VPN corporativas expuestas son un objetivo frecuente. |

### 1.4 Wi-Fi pública

| Término | Definición | Ejemplo / nota |
|---|---|---|
| **SSID** | Nombre visible de la red Wi-Fi. | `CafeNova_Gratis`. |
| **BSSID** | Dirección MAC del punto de acceso; identifica físicamente a cada uno. | |
| **Sniffing** | Captura de tráfico en la red. | `tcpdump`, `tshark`. |
| **Evil twin (red gemela)** | Punto de acceso falso con el mismo nombre que uno legítimo. | |
| **Desautenticación (deauth)** | Trama 802.11 que expulsa a un cliente de la red; sin protección puede falsificarse. | |
| **802.11w (PMF)** | Protección de tramas de gestión; obligatoria en WPA3. | |
| **WPA2 / WPA3** | Estándares de cifrado Wi-Fi. WPA3 usa SAE y protege contra ataques de diccionario offline. | |
| **OWE** | Cifrado oportunista para redes abiertas: cifra sin contraseña, pero no autentica el punto de acceso. | |
| **Portal cautivo** | Página que aparece al conectarte a una Wi-Fi pública. | |
| **EAPOL** | Mensajes del apretón de manos de 4 vías de WPA2. | |
| **Contraseña ≠ seguridad** | Que una red tenga clave no garantiza que sea confiable; quien conoce la clave puede ver o suplantar. | |

### 1.5 Principios

| Término | Definición |
|---|---|
| **Tríada CIA** | **Confidencialidad** (solo lo ve quien debe), **Integridad** (no se altera), **Disponibilidad** (está cuando se necesita). |
| **MFA** | Autenticación multifactor; mitiga el robo de contraseñas (Semana 5). |
| **Defensa en capas** | Combinar controles: local (navegador), red (VPN, Wi-Fi) y comportamiento (hábitos). |
| **Mínimo privilegio** | Dar solo el acceso necesario. |

---

## 2. Fórmulas y cálculos

| Cálculo | Fórmula | Ejemplo |
|---|---|---|
| **Bits de una huella** | bits = log₂(N) | 8 × 10⁹ personas → 32,9 bits |
| **Bits de un atributo** | log₂(valores posibles) | 1024 → 10 bits; 16 → 4; 8 → 3; 32 → 5; 4096 → 12 |
| **Bits combinados (independientes)** | suma de bits | 10+4+3+5+12 = 34 bits |
| **Tamaño del grupo restante** | N / 2^bits | 8×10⁹ / 2^34 ≈ 0,47 |
| **Segundos de HSTS a días** | max-age ÷ 86.400 | 31.536.000 ÷ 86.400 = 365 días |
| **Renovaciones por año** | 365 ÷ validez | 200 d → 1,8; 100 d → 3,65; 47 d → 7,8 |
| **MTU del túnel WireGuard** | MTU enlace − sobrecarga | 1500 − 80 = 1420 (IPv6); 1500 − 60 = 1440 (IPv4) |
| **Duración de un certificado** | notAfter − notBefore | 26/10/2026 → 24/1/2027 = 90 días |

> Nota: la suma de bits supone atributos independientes. En la práctica hay correlación, por lo que es una **estimación**.

---

## 3. Comandos del laboratorio

### 3.1 Web y TLS

```bash
curl -sv -o /dev/null http://tiendanova.test 2>&1 | grep -E '^[<>*]'   # ver pedido y respuesta
curl -s http://tiendanova.test/huella                                   # huella calculada por el servidor
curl -sv https://tiendanova.test/ip                                     # handshake TLS y verificación
curl --cacert tls/pki/ca.crt https://tiendanova.test/ip                 # confiar en la CA del lab
curl -k https://autofirmado.test:9443/ip                                # ignora el error (solo en el lab)
curl --hsts hsts.txt -w '%{url_effective}\n' -o /dev/null -s http://tiendanova.test/ip
openssl s_client -connect tiendanova.test:443 -servername tiendanova.test </dev/null
openssl x509 -in cert.pem -noout -subject -issuer -dates -ext subjectAltName
```

### 3.2 Captura de tráfico

```bash
sudo tcpdump -i c0 -nn -w captura.pcap                          # capturar
sudo tcpdump -nn -A -r captura.pcap 'tcp port 80'                # leer HTTP en claro
tshark -r captura.pcap -Y 'http.request.method == "POST"'        # filtro: POST
tshark -r captura.pcap -Y 'tls.handshake.type == 1' -T fields -e tls.handshake.extensions_server_name
tshark -r captura.pcap -Y 'udp.port == 51820'                    # tráfico WireGuard
```

### 3.3 VPN y kill switch

```bash
sudo wg show                          # estado del túnel
sudo ./vpn/vpn_lab.sh subir|bajar|estado|killswitch|sinkill
ip route                              # rutas (0/1 y 128/1 llevan todo al túnel)
sudo nft list ruleset                 # reglas del kill switch
```

### 3.4 Wi-Fi

```bash
python3 wifi/generar_captura_wifi.py   # genera captura 802.11 sintética
python3 wifi/analizar_wifi.py captura_wifi.pcap
```

---

## 4. Ejemplos actuales (2025–2026)

- **Certificados más cortos:** el CA/Browser Forum fijó validez máxima de 200 días (15/3/2026), 100 (15/3/2027) y 47 (15/3/2029). *(The Register)*
- **HTTPS por defecto:** Google anunció que Chrome 154 (octubre de 2026) activará HTTPS por defecto; ya hoy ~97–99 % de la navegación en Chrome usa HTTPS. *(blog.google, oct. 2025)*
- **Verificación de edad y VPN:** tras la entrada en vigor de la Online Safety Act del Reino Unido (25/7/2025), las altas en Proton VPN subieron ~1.400 %. *(The Register)*
- **TunnelVision (CVE-2024-3661):** permite desviar tráfico fuera de la VPN. *(The Hacker News / Zscaler)*
- **Dispositivos de borde y VPN:** el DBIR 2025 de Verizon indica que los dispositivos de borde y VPN fueron el 22 % de los objetivos de explotación de vulnerabilidades (3 % el año previo); solo el 54 % se corrigió por completo, con mediana de 32 días. *(Tenable, sobre el DBIR 2025)* Ejemplo: CVE-2025-0282 de Ivanti (enero de 2025).
- **Incógnito y Google:** acuerdo judicial de abril de 2024 por recolección de datos de usuarios en modo incógnito. *(CTV News)*
- **Wi-Fi de aerolínea (evil twin):** vuelo DL591 de Delta (10/8/2026): la tripulación avisó de una red falsa "Delta WiFi Fast", apagó el Wi-Fi oficial unos 30 minutos y notificó al FBI. La técnica exacta y si hubo robo de datos no están confirmadas; presentarlo con cautela.
- **Clapsis:** condena de 7 años y 4 meses por montar redes Wi-Fi gemelas en aeropuertos y vuelos. *(SecurityWeek, dic. 2025)*

---

## 5. Errores frecuentes

1. **"En incógnito soy invisible."** Solo no se guarda nada local.
2. **"Con VPN estoy anónimo."** Cambia el observador; el proveedor de VPN te ve y el navegador sigue entregando la huella.
3. **"Tiene candado, entonces es confiable."** Cifrado ≠ legítimo.
4. **"La Wi-Fi con contraseña es segura."** Quien conoce la clave puede espiar, y una red gemela puede copiar el nombre.
5. **"La VPN gratuita me protege."** Puede registrar y vender tus datos.
6. **"Ignoro el aviso de certificado, solo es un aviso."** El aviso es justamente la señal de un posible MITM.
7. **Olvidar el kill switch:** si el túnel cae, el tráfico sale con tu IP real.
8. **Confundir HTTP con HTTPS en capturas:** HTTPS muestra ClientHello/SNI, no formularios.

---

## 6. Síntesis en tres capas

| Capa | Qué protege | Herramienta |
|---|---|---|
| **Local** | Lo guardado en tu equipo | Incógnito, borrar cookies, bloqueadores |
| **Red** | Lo que viaja | HTTPS/TLS, VPN, WPA3 |
| **Comportamiento** | Lo que hacés | Verificar nombres, MFA, desconfiar de redes abiertas |

**Tres reglas de oro (sugeridas):** 1) Verificá el nombre de la red y del sitio. 2) Usá HTTPS y VPN de confianza en redes ajenas. 3) Datos sensibles, mejor desde tu propia conexión, con MFA.

---

## 7. Puente a la próxima semana

Con la navegación y la conectividad bajo control, la próxima semana se continúa con el siguiente bloque del programa.
