# Guía de ejercicios — Semana 6

## Diplomatura en Ciberseguridad — Seguridad en la web y conectividad

Esta guía tiene 14 ejercicios: 1–3 huella digital y navegación privada; 4–9 HTTP, HTTPS, TLS y certificados; 10–12 VPN; 13 Wi-Fi pública y 14 programación en Python. Cada ejercicio incluye su resolución justificada.

**Convenciones:** todo nombre `.test` y toda IP `203.0.113.x`, `198.51.100.x` o `10.x` pertenece al laboratorio ficticio. Un **bit de identificación** reduce a la mitad el grupo de personas entre las que podrías ser: con **b** bits, el grupo se divide por 2ᵇ.

---

### Ejercicio 1 — ¿Qué se borra y qué no?

**Enunciado:** Para cada rastro indicá (a) quién lo guarda, (b) si el modo incógnito lo elimina al cerrar la ventana y (c) si un sitio lo puede seguir viendo igual: dirección IP, historial, cookies, huella del navegador (fingerprinting).

**Resolución:**

| Rastro | Quién lo guarda | ¿Lo borra el incógnito? | ¿El sitio lo sigue viendo? |
|---|---|---|---|
| IP | El sitio y tu proveedor (la IP es necesaria para responderte) | No aplica: no se guarda en tu equipo | **Sí**, siempre |
| Historial | Tu navegador (local) | **Sí** (no lo guarda) | No lo ve el sitio, pero sí tu proveedor y tu red |
| Cookies | Tu navegador, a pedido del sitio | **Sí**, al cerrar la ventana | Dentro de la sesión sí; luego te ve como visitante nuevo |
| Huella (fingerprinting) | **Nadie en tu equipo**: la calcula el sitio con lo que tu navegador envía | **No** | **Sí**: es igual en cada visita |

**Idea clave:** incógnito borra lo que está guardado en *tu* equipo. La huella no está guardada: se recalcula cada vez.

---

### Ejercicio 2 — Verdadero o falso

**Enunciado:** Justificá cada afirmación.

a) En modo incógnito, mi proveedor de internet no ve los sitios que visito.
b) En incógnito, si inicio sesión en Google, Google sabe que soy yo.
c) Con una VPN, mi navegador deja de guardar el historial.
d) Si uso la computadora de la escuela en incógnito, la escuela no ve lo que hago.

**Resolución:**
- a) **Falso.** Incógnito actúa solo en tu equipo; el proveedor ve los destinos.
- b) **Verdadero.** La sesión iniciada identifica tu cuenta, uses o no incógnito.
- c) **Falso.** El historial es una función del navegador; la VPN actúa sobre la red. Para no guardar historial hace falta incógnito (o borrarlo).
- d) **Falso.** La red y los equipos de la escuela pueden registrar destinos, y el equipo puede tener monitoreo.

---

### Ejercicio 3 — Cuántos bits te identifican

**Enunciado:** Hay unos 8.000 millones de personas. (1) ¿Cuántos bits de información identifican a una persona entre todas? (2) Un navegador entrega estos atributos, con la cantidad de valores que se reparten entre los usuarios (supongamos independientes): *User-Agent*: 1.024 · idioma: 16 · zona horaria: 8 · resolución de pantalla: 32 · conjunto de fuentes: 4.096. ¿Cuántos bits aporta cada uno y cuántos suman? (3) ¿Alcanza para identificarte?

**Resolución:**
1. **log₂(8 × 10⁹) ≈ 32,9 bits.**
2. Bits = log₂(valores): User-Agent **10**, idioma **4**, zona horaria **3**, pantalla **5**, fuentes **12**. Total: **34 bits**.
3. **Sí**, en teoría: 34 > 32,9. Los datos reales no son independientes (hay correlación) y las poblaciones no se reparten uniformemente, pero con más atributos (canvas, WebGL, complementos) la huella se vuelve casi única. Ningún dato por separado identifica; **la combinación sí**.

**Verificación en el laboratorio:** `curl -s http://tiendanova.test/huella` muestra la huella calculada con cuatro encabezados y su hash. Con otro `-A` (User-Agent) cambia.

---

### Ejercicio 4 — HTTP vs HTTPS en una captura

**Enunciado:** Un espía en la red de la cafetería obtuvo estas dos líneas con `analizar_trafico.py`:

```text
10.10.0.2 -> 198.51.100.20  POST /login HTTP/1.1  Host=tiendanova.test  User-Agent=curl/8.5.0
      [!] DATO EXPUESTO: usuario = laura
      [!] DATO EXPUESTO: clave = Secreta123
...
10.10.0.2 -> 198.51.100.20  ClientHello  nombre del sitio (SNI) visible: tiendanova.test
```

