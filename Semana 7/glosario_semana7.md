# Glosario de términos y fórmulas — Semana 7

## Introducción al escaneo con Nmap

---

## 1. Términos

### 1.1 Conceptos de red

| Término | Definición | Ejemplo / nota |
|---|---|---|
| **Host (equipo)** | Cualquier dispositivo conectado a la red con una dirección IP. | Laptop, servidor, impresora, Smart TV. |
| **Dirección IP** | Identificador lógico de un host en la red. | 10.20.0.20 |
| **Dirección MAC** | Identificador físico de la tarjeta de red; solo es visible dentro del mismo segmento local. | 02:00:00:00:00:20 |
| **Puerto** | Número (0–65535) que identifica un servicio dentro de un host. Hay 65.535 utilizables (1–65535). | 22 (SSH), 80 (HTTP), 443 (HTTPS). |
| **Puertos bien conocidos / registrados / dinámicos** | 0–1023 / 1024–49151 / 49152–65535. | |
| **Servicio** | Programa que escucha en un puerto y atiende conexiones. | Apache, OpenSSH, MySQL. |
| **Banner** | Texto con el que un servicio se presenta al conectarse; suele incluir nombre y versión. | `SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5` |
| **CIDR** | Notación `dirección/prefijo` para describir un rango de red. | 10.20.0.0/24 |
| **Segmento / subred** | Grupo de equipos que se alcanzan sin pasar por un router. | LAN 10.20.0.0/24 |
| **Gateway (puerta de enlace)** | Router que conecta un segmento con otros. | 10.20.0.1 |
| **DMZ** | Zona intermedia donde se ubican servicios expuestos, separada de la red interna por un firewall. | 10.30.0.0/24 |
| **ARP** | Protocolo que traduce una IP en una MAC dentro del segmento local. | `who-has 10.20.0.21 tell 10.20.0.10` |
| **ICMP** | Protocolo de control y diagnóstico (el «ping» es *echo request*). | |
| **TTL** | Contador que disminuye en cada router; sirve para estimar la distancia. | `ttl 63` = 64 − 1 salto |
| **DNS inverso (PTR)** | Consulta que traduce una IP en un nombre. | `web.tiendanova.lab` |
| **Firewall (cortafuegos)** | Sistema que permite o bloquea tráfico según reglas. | `nftables` |
| **Política drop / reject** | *drop*: descarta en silencio (el puerto aparece *filtered*); *reject*: rechaza y avisa (RST o ICMP). | |

### 1.2 TCP y UDP

| Término | Definición | Ejemplo / nota |
|---|---|---|
| **TCP** | Protocolo orientado a conexión: establece, mantiene y cierra sesiones. | |
| **Saludo de tres pasos (3-way handshake)** | SYN → SYN/ACK → ACK; así se abre una conexión TCP. | |
| **SYN / SYN-ACK / ACK / RST / FIN** | Banderas TCP: iniciar, aceptar, confirmar, abortar, terminar. | Puerto abierto responde SYN-ACK; cerrado, RST. |
| **UDP** | Protocolo sin conexión; no hay saludo. Un puerto cerrado responde ICMP *port unreachable*. | DNS (53), SNMP (161). |
| **Sonda (probe)** | Paquete que Nmap envía para provocar una respuesta. | |

### 1.3 Nmap y escaneo

