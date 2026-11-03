# Guía de ejercicios — Semana 7

## Diplomatura en Ciberseguridad — Introducción al escaneo con Nmap

Esta guía tiene 15 ejercicios con su resolución: 1–2 repasan redes (CIDR y puertos); 3–4 estados de puertos y la mecánica TCP; 5–7 descubrimiento de hosts y costo de un escaneo; 8–10 servicios, versiones y sistema operativo; 11–12 elección de opciones y scripts NSE; 13 informe de auditoría; 14 ética y defensa; 15 programación en Python.

**Convenciones:** todo lo que dice `10.20.0.x`, `10.30.0.x` o `.tiendanova.lab` pertenece al laboratorio ficticio del kit. Las salidas que ves son extractos reales del laboratorio; en tu VM los tiempos, las latencias y la estimación del sistema operativo pueden variar levemente.

**Antes de empezar:** ninguno de los ejercicios requiere escanear nada fuera del laboratorio. Los que usan Nmap se ejecutan como `sudo ip netns exec auditor nmap ...`.

---

### Ejercicio 1 — Direcciones, máscaras y rangos (CIDR)

**Enunciado:** (a) ¿Cuántas direcciones tiene cada bloque y cuántos equipos se pueden direccionar? `/24`, `/26`, `/27`, `/22`, `/30`. (b) ¿Qué rango cubre `10.20.0.0/27`? (c) El apunte dice que un `/24` son «256 posibles dispositivos»: ¿es exacto? (d) Escribí en notación de Nmap: todos los equipos del 1 al 50 de la LAN del laboratorio, y la LAN entera excepto el auditor.

**Resolución:**
(a) Direcciones = 2^(32 − prefijo). Equipos utilizables = direcciones − 2 (dirección de red y de difusión), salvo en `/31` y `/32`.

| Bloque | Direcciones | Equipos utilizables |
|---|---|---|
| /24 | 256 | 254 |
| /26 | 64 | 62 |
| /27 | 32 | 30 |
| /22 | 1.024 | 1.022 |
| /30 | 4 | 2 |

(b) `/27` = bloques de 32: `10.20.0.0` a `10.20.0.31` (la `.0` es la red y la `.31` la difusión; utilizables `.1`–`.30`).
(c) Casi: son **256 direcciones**, de las cuales **254** son asignables a equipos. Nmap igualmente prueba las 256 (por eso el laboratorio informa «256 IP addresses»).
(d) `nmap -sn 10.20.0.1-50` y `nmap -sn 10.20.0.0/24 --exclude 10.20.0.10`.

---

### Ejercicio 2 — Puertos y servicios

**Enunciado:** Completá qué servicio suele corresponder a cada puerto y por qué su exposición a internet sería un hallazgo (o no): 21, 22, 23, 80, 139/445, 443, 631, 3306, 3389, 9100.

**Resolución:**

| Puerto | Servicio | ¿Hallazgo si está expuesto a internet? |
|---|---|---|
| 21/tcp | FTP (transferencia sin cifrado) | Sí: protocolo sin cifrado; revisar si hace falta |
| 22/tcp | SSH (administración remota) | Depende: aceptable si es necesario, con claves, MFA y restricción por origen |
| 23/tcp | Telnet | Sí, crítico: administración sin cifrado, obsoleta |
| 80/tcp | HTTP | No si el servidor es público; debería redirigir a 443 |
| 139, 445/tcp | NetBIOS / SMB (archivos compartidos de Windows) | Sí, crítico: nunca deberían salir a internet |
| 443/tcp | HTTPS | No, si es un servicio público |
| 631/tcp | IPP / CUPS (impresión) | Sí: una impresora no debe ser accesible desde internet |
| 3306/tcp | MySQL | Sí: una base de datos no debe estar expuesta; solo desde la aplicación |
| 3389/tcp | RDP (Escritorio Remoto) | Sí, crítico: objetivo habitual de ataques de fuerza bruta |
| 9100/tcp | Impresión directa (JetDirect) | Sí: ídem impresora |

**Idea clave:** el puerto es una *convención*, no una garantía. Un servicio puede escuchar en un puerto no estándar (por eso existe `-sV`), y un puerto abierto es **superficie de ataque**, no una vulnerabilidad por sí mismo.