a) ¿Cuál de las dos conexiones es HTTP y cuál HTTPS? b) ¿Qué pudo leer el espía en cada una? c) ¿Qué debería hacer Laura con esa contraseña?

**Resolución:**
- a) La primera es **HTTP** (se ve el método, la ruta y el formulario en claro); la segunda es **HTTPS** (solo se observa el saludo inicial de TLS).
- b) En HTTP: el sitio, la ruta `/login`, el User-Agent, **usuario y clave**. En HTTPS: la IP de destino, el nombre del sitio (SNI), tiempos y volumen; **no** la ruta, el formulario ni la clave.
- c) Considerarla **comprometida**: cambiarla en este y en cualquier sitio donde la reutilizó, y activar MFA (Semana 5).

---

### Ejercicio 5 — Ordená el saludo TLS y su visibilidad

**Enunciado:** Ordená los pasos de una conexión TLS 1.3 y marcá cuáles viajan **sin cifrar**: *ClientHello con el SNI · datos de la aplicación (HTTP) · el servidor presenta su certificado · ambos derivan la clave de sesión · el cliente verifica el certificado*.

**Resolución:**
1. **ClientHello con el SNI** — sin cifrar (el nombre del sitio queda visible, salvo ECH).
2. **Respuesta del servidor** (negociación de claves); en TLS 1.3 el certificado ya viaja **cifrado**.
3. **El servidor presenta su certificado.**
4. **El cliente verifica el certificado** (firma de la CA, dominio, vigencia).
5. **Ambos derivan la clave de sesión** (nunca se envía por la red).
6. **Datos de la aplicación (HTTP)** — cifrados.

**Nota docente:** en TLS 1.2 el certificado sí viajaba en claro; en TLS 1.3 el intercambio de claves es anterior y casi todo lo posterior al ClientHello queda cifrado.

---

### Ejercicio 6 — Leer un certificado

**Enunciado:** Salida de `openssl x509` sobre el certificado del dominio del laboratorio:

```text
subject=CN = tiendanova-login.test
issuer=O = TiendaNova Lab, CN = TiendaNova Lab CA
notBefore=Oct 26 20:46:33 2026 GMT
notAfter=Jan 24 20:46:33 2027 GMT
X509v3 Subject Alternative Name:
    DNS:tiendanova-login.test
```

a) ¿Para qué nombre vale? b) ¿Quién lo firmó? c) ¿Cuántos días dura? d) ¿Un navegador lo aceptaría hoy (26/10/2026) si confiara en esa CA? e) ¿Y si lo presentara el sitio `tiendanova.test`?

**Resolución:**
- a) Para **`tiendanova-login.test`** únicamente (el campo SAN manda).
- b) La autoridad de laboratorio **TiendaNova Lab CA**.
- c) Del 26/10/2026 al 24/1/2027: **90 días**.
- d) **Sí** (está dentro de la vigencia y la firma es válida, si la CA es de confianza).
- e) **No**: el nombre no coincide con el SAN. curl lo informa: `SSL: no alternative certificate subject name matches target host name`.

---

### Ejercicio 7 — El candado no es honestidad

**Enunciado:** Clasificá cada caso como *"conexión cifrada y sitio legítimo"*, *"conexión cifrada pero sitio fraudulento"* o *"conexión no confiable"* y explicá:

a) `https://tiendanova.test` con certificado de la CA de laboratorio (que tu equipo reconoce).
b) `https://tiendanova-login.test:8443` con certificado válido de la misma CA.
c) `https://autofirmado.test:9443` con un certificado autofirmado.
d) `http://tiendanova.test`.

**Resolución:**

| Caso | Clasificación | Por qué |
|---|---|---|
| a | Cifrada y legítima | Dominio correcto y firma válida |
| b | **Cifrada pero fraudulenta** (en el escenario de phishing) | La CA solo comprueba que el solicitante controla *ese dominio parecido*. El candado aparece igual |
| c | No confiable | Nadie avala el certificado; curl: `SSL certificate problem: self-signed certificate` |
| d | Sin cifrado | Cualquiera en el camino lee y modifica |

**Verificación:** el script `verificar_lab.sh` comprueba los tres comportamientos.

---

### Ejercicio 8 — HSTS y la primera visita

**Enunciado:** Un sitio responde: `Strict-Transport-Security: max-age=31536000; includeSubDomains`. (1) ¿Cuántos días recordará el navegador usar HTTPS? (2) ¿Qué ataque evita? (3) ¿Por qué la *primera* visita sigue siendo vulnerable sin la lista *preload*?