| Término | Definición | Ejemplo / nota |
|---|---|---|
| **Nmap (Network Mapper)** | Herramienta libre de descubrimiento de redes y auditoría de seguridad, creada por Gordon Lyon («Fyodor») en 1997. | |
| **Reconocimiento (reconnaissance)** | Primera fase de una auditoría o ataque: reunir información del objetivo. | MITRE ATT&CK T1595 (*Active Scanning*). |
| **Superficie de ataque** | Conjunto de puntos de una organización accesibles a un atacante. | Puerto abierto = superficie; **no** es una vulnerabilidad. |
| **Vulnerabilidad** | Debilidad concreta que puede ser explotada. | CVE-2021-41773 |
| **CVE** | Identificador público de una vulnerabilidad conocida. | |
| **Descubrimiento de hosts (host discovery)** | Fase que determina qué equipos están activos. | `-sn` |
| **Ping scan** | Descubrimiento sin escaneo de puertos. | `nmap -sn 10.20.0.0/24` |
| **List scan** | Solo lista y resuelve los nombres de los objetivos, sin enviar sondas a ellos. | `-sL` |
| **Escaneo de puertos** | Determinar el estado de los puertos de un host. | |
| **SYN scan (semiabierto)** | Envía SYN y corta con RST al recibir SYN/ACK; requiere privilegios. | `-sS` |
| **Connect scan** | Completa la conexión con `connect()` del sistema; no requiere privilegios. | `-sT` |
| **UDP scan** | Sondea puertos UDP; es lento y los resultados son frecuentemente `open|filtered`. | `-sU` |
| **Xmas / FIN / Null scan** | Escaneos con banderas anómalas; sirven para estudiar firewalls; ruidosos. | `-sX`, `-sF`, `-sN` |
| **Estado `open`** | Hay una aplicación escuchando. | |
| **Estado `closed`** | El puerto es accesible pero nadie escucha (responde RST). | |
| **Estado `filtered`** | No se puede determinar: un filtro (firewall) descarta las sondas. | |
| **Estado `unfiltered`** | Accesible, pero Nmap no sabe si está abierto o cerrado. | `-sA` |
| **Estado `open|filtered`** | Nmap no puede distinguir entre abierto y filtrado. | UDP, `-sX` |
| **Estado `closed|filtered`** | Nmap no puede distinguir entre cerrado y filtrado. | Escaneo *idle* |
| **Detección de servicios / versiones** | Nmap conversa con el puerto y compara la respuesta con su base de firmas. | `-sV` |
| **Detección de S.O.** | Estimación por huella de la pila TCP/IP (necesita un puerto abierto y uno cerrado). | `-O` |
| **Huella (fingerprint)** | Conjunto de rasgos de respuesta que identifican un servicio o un S.O. | |
| **CPE** | Identificador estandarizado de productos. | `cpe:/a:apache:http_server:2.4.49` |
| **NSE (Nmap Scripting Engine)** | Motor de scripts en Lua para automatizar tareas. | `-sC`, `--script` |
| **Categorías NSE** | `auth`, `broadcast`, `brute`, `default`, `discovery`, `dos`, `exploit`, `external`, `fuzzer`, `intrusive`, `malware`, `safe`, `version`, `vuln`. | Usar `safe`/`default` primero. |
| **Modo agresivo** | `-A` = `-sV` + `-O` + `-sC` + `--traceroute`; es muy informativo y ruidoso. | |
| **Plantilla de tiempos** | `-T0` a `-T5`: de paranoico a insano. | `-T4` es habitual en LAN. |
| **Salida normal / XML / grepable** | `-oN`, `-oX`, `-oG` (y `-oA` los genera todos). | El XML es el formato para procesar con scripts. |

### 1.4 Auditoría, ética y defensa

| Término | Definición | Ejemplo / nota |
|---|---|---|
| **Alcance (scope)** | Lista acordada de sistemas y técnicas que se pueden evaluar. | |
| **Autorización escrita** | Documento del titular que permite la auditoría. | Sin ella, no se escanea. |
| **Reglas de compromiso (rules of engagement)** | Condiciones de la auditoría: horarios, técnicas, contacto de emergencia. | |
| **Hallazgo** | Observación documentada: qué es, por qué importa y qué hacer. | |
| **Mínimo servicio necesario** | Política: solo debe estar activo lo que la función del equipo requiere. | |
| **Inventario de activos** | Lista de todos los dispositivos y software de la organización. | CIS Controls v8, controles 1 y 2. |
| **IDS / IPS** | Sistemas que detectan (o bloquean) tráfico sospechoso. | Suricata, Snort, Zeek. |
| **Falso positivo / falso negativo** | Alerta sin ataque real / ataque real sin alerta. | |
| **Remediación y re-escaneo** | Corregir un hallazgo y volver a escanear para verificar. | |
| **Data dump** | Pegar la salida de una herramienta sin interpretarla: error de reporte. | |

---

## 2. Fórmulas y cálculos