---

### Ejercicio 3 — Los estados de un puerto y por qué se producen

**Enunciado:** Salida real contra el bastión (`sudo ip netns exec auditor nmap -Pn --reason -p 22,80,8080,8443 10.30.0.20`):

```text
PORT     STATE    SERVICE    REASON
22/tcp   open     ssh        syn-ack ttl 63
80/tcp   filtered http       no-response
8080/tcp closed   http-proxy reset ttl 63
8443/tcp open     https-alt  syn-ack ttl 63
```

(a) ¿Qué respondió el equipo en cada caso? (b) ¿Qué indica que el 80 sea `filtered` y el 8080 `closed` sobre el firewall? (c) Nmap tiene **seis** estados, no tres: nombralos. (d) ¿Qué significa `ttl 63`?

**Resolución:**
(a) 22 y 8443: respondieron **SYN/ACK** (hay una aplicación escuchando). 8080: respondió **RST** (el equipo está, pero nadie escucha; además el firewall lo rechaza con `reject with tcp reset`). 80: **no respondió nada**: el firewall descartó el paquete.
(b) Un puerto `filtered` revela un **firewall con política de descarte** (`drop`): no contesta ni siquiera con un rechazo. Un puerto `closed` indica que el paquete llegó a la pila TCP/IP del equipo. Entre ambos se puede **inferir la política del firewall** sin ver su configuración.
(c) `open`, `closed`, `filtered`, `unfiltered` (accesible pero no se sabe si abierto o cerrado; aparece con `-sA`), `open|filtered` (no se puede distinguir; típico de UDP y de `-sX/-sF/-sN`) y `closed|filtered` (propio del escaneo *idle*).
(d) El TTL (tiempo de vida) recibido es 63: el equipo inicia en 64 y el paquete cruzó **un router** (el gw) que restó 1. Es una pista de que el destino está en otra red.

---

### Ejercicio 4 — Leer un saludo TCP en una captura

**Enunciado:** Se capturó (`tcpdump -nn`) un escaneo `-sS` a los puertos 22 y 81 del servidor web:

```text
10.20.0.10.53529 > 10.20.0.20.22: Flags [S]
10.20.0.20.22 > 10.20.0.10.53529: Flags [S.]
10.20.0.10.53529 > 10.20.0.20.22: Flags [R]
10.20.0.10.53529 > 10.20.0.20.81: Flags [S]
10.20.0.20.81 > 10.20.0.10.53529: Flags [R.]
```

(a) ¿Qué puerto está abierto y cuál cerrado? Justificá con las banderas. (b) ¿Por qué el escáner envía un `[R]` en la línea 3? (c) En un escaneo `-sT` (connect) a los mismos puertos aparece, en el puerto 22, una tercera bandera `[.]` (ACK). ¿Qué cambia y qué consecuencia tiene para los registros del servidor? (d) ¿Por qué se llama «semiabierto» al `-sS`?

**Resolución:**
(a) **22 abierto**: respondió `[S.]` (SYN/ACK). **81 cerrado**: respondió `[R.]` (RST/ACK).
(b) El escáner ya obtuvo la respuesta que necesitaba (SYN/ACK = abierto) y **corta la conexión** con un RST antes de completar el saludo de tres pasos.
(c) `-sT` completa el saludo (SYN → SYN/ACK → **ACK**) usando la llamada `connect()` del sistema operativo, por lo que la aplicación del servidor **recibe una conexión completa** y es probable que la registre en su log. No requiere privilegios de administrador, a diferencia de `-sS`.
(d) Porque nunca completa la conexión: se queda en «medio» saludo. Por eso la aplicación suele no enterarse; no obstante **un firewall o un IDS sí lo detectan**, así que no es «invisible» (el apunte lo llama «sigilo relativo»).

---

### Ejercicio 5 — Descubrimiento de hosts: qué sondas se envían