**Resolución:**
1. 31.536.000 s ÷ 86.400 = **365 días**; `includeSubDomains` extiende la regla a todos los subdominios.
2. El **SSL stripping**: un atacante que intercepta el `http://` inicial y elimina la redirección a `https://`. Con HSTS, el navegador no hace el pedido por HTTP.
3. Porque el navegador aprende la regla **al ver el encabezado por HTTPS**. Si nunca visitó el sitio, su primer pedido puede ser HTTP. La lista *preload* incluida en el navegador cubre ese hueco.

**Verificación:** `curl --hsts hsts.txt https://tiendanova.test/ip` y luego `curl --hsts hsts.txt -w '%{url_effective}\n' http://tiendanova.test/ip` devuelve una URL `https://…`.

---

### Ejercicio 9 — Renovar certificados

**Enunciado:** El calendario del CA/Browser Forum fija una validez máxima de **200 días** desde el 15/3/2026, **100 días** desde el 15/3/2027 y **47 días** desde el 15/3/2029. ¿Cuántas emisiones por año como mínimo necesita un sitio en cada etapa? ¿Qué implica para la operación?

**Resolución:**
- 365 ÷ 200 = 1,8 → **2** emisiones por año.
- 365 ÷ 100 = 3,65 → **4** emisiones por año.
- 365 ÷ 47 = 7,8 → **8** emisiones por año (en la práctica más, porque se renueva antes del vencimiento).
- Implicancia: la renovación **manual deja de ser viable**; hay que automatizarla (protocolo ACME, Certbot, Let's Encrypt) y **monitorear la fecha de vencimiento**. Un certificado vencido provoca advertencias o caídas del servicio.

---

### Ejercicio 10 — ¿Quién ve qué?

**Enunciado:** Laura se conecta desde la cafetería a `http://tiendanova.test` y luego a `https://tiendanova.test`. Completá qué ve cada observador **sin VPN** y **con VPN**. Observadores: red de la cafetería (espía), proveedor de internet, sitio destino, proveedor de VPN.

**Resolución:**

| Observador | Sin VPN, HTTP | Sin VPN, HTTPS | Con VPN (cualquiera de los dos) |
|---|---|---|---|
| Red de la cafetería | Todo: sitio, ruta, clave | IP y SNI de destino, tiempos, volumen | Solo que hay un túnel hacia el servidor VPN (UDP/51820 en el laboratorio) |
| Proveedor de internet | Igual que la cafetería | IP y SNI de destino | Solo el servidor VPN |
| Sitio destino | IP de la cafetería (203.0.113.2) | IP de la cafetería | **IP del servidor VPN (203.0.113.10)** |
| Proveedor de VPN | No participa | No participa | **Ve el destino; y el contenido si es HTTP** |

**Idea clave:** la VPN **cambia de observador**. En HTTP el proveedor de VPN ve la clave; por eso VPN no reemplaza a HTTPS.

---

### Ejercicio 11 — El costo de un túnel: MTU

**Enunciado:** WireGuard agrega ≈ 60 bytes por paquete sobre IPv4 y ≈ 80 bytes sobre IPv6 (cabeceras IP, UDP y WireGuard). Con un enlace de MTU 1500: (1) ¿Qué MTU debe tener la interfaz del túnel para no fragmentar si el túnel puede ir sobre IPv6? (2) ¿Y solo sobre IPv4? (3) ¿Qué síntoma verías con un MTU mal configurado?

**Resolución:**
1. 1500 − 80 = **1420** (es el valor por defecto de WireGuard y el que muestra el laboratorio: `mtu 1420`).
2. 1500 − 60 = **1440**.
3. Páginas que cargan a medias o conexiones que se cuelgan al transferir datos grandes (los paquetes grandes se descartan por fragmentación), aunque los pings pequeños funcionen.

---

### Ejercicio 12 — Fugas y kill switch

**Enunciado:** (1) Explicá qué ocurrió en el laboratorio cuando se borró la interfaz `wgc0` sin kill switch y qué cambió con él. (2) Interpretá estas reglas:

```text
table inet killswitch {
  chain output {
    type filter hook output priority 0; policy drop;
    oifname "lo" accept
    oifname "wgc0" accept
    ip daddr 203.0.113.10 udp dport 51820 accept
  }
}
```

**Resolución:**
1. **Sin kill switch**, al caer el túnel el sistema volvió a su ruta normal y el pedido salió por la red de la cafetería: el sitio vio **203.0.113.2** (IP real, fuga). **Con kill switch**, no hay ruta permitida y el pedido expiró (`curl` terminó por tiempo de espera, código 28).
2. `policy drop`: todo lo que sale se **descarta por defecto**. Se permite solo: el tráfico local (`lo`), el que sale por la interfaz del túnel (`wgc0`) y los paquetes UDP al servidor VPN en el puerto 51820 (necesarios para **reconectar**). Defensa relacionada con TunnelVision (CVE-2024-3661): bloquear lo que no va por el túnel.

---

### Ejercicio 13 — Informe forense de una Wi-Fi

**Enunciado:** `analizar_wifi.py` entregó:

```text
  CafeNova_Gratis        aa:bb:cc:00:00:01       6  WPA2/RSN
  CafeNova_Gratis        de:ad:be:ef:00:66      11  ABIERTA
  ...
  [!] 60 tramas de desautenticación desde aa:bb:cc:00:00:01
Mensajes EAPOL (apretón de manos WPA2): 4
```

(a) ¿Cuál es la red legítima y cuál la gemela? (b) ¿Por qué hay tramas de desautenticación "desde la red legítima"? (c) ¿Qué haría un usuario para protegerse? (d) Escribí tus **3 reglas de oro**.

**Resolución:**
- a) La legítima es la **protegida con WPA2 (BSSID aa:bb:…:01, canal 6)**; la gemela es **abierta (de:ad:…:66, canal 11)**. Mismo nombre y distinta seguridad es la señal clásica.
- b) El atacante **falsifica** la dirección MAC de la red legítima para enviar la desautenticación: los clientes creen que "la red los expulsa", se desconectan y, al reconectar, eligen la gemela. (La protección de tramas de gestión, 802.11w, que es obligatoria en WPA3, lo dificulta.)
- c) Verificar el nombre exacto con el local; no usar redes abiertas para lo sensible; VPN o datos móviles; desactivar la conexión automática; MFA o passkeys por si se roba una credencial.
- d) Respuesta libre. Ejemplo: 1) *Verifico el nombre exacto de la red con el local.* 2) *Activo la VPN antes de abrir correo o banco; solo sitios HTTPS.* 3) *Desactivo la conexión automática y olvido la red al irme.*