| Cálculo | Fórmula | Ejemplo |
|---|---|---|
| **Direcciones de un bloque CIDR** | 2^(32 − prefijo) | /24 → 2⁸ = 256; /27 → 32; /22 → 1.024 |
| **Equipos utilizables** | direcciones − 2 (red y difusión) | /24 → 254; /30 → 2 |
| **Puertos totales (1–65535)** | 2¹⁶ − 1 | 65.535 |
| **Sondas de un escaneo** | equipos × puertos | 254 × 1.000 = 254.000 |
| **Tiempo estimado** | sondas ÷ tasa (sondas/s) | 254.000 ÷ 1.000 = 254 s |
| **Todos los puertos de un /24** | 254 × 65.535 | 16.645.890 sondas ≈ 4 h 37 min a 1.000/s |
| **TTL de origen estimado** | 64, 128 o 255 → saltos = TTL inicial − TTL recibido | 64 − 63 = 1 salto |
| **Duración de un certificado** | notAfter − notBefore | 2026-11-02 → 2027-11-02 = 365 días |

> La tasa de sondas real depende de la red, de los firewalls y de la plantilla de tiempos (`-T`). El cálculo es una **estimación de orden de magnitud**.

---

## 3. Comandos esenciales

> En el laboratorio se ejecutan con `sudo ip netns exec auditor ...`. En una red real se escribe solo `nmap ...` (con `sudo` para escaneos que requieren privilegios).

### 3.1 Descubrimiento

```bash
nmap -sn 10.20.0.0/24              # ¿quién está vivo? (ARP en la LAN)
nmap -sn -n 10.20.0.0/24           # igual, sin resolver nombres (más rápido)
nmap -sL 10.20.0.0/29              # listar nombres sin enviar sondas a los equipos
nmap -Pn 10.30.0.20                # omitir descubrimiento: asumir que el equipo está activo
nmap -sn -PS8443 10.30.0.20        # descubrimiento con SYN a un puerto concreto
nmap 10.20.0.1-50                  # rango de equipos
nmap 10.20.0.0/24 --exclude 10.20.0.10
```

### 3.2 Puertos

```bash
nmap 10.20.0.20                    # 1.000 puertos TCP más comunes
nmap -F 10.20.0.20                 # modo rápido (100 puertos)
nmap -p 22,80,443 10.20.0.20       # puertos concretos
nmap -p- 10.20.0.20                # los 65.535 puertos
nmap --top-ports 20 10.20.0.20
nmap -sS 10.20.0.20                # SYN (semiabierto, root)
nmap -sT 10.20.0.20                # connect (sin privilegios)
nmap -sU -p 53,161 10.20.0.1       # UDP
nmap --reason 10.20.0.20           # por qué Nmap decidió cada estado
nmap --open 10.20.0.20             # mostrar solo los abiertos
```

### 3.3 Servicios, sistema operativo y scripts

```bash
nmap -sV 10.20.0.20                # versión de servicios
nmap -sV --version-intensity 9 ...  # más sondas (0–9)
nmap -O --osscan-guess 10.20.0.20  # sistema operativo (con conjeturas)
nmap -sC 10.20.0.20                # scripts por defecto
nmap --script http-headers -p 80 10.20.0.20
nmap --script-help ssl-cert
nmap -A 10.20.0.20                 # -sV -O -sC --traceroute
```

### 3.4 Resultados y comparación

```bash
nmap -sV -oA servidor_web 10.20.0.20       # genera .nmap, .xml y .gnmap
python3 reporte/nmap_a_markdown.py servidor_web.xml --autor "Tu nombre" > reporte.md
python3 reporte/comparar_escaneos.py antes.xml despues.xml
```

### 3.5 Captura y defensa

```bash
sudo ip netns exec auditor tcpdump -i eth0 -nn -w escaneo.pcap "host 10.20.0.20 and tcp"
tcpdump -nn -r escaneo.pcap | head
sudo nft list ruleset
```

---

## 4. Opciones que se confunden