**Enunciado:** (a) Al ejecutar `nmap -sn 10.20.0.20-22` en la LAN, se capturó `ARP, Request who-has 10.20.0.21 tell 10.20.0.10`. ¿Por qué ARP y no ICMP? (b) Al ejecutar `nmap -sn 10.30.0.20` (otra red, detrás de un router) se capturaron: ICMP echo request, TCP SYN al 443, TCP ACK al 80 e ICMP timestamp. ¿Por qué cambia la técnica? (c) Con `-sn` el bastión **no aparece** como activo, pero `-Pn` y `-PS8443` sí lo encuentran. ¿Por qué? (d) ¿Qué riesgo tiene usar siempre `-Pn`?

**Resolución:**
(a) En un **segmento local**, Nmap (con privilegios) usa **ARP**: es más rápido y *no se puede filtrar* —un equipo debe responder ARP para comunicarse—, por lo que descubre incluso equipos que ignoran el ping.
(b) Al otro lado de un router no hay ARP: Nmap envía la combinación por defecto de sondas: ICMP echo, SYN al 443, ACK al 80 e ICMP timestamp. Basta una respuesta para marcar el equipo como activo.
(c) El firewall del bastión descarta el ping y solo deja pasar el 22 y el 8443; los sondeos al 80 y al 443 caen en silencio, por lo que Nmap concluye «parece apagado». `-Pn` **omite el descubrimiento** y trata el equipo como activo; `-PS8443` envía el SYN al puerto que *sí* está abierto. Respuesta práctica: *«no responde al ping» ≠ «está apagado»*.
(d) Con `-Pn` se escanean los puertos de **todas** las direcciones, incluso las que no existen: un `/24` completo tarda mucho más (cada IP inexistente agota tiempos de espera) y genera más ruido.

---

### Ejercicio 6 — Costo de un escaneo

**Enunciado:** Se debe auditar un `/24` completo (254 equipos activos). Suponé una tasa sostenida de 1.000 sondas por segundo. Calculá cuántas sondas y cuánto tiempo requieren: (a) los 1.000 puertos por defecto, (b) `-F` (100 puertos), (c) `-p-` (65.535 puertos). (d) ¿Qué estrategia razonable se deduce?

**Resolución:**
Sondas = equipos × puertos; tiempo = sondas ÷ tasa (sin contar reintentos).

| Opción | Sondas | Tiempo a 1.000/s |
|---|---|---|
| Por defecto (1.000) | 254 × 1.000 = 254.000 | 254 s ≈ 4 min 14 s |
| `-F` (100) | 254 × 100 = 25.400 | 25,4 s |
| `-p-` (65.535) | 254 × 65.535 = 16.645.890 | 16.646 s ≈ **4 h 37 min** |

(d) **De lo general a lo particular**: primero descubrir equipos (`-sn`), luego escanear los puertos comunes de los activos y reservar `-p-` para los equipos críticos o sospechosos. En el laboratorio un `-p-` a un solo equipo tarda menos de un segundo porque la red es virtual; en una red real con latencia y firewalls, no.

---

### Ejercicio 7 — Qué dice un `Not shown`

**Enunciado:** Dos equipos devuelven: (A) `Not shown: 995 closed tcp ports (reset)` y (B) `Not shown: 997 filtered tcp ports (no-response)`. ¿Qué diferencia hay en lo que sabés de cada uno? ¿Cuál tiene un firewall delante? ¿Sirve `-sV` contra los puertos cerrados o filtrados?

**Resolución:**
(A) Casi todos los puertos **respondieron con RST**: no hay firewall que filtre; simplemente no hay servicios escuchando. (B) Casi todos **no responden**: hay un firewall que descarta (política `drop`) o el equipo está caído para esos puertos. El resultado (B) esconde información: no sabemos qué hay detrás; solo podemos ver los puertos que el firewall deja pasar (en el laboratorio, el bastión). `-sV` solo actúa sobre puertos **abiertos** (o `open|filtered`); no tiene a quién preguntar en los cerrados ni en los filtrados.

---

### Ejercicio 8 — Dos equipos, dos perfiles (casos A y B del apunte)

**Enunciado:** Escaneo por defecto del servidor web (`10.20.0.20`) y de la PC de oficina (`10.20.0.30`):