---

### Ejercicio 14 — Python: detectar redes gemelas

**Enunciado:** Escribí `detectar_gemelas(redes)`, donde `redes` es una lista de diccionarios `{"ssid", "bssid", "seguridad"}`. Debe devolver `{ssid: [bssid, ...]}` para cada SSID anunciado por **varios BSSID con seguridad distinta**. Un SSID repetido con **la misma** seguridad (por ejemplo, un repetidor legítimo) **no** debe marcarse.

**Resolución:**

```python
def detectar_gemelas(redes):
    grupos = {}
    for r in redes:
        grupos.setdefault(r["ssid"], []).append(r)
    sospechosos = {}
    for ssid, lista in grupos.items():
        if len({r["seguridad"] for r in lista}) > 1:
            sospechosos[ssid] = sorted(r["bssid"] for r in lista)
    return sospechosos


if __name__ == "__main__":
    redes = [
        {"ssid": "CafeNova_Gratis", "bssid": "aa:bb:cc:00:00:01", "seguridad": "WPA2"},
        {"ssid": "CafeNova_Gratis", "bssid": "de:ad:be:ef:00:66", "seguridad": "ABIERTA"},
        {"ssid": "Libreria_WiFi",   "bssid": "aa:bb:cc:00:00:02", "seguridad": "WPA2"},
        {"ssid": "Libreria_WiFi",   "bssid": "aa:bb:cc:00:00:12", "seguridad": "WPA2"},  # repetidor legítimo
    ]
    assert detectar_gemelas(redes) == {"CafeNova_Gratis": ["aa:bb:cc:00:00:01", "de:ad:be:ef:00:66"]}
    assert detectar_gemelas([]) == {}
    print("OK")
```

**Justificación:** agrupar por SSID es O(n). Se compara el **conjunto** de seguridades: si hay más de una, hay sospecha. **Limitación:** un atacante astuto puede copiar también la seguridad (una gemela WPA2 con otra clave); por eso conviene sumar otras señales: BSSID desconocido, canal inesperado, ráfagas de desautenticación y señal anormalmente fuerte.

---

### Cierre de la guía: el entregable en GitHub

El README.md de `practica-wifi-segura` debe tener: **Introducción, Sitio analizado, Evidencia observada, Riesgos encontrados, Cómo ayuda una VPN y 3 Reglas de Oro.** Usá `informe/plantilla_README.md` del kit. Sin interfaz gráfica, la evidencia que el apunte pide ver en las herramientas del navegador (URL, método, host, protocolo, encabezados) se obtiene con:

```bash
curl -sv -o /dev/null http://neverssl.com 2>&1 | grep -E '^[<>*]'
```

**Honestidad técnica:** pegá solo fragmentos cortos, sin datos personales, y aclará qué no pudiste comprobar.