| Opción | Qué hace | Error frecuente |
|---|---|---|
| `-O` | Detecta el **S**istema **O**perativo | Confundir con `-o` |
| `-o` (`-oN/-oX/-oG/-oA`) | Guarda la salida en archivos | |
| `-sn` | Descubre equipos **sin** escanear puertos | Creer que «no ve el equipo» = apagado |
| `-Pn` | No hace descubrimiento; escanea puertos igual | Usarlo siempre: lentísimo y ruidoso |
| `-sV` | Versión del servicio | Solo actúa en puertos abiertos |
| `-sC` | Scripts `default` | No es «seguro en todo contexto» |
| `-A` | Todo junto | Es ruidoso: mejor en laboratorio o con permiso |
| `-p-` | Todos los puertos | Puede tardar horas en una red real |
| `-sX` | Escaneo con banderas anómalas | No es un escaneo de inventario |

---

## 5. Ejemplos actuales (2025–2026)

- **Nmap sigue activo:** la versión 7.993 se publicó el 23/10/2026 (la 7.992, el 15/10/2026). *(nmap.org/changelog)* Debian 13 trae su propia versión empaquetada, que alcanza para este curso.
- **El escaneo precede a las vulnerabilidades:** un informe de GreyNoise (20/4/2026) encontró que más de la mitad de los picos de actividad de escaneo sobre un producto fueron seguidos, en un plazo de hasta tres semanas (mediana de 11 días), por la divulgación de una vulnerabilidad de ese fabricante. *(GreyNoise; según la nota de prensa)*
- **RDP y VNC expuestos:** Forescout Vedere Labs encontró (con Shodan) unos 1,8 millones de servidores RDP y 1,6 millones de VNC visibles en internet; tras descartar *honeypots*, identificó 91.000 RDP y 29.000 VNC clasificables por industria. *(ITPro, 1/5/2026)*
- **Dispositivos de borde:** el DBIR 2025 de Verizon indica que los dispositivos de borde y VPN pasaron del 3 % al 22 % de los objetivos de explotación; solo el 54 % se corrigió por completo (mediana: 32 días). *(Tenable, resumen)* Se conecta con la Semana 6: lo que se expone es lo que se escanea.
- **regreSSHion (CVE-2024-6387):** afecta a OpenSSH desde 8.5p1 hasta antes de 9.8p1. Un escaneo `-sV` permite ubicar versiones en ese rango, pero el parche de la distribución puede no cambiar el número. *(Qualys)*
- **Marco legal:** Argentina aprobó el Convenio de Budapest sobre ciberdelito con la Ley 27.411 (B. O. 15/12/2017); el acceso ilegítimo a sistemas informáticos está previsto en el art. 153 bis del Código Penal (Ley 26.388).

---

## 6. Errores frecuentes

1. **«Si Nmap no ve el equipo, está apagado.»** Puede descartar el ping y los sondeos por defecto: probar `-Pn` o `-PS<puerto>`.
2. **«Puerto abierto = vulnerabilidad.»** Es superficie de ataque; la vulnerabilidad es la debilidad del servicio que escucha.
3. **«El banner es la verdad.»** Es texto configurable; las distribuciones aplican parches sin cambiar la versión.
4. **«Nmap acierta siempre el S.O.»** Es una estimación; con firewalls o kernels nuevos puede ser «no concluyente».
5. **«El `-sS` es invisible.»** Es *semiabierto*, pero firewalls e IDS lo detectan.
6. **Reporte «data dump».** Pegar capturas sin interpretar: el valor está en el análisis.
7. **Escanear sin autorización.** Siempre alcance y permiso por escrito.
8. **Confundir `-o` con `-O`.**

---

## 7. Síntesis

| Pregunta | Herramienta | Resultado |
|---|---|---|
| ¿Quién está ahí? | `-sn` | Lista de equipos activos |
| ¿Qué puertas están abiertas? | `nmap <ip>` | open / closed / filtered |
| ¿Quién vive detrás de cada puerta? | `-sV`, `-sC` | Servicios, versiones, evidencia |
| ¿Qué sistema operativo es? | `-O` | Estimación con porcentaje |
| ¿Qué significa para la organización? | Reporte | Hallazgo + criterio + recomendación |

**Puente a la próxima semana:** con el mapa de la red y de sus servicios, el paso siguiente es analizar esas debilidades con más profundidad. *(El tema exacto de la Semana 8 no estaba en el material; ajustalo si hace falta.)*