```text
10.20.0.20                      10.20.0.30
22/tcp   open  ssh              21/tcp   open  ftp
80/tcp   open  http             23/tcp   open  telnet
443/tcp  open  https            139/tcp  open  netbios-ssn
3306/tcp open  mysql            445/tcp  open  microsoft-ds
                                3389/tcp open  ms-wbt-server
```

Clasificá cada puerto como «esperable» o «a revisar» según la función de cada equipo y redactá una conclusión de dos líneas por equipo.

**Resolución:**
**Servidor web:** 80 y 443 son esperables (es su función). 22 es esperable solo si hace falta administrar el servidor de forma remota y debe restringirse por origen. **3306 (MySQL) es el hallazgo principal**: una base de datos no debería aceptar conexiones de toda la red, solo de la aplicación (idealmente `localhost`).
**PC de oficina:** una PC de usuario no necesita FTP (21) ni Telnet (23); **ambos** son protocolos sin cifrado. 139/445 (archivos compartidos) y 3389 (Escritorio Remoto) pueden tener un uso legítimo, pero con ese conjunto de puertos el equipo es un **objetivo clásico** de movimiento lateral y de ransomware. Conclusión: casi toda la lista es «a revisar» bajo el criterio del *mínimo servicio necesario*.

**Idea clave:** el mismo puerto puede ser normal en un equipo y un hallazgo en otro. Se evalúa contra la **función esperada** del equipo.

---

### Ejercicio 9 — Versiones y vulnerabilidades conocidas

**Enunciado:** `sudo ip netns exec auditor nmap -sV 10.20.0.20` y `... 10.20.0.30` devuelven:

```text
22/tcp   open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http     Apache httpd 2.4.49 ((Unix))
443/tcp  open  ssl/http Apache httpd 2.4.49 ((Unix))
3306/tcp open  mysql    MySQL 5.5.62-0ubuntu0.14.04.1
21/tcp   open  ftp      vsftpd 2.3.4
```

(a) ¿Qué conviene investigar de cada versión? (b) ¿Por qué un auditor **no debe afirmar** «es vulnerable» solo por el número de versión? (c) ¿Qué pasos siguen antes de escribirlo en el informe?

**Resolución:**
(a) **Apache 2.4.49**: versión afectada por CVE-2021-41773 (recorrido de rutas con posible ejecución remota); el arreglo inicial (2.4.50) resultó incompleto y se corrigió en 2.4.51 (CVE-2021-42013). **vsftpd 2.3.4**: el paquete distribuido en 2011 contenía una **puerta trasera** (CVE-2011-2523). **MySQL 5.5.x**: rama sin soporte desde fin de 2018. **OpenSSH 8.2p1**: antigua; revisar el estado del paquete de la distribución.
(b) Porque las distribuciones (Debian, Ubuntu, Red Hat) **parchean sin cambiar el número de versión** (*backports*): un `9.2p1` puede estar corregido y un `2.4.49` puede ser un servicio propio. Además, **el banner es texto configurable**: puede mentir o estar ocultado.
(c) Confirmar contra la fuente: paquete instalado (`apt policy`, `dpkg -l`), changelog de seguridad de la distribución, base de CVE (NVD) y, si hay autorización, una verificación controlada. En el informe: *«El banner indica Apache 2.4.49, afectada por CVE-2021-41773; verificar versión real del paquete»*.

> En el laboratorio los banners son **simulados**: no hay software vulnerable real detrás.

---

### Ejercicio 10 — ¿Qué sistema operativo es? Evidencias que se contradicen

**Enunciado:** Contra la PC de oficina, `-sV` informa `Service Info: OSs: Unix, Linux, Windows` (y detecta `ms-wbt-server Microsoft Terminal Services`), mientras que `-O --osscan-guess` propone `Linux 5.3 - 5.4 (96 %)`. (a) ¿Por qué `-sV` y `-O` pueden discrepar? (b) ¿Qué condición necesita `-O` para funcionar bien? (c) Al ejecutar `nmap -A -p 22,80 10.20.0.20` aparece `Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port`. ¿Qué indica y cómo se corrige? (d) ¿Qué diferencia hay entre `-o` y `-O`?

**Resolución:**
(a) Se miran cosas distintas: `-sV` interpreta los **banners y respuestas de las aplicaciones** (que pueden estar simulados, traducidos por un proxy o configurados a propósito); `-O` analiza el comportamiento de la **pila TCP/IP** (tamaño de ventana, opciones TCP, TTL, números de secuencia) del kernel real. En el laboratorio la PC «parece Windows» por sus servicios pero es un Linux por su pila: es una simulación, y en la vida real ocurre con *proxies*, redes traducidas (NAT), *honeypots* o servicios deliberadamente falseados. **Una contradicción es un dato**: hay que investigarla, no promediarla.
(b) Necesita al menos **un puerto abierto y uno cerrado** para sus pruebas.
(c) Se limitó el escaneo a dos puertos abiertos: no hubo ninguno cerrado donde probar. Se corrige escaneando un rango que incluya puertos cerrados (por ejemplo el escaneo por defecto: `-O` sin `-p`).
(d) `-o` (minúscula: `-oN`, `-oX`, `-oG`, `-oA`) **guarda resultados en archivos**. `-O` (mayúscula) **detecta el sistema operativo**.

> La estimación de `-O` depende de la base de huellas de tu versión de Nmap: con kernels recientes puede decir «No exact OS matches» y sugerir una familia (Linux). La familia es el dato confiable; la versión exacta, no.

---

### Ejercicio 11 — Elegir las opciones correctas

**Enunciado:** Escribí el comando (contra el laboratorio) para cada necesidad. (a) Inventario rápido de la LAN sin escanear puertos. (b) Todos los puertos TCP del servidor web, guardando los resultados en los tres formatos. (c) Escanear el bastión aunque no responda al ping, mostrando el motivo de cada estado. (d) Ver qué nombres DNS tiene el rango `10.20.0.0/29` **sin enviar ni un paquete** a los equipos. (e) Comprobar si el gateway ofrece DNS por UDP. (f) Versión de servicios solo de los puertos abiertos de la impresora, con salida limpia. (g) Escanear sin resolver nombres (más rápido). (h) El comando del checkpoint del apunte es `sudo nmap -sX -sV -O [IP]`: ¿es una buena elección para una auditoría?

**Resolución:**
(a) `nmap -sn 10.20.0.0/24`
(b) `nmap -p- -oA servidor_web 10.20.0.20` (genera `.nmap`, `.xml` y `.gnmap`).
(c) `nmap -Pn --reason 10.30.0.20`
(d) `nmap -sL 10.20.0.0/29` (*list scan*: solo resuelve nombres; no envía sondas al objetivo).
(e) `nmap -sU -p 53 10.20.0.1`
(f) `nmap -sV --open 10.20.0.40`
(g) `nmap -n ...` (por ejemplo `nmap -n -sn 10.20.0.0/24`).
(h) **No es la mejor elección.** `-sX` (*Xmas*) envía paquetes con banderas anómalas (FIN, PSH, URG) y sirve para estudiar cómo responde un firewall o para evadirlos, no para inventariar. Contra Linux, los puertos abiertos aparecen como `open|filtered` (en el laboratorio, `-sX` solo mostró `open|filtered`); suele ser **más lento**, **más ruidoso** (es una firma clásica para un IDS) y **no funciona igual** contra Windows (que responde RST a todo). Para el checkpoint, el comando adecuado es `sudo nmap -sS -sV -O [IP]` (o simplemente `sudo nmap -sV -O [IP]`).

---

### Ejercicio 12 — Scripts NSE

**Enunciado:** (a) ¿Qué hace `-sC`? (b) Extracto de `-sC` contra el puerto 443 del servidor web (comando `nmap -sC -v -p 443 10.20.0.20`, extracto):

```text
443/tcp  open  https
| ssl-cert: Subject: commonName=tienda-web.lab/organizationName=TiendaNova Lab
| Subject Alternative Name: DNS:tienda-web.lab
| Issuer: commonName=tienda-web.lab/organizationName=TiendaNova Lab
| Not valid before: 2026-11-02T20:30:58
|_Not valid after:  2027-11-02T20:30:58
|_http-title: TiendaNova - Tienda en linea
```
¿Qué datos útiles para la auditoría aparecen? (c) ¿Qué categorías de scripts evitarías en un servidor en producción sin autorización expresa? (d) ¿Cómo se ve la ayuda de un script?

**Resolución:**
(a) `-sC` equivale a `--script=default`: ejecuta los scripts de la categoría **default**, que se consideran útiles y relativamente seguros (título web, certificado, banners).
(b) Del certificado: el **nombre del sitio**, su **vigencia** (un año) y el título de la página. Con `-v` el script agrega el emisor (`Issuer: commonName=tienda-web.lab`), igual al sujeto: el certificado es **autofirmado**. Para un servicio público, eso es un hallazgo (los navegadores mostrarán una advertencia).
(c) `intrusive`, `dos` (denegación de servicio), `exploit`, `brute` (fuerza bruta de credenciales) y `fuzzer`: pueden afectar al servicio o bloquear cuentas. Las categorías `safe`, `default`, `discovery` y `version` son las apropiadas para empezar.
(d) `nmap --script-help ssl-cert`

---

### Ejercicio 13 — Redactar un hallazgo (la impresora «olvidada»)

**Enunciado:** `nmap -sV 10.20.0.40` devuelve:

```text
80/tcp   open  http       Embedded HTTP Server 1.0
631/tcp  open  ipp        CUPS 2.4
9100/tcp open  jetdirect?
```
La impresora no tiene nombre en el DNS y nadie la tenía en el inventario. Redactá el hallazgo (¿qué es?, ¿por qué importa?, recomendación) y corregí esta frase de un informe: *«Creo que la impresora es peligrosa porque tiene muchos puertos.»*

**Resolución:**
- **¿Qué es?** Un dispositivo de impresión (puertos 80 con panel web, 631/IPP y 9100/impresión directa) que está activo en la red `10.20.0.0/24`, **sin registro DNS ni inventario**.
- **¿Por qué importa?** Es un activo **no gestionado** (CIS Controls v8, control 1: inventario de activos). Expone un panel web con versión y tres servicios de impresión sin que exista un responsable de actualizarlos; los dispositivos de impresión suelen quedar sin parches y con credenciales por defecto.
- **Recomendación:** (1) identificar al propietario y registrar el activo; (2) deshabilitar los servicios que no se usen (por ejemplo el 80 si no hay administración web, o restringirlo); (3) limitar el acceso a los puertos 631/9100 a la subred de impresión o a los equipos que imprimen; (4) cambiar credenciales por defecto y actualizar el *firmware*.
- **Corrección de la frase:** *«El dispositivo 10.20.0.40 expone tres servicios de impresión (80, 631 y 9100) sin gestión registrada. Representa un riesgo de seguridad según la política de “mínimo servicio necesario”, ya que ofrece una superficie de ataque no inventariada.»* (Se cita un **criterio** en lugar de una opinión.)

---

### Ejercicio 14 — Ética, legalidad y defensa

**Enunciado:** (a) ¿Cuáles de estos escaneos están autorizados? (1) El laboratorio de la clase; (2) tu red doméstica; (3) el router del vecino «solo para ver»; (4) los servidores de una empresa que te contrató con un contrato de alcance escrito; (5) los servidores de una empresa «porque tienen un programa de recompensas», sin leer sus reglas. (b) ¿Qué debe incluir una autorización? (c) Desde el **lado defensivo**: aplicá las reglas siguientes en el servidor web del laboratorio, volvé a escanear y explicá qué cambió.

```bash
sudo ip netns exec web nft -f - <<'NFT'
table inet remediacion {
  chain input {
    type filter hook input priority 0; policy drop;
    iif "lo" accept
    ct state established,related accept
    icmp type echo-request accept
    tcp dport { 80, 443 } accept
    ip saddr 10.20.0.30 tcp dport 22 accept
  }
}
NFT
sudo ip netns exec auditor nmap -p 22,80,443,3306 10.20.0.20
```

**Resolución:**
(a) Autorizados: (1), (2) y (4). **No** lo están (3) y (5): sin permiso del titular, «solo para ver» no cuenta, y un programa de recompensas autoriza **solo lo que sus reglas dicen** (alcance, técnicas permitidas). En Argentina, el acceso sin autorización a un sistema o dato informático está tipificado (Código Penal, art. 153 bis, incorporado por la Ley 26.388), y el país aprobó el Convenio de Budapest sobre ciberdelito (Ley 27.411). Un escaneo de puertos aislado no siempre constituye delito, pero puede ser interpretado como un acto hostil por el titular o el proveedor de internet; la regla práctica es **no hacerlo sin permiso**.
(b) Quién autoriza y su cargo; **alcance** (IP, dominios, segmentos); técnicas permitidas y prohibidas (por ejemplo, sin `dos` ni `exploit`); **fechas y horarios**; contacto de emergencia; tratamiento de la información obtenida.
(c) Resultado esperado:

```text
22/tcp   filtered ssh        (solo se permite desde 10.20.0.30; el auditor queda afuera)
80/tcp   open     http
443/tcp  open     https
3306/tcp filtered mysql      (la base de datos ya no es alcanzable desde la red)
```
Con `policy drop`, todo lo que no se permite **se descarta en silencio**, y desde afuera aparece como `filtered`. Es la verificación clásica de una remediación: **volver a escanear** y comprobar que el hallazgo desapareció. (Para volver al estado original: `sudo ip netns exec web nft delete table inet remediacion`.)

---

### Ejercicio 15 — Python: detectar un barrido de puertos

**Enunciado:** Un escaneo aparece en una captura como muchos `SYN` desde un mismo origen hacia **muchos puertos distintos** de un mismo destino. Escribí `detectar_escaneos(lineas, umbral=15)`: recibe líneas de texto de `tcpdump -nn` (por ejemplo `IP 10.20.0.10.53529 > 10.20.0.20.22: Flags [S], seq ...`) y devuelve `{(origen, destino): cantidad_de_puertos_distintos}` para los pares que alcanzan el umbral. Solo deben contarse los SYN «puros» (`Flags [S]`), no los SYN/ACK de las respuestas (`Flags [S.]`).

**Resolución (archivo `solucion_detectar_escaneo.py`):**

```python
import re
from collections import defaultdict

PATRON = re.compile(r"IP (\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+): Flags \[S\],")

def detectar_escaneos(lineas, umbral=15):
    puertos = defaultdict(set)
    for linea in lineas:
        m = PATRON.search(linea)
        if m:
            origen, _, destino, pdst = m.groups()
            puertos[(origen, destino)].add(int(pdst))
    return {par: len(p) for par, p in puertos.items() if len(p) >= umbral}
```

**Justificación:** se usa un **conjunto** por par origen–destino para contar puertos *distintos* (50 SYN al mismo puerto 443 no son un escaneo; 30 SYN a 30 puertos diferentes, sí). El patrón `Flags \[S\],` descarta los `[S.]` de las respuestas. Probado contra una captura real de `nmap -sS 10.20.0.30` del laboratorio: informó *«10.20.0.10 probó 1000 puertos distintos en 10.20.0.30»* (los 1.000 puertos por defecto).
**Limitaciones:** el umbral fijo genera falsos positivos (un *balanceador* o una herramienta de monitoreo legítima) y falsos negativos (escaneos lentos, repartidos en el tiempo o desde varias IP: `-T0`, `-T1`, fuentes distribuidas). Un detector real usa **ventanas de tiempo** y correlación (por eso existen Suricata, Zeek y Snort).

---

### Entregable: Reporte de auditoría de red local (checkpoint)

El apunte pide un PDF (o Markdown) con el análisis de **al menos 2 dispositivos**: IP y MAC, sistema operativo (`-O`), tabla de puertos/estado/versión (`-sV`) y, por equipo, ¿qué es?, ¿por qué importa? y recomendación. El kit incluye un **generador de esqueleto** que arma las tablas a partir del XML de Nmap; **el análisis lo escribís vos**:

```bash
sudo ip netns exec auditor nmap -sV -O --osscan-guess -oA dispositivos 10.20.0.20 10.20.0.30
python3 reporte/nmap_a_markdown.py dispositivos.xml --autor "Tu nombre" > reporte.md
```

Para convertirlo a PDF: abrí `reporte.md` en cualquier editor de Markdown del equipo anfitrión y exportalo, o en Debian usá `pandoc reporte.md -o reporte.pdf` (necesita `texlive` instalado).
