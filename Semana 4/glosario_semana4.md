# Glosario de términos y fórmulas — Semana 4

## Diplomatura en Ciberseguridad — Amenazas comunes y phishing

---

## 1. Ingeniería social y phishing

### 🎣 Ingeniería social
> Manipulación psicológica de personas para que entreguen información o realicen acciones que comprometen la seguridad. Ataca a la persona, no al software.

### 🎣 Phishing
> Mensaje fraudulento (generalmente por correo) que simula venir de una entidad confiable para que la víctima entregue datos, haga clic o descargue algo.

| Variante | Canal | Nota |
|---|---|---|
| **Phishing** | Correo electrónico | Masivo y de bajo costo |
| **Smishing** | SMS / mensajería | Llega al celular |
| **Vishing** | Llamada de voz | Presión en tiempo real; posible clonación de voz con IA |
| **Quishing** | Código QR | El enlace no es legible; evade filtros de texto |
| **Spear phishing** | Cualquiera | Dirigido a una persona concreta, con datos reales |
| **Whaling** | Cualquiera | Dirigido a directivos |
| **BEC** (Business Email Compromise) | Correo | Suplantación de un ejecutivo o proveedor para pedir pagos |

### 🔄 Ciclo del phishing
> 1) **Reconocimiento** (recopilar datos de la víctima) → 2) **Pretexto** (historia creíble) → 3) **Entrega** (envío del mensaje) → 4) **Gancho/acción** (la víctima hace clic o responde) → 5) **Robo** (credenciales, dinero o acceso).

### 🚩 Las cinco banderas rojas
> Urgencia · Remitente raro · Enlace sospechoso · Pedido de datos sensibles · Errores o formato extraño.

### 🧠 Gatillos psicológicos
> Urgencia, miedo, autoridad, curiosidad, codicia y confianza. El atacante busca que actúes antes de pensar.

### 🔐 MFA (Autenticación multifactor)
> Pedir dos o más pruebas de identidad (algo que sabés, algo que tenés, algo que sos). Reduce mucho el riesgo, pero no es infalible: ver AiTM.

### 🕸 AiTM (Adversary-in-the-Middle)
> Técnica en la que el atacante pone un sitio intermediario entre la víctima y el servicio real y captura contraseña **y** código MFA (o la cookie de sesión) en tiempo real. Mitigación: llaves de seguridad FIDO2/passkeys.

### 🔑 Gestor de contraseñas
> Aplicación que genera y guarda contraseñas únicas y largas, y solo las autocompleta en el dominio correcto (lo que ayuda a detectar sitios falsos). Ejemplos: Bitwarden, KeePassXC.

---

## 2. Cómo viaja un correo (teoría de redes)

### ✉ SMTP
> Protocolo para **enviar** correo entre servidores (puertos 25, 587, 465).

### 📬 MX (Mail eXchanger)
> Registro DNS que indica qué servidores reciben el correo de un dominio.

### 📖 DNS
> Sistema que traduce nombres de dominio a direcciones IP y publica información adicional (MX, TXT, etc.).

### 📋 Cabeceras del correo

| Campo | Qué es |
|---|---|
| **From** | Remitente visible. Se puede falsificar |
| **Reply-To** | A dónde irá tu respuesta. Si difiere del From, sospechá |
| **Return-Path** | Dirección de rebote (el remitente técnico) |
| **Received** | Una línea por cada servidor por el que pasó. Se lee de **abajo hacia arriba** |
| **Authentication-Results** | Resultado de SPF, DKIM y DMARC según el receptor |

### 🛡 SPF, DKIM, DMARC

| Mecanismo | Pregunta | Dónde se publica |
|---|---|---|
| **SPF** | ¿Este servidor puede enviar por el dominio? | TXT del dominio (`v=spf1 ...`) |
| **DKIM** | ¿Está firmado y no fue alterado? | TXT en `selector._domainkey.dominio` |
| **DMARC** | ¿Qué hacer si fallan y cómo reportar? | TXT en `_dmarc.dominio` |

**Políticas DMARC:** `p=none` (solo monitorear) · `p=quarantine` (a spam) · `p=reject` (rechazar).

### 🔤 Dominios engañosos

| Técnica | Ejemplo |
|---|---|
| **Typosquatting** | `rnercadolibre.com.ar` (rn por m) |
| **Homógrafo** | Carácter Unicode parecido (`í` por `i`) |
| **Subdominio engañoso** | `banco.com.ar.verificar.net` |
| **Palabra gancho** | `banco-seguridad-ar.com` |

**Regla:** el dominio real es lo que está inmediatamente antes de la extensión final, leyendo de derecha a izquierda.

---

## 3. Software malicioso

### 🦠 Malware
> Término general para cualquier software malicioso. **Virus, gusano, troyano, ransomware, spyware y RAT son tipos de malware.** No todo malware es un virus.

| Tipo | Qué hace | Cómo se propaga |
|---|---|---|
| **Virus** | Se replica adjuntándose a archivos | Requiere ejecución humana |
| **Gusano** | Se copia solo por la red | Automática |
| **Troyano** | Parece útil y oculta una función dañina | Engaño |
| **Ransomware** | Cifra archivos y pide rescate | Phishing, vulnerabilidades |
| **Spyware** | Espía y roba datos | Software gratuito, adjuntos |
| **RAT** | Da control remoto al atacante | Troyano, phishing |

### 🔒 Ransomware / doble extorsión
> Cifra los archivos y exige un pago. En la **doble extorsión** además roba los datos y amenaza con publicarlos si no se paga: el backup no resuelve esa parte.

### 🕵 Spyware / keylogger
> Software que recopila información sin consentimiento. El *keylogger* registra las teclas presionadas.

### 🎮 RAT (Remote Access Trojan)
> Troyano que da al atacante control remoto del equipo (archivos, cámara, micrófono, pantalla).

### 💾 Regla de backup 3-2-1
> **3** copias · **2** soportes distintos · **1** copia fuera del sitio y desconectada/inmutable. Probar la restauración.

---

## 4. Malware en la red y herramientas

### 📡 C2 (Command and Control)
> Servidor que el atacante usa para enviar órdenes a los equipos infectados y recibir los datos robados.

### 💓 Beaconing
> Conexión periódica y regular de un equipo infectado hacia su C2 (el "latido"). Detectable por su regularidad temporal.

### 🔍 Indicador de compromiso (IoC)
> Evidencia observable de que hubo intrusión: un hash de archivo malicioso, una IP o dominio de C2, un patrón de tráfico.

### #️⃣ Hash
> Huella digital de un archivo (SHA-256). Si el archivo cambia un solo byte, el hash cambia. Sirve para identificar archivos conocidos y comprobar integridad.

```bash
sha256sum archivo.bin                 # Debian
Get-FileHash archivo.bin -Algorithm SHA256   # Windows PowerShell
```

### 🧪 EICAR
> Cadena de texto inofensiva estandarizada que todos los antivirus detectan como si fuera malware. Sirve para probar antivirus sin riesgo.

### 🧰 Herramientas

| Herramienta | Para qué sirve |
|---|---|
| **VirusTotal** | Analizar archivos/URLs con decenas de motores |
| **urlscan.io** | Ver qué hace una URL sin visitarla (capturas, solicitudes) |
| **MXToolbox** | Consultar MX, SPF, DMARC, listas negras |
| **dig / Resolve-DnsName** | Consultas DNS desde la terminal |
| **whois** | Datos de registro de un dominio |
| **CyberChef** | Decodificar y transformar datos (base64, hex...) |
| **Any.run / Hybrid Analysis** | Sandboxes: ejecutan muestras en un entorno aislado |
| **Wireshark** | Captura y análisis gráfico de paquetes |
| **tshark** | Wireshark en línea de comandos |
| **tcpdump** | Captura de paquetes ligera en terminal |
| **Sysinternals** | Suite para Windows (Process Explorer, Autoruns, TCPView) |
| **Microsoft Defender** | Antimalware integrado en Windows |
| **ClamAV** | Antivirus open source en Linux |

---

## 5. Fórmulas y comandos útiles

### Capturar y analizar tráfico

| Objetivo | Comando |
|---|---|
| Capturar en una interfaz | `sudo tcpdump -i enp0s3 -w captura.pcap` |
| Leer una captura | `tshark -r captura.pcap` |
| Filtrar por IP destino | `tshark -r captura.pcap -Y "ip.dst==10.0.0.5"` |
| Solo SYN iniciales | `-Y "tcp.flags.syn==1 && tcp.flags.ack==0"` |
| Tiempos entre conexiones | `-T fields -e frame.time_relative` |

### Intervalo de beaconing
> **Intervalo = tᵢ₊₁ − tᵢ** (diferencia de tiempo entre conexiones consecutivas). Si los intervalos son casi constantes (baja desviación), es sospechoso. Algunos malware agregan *jitter* (variación aleatoria) para disimular.

### Consultas DNS

| Objetivo | Debian | Windows |
|---|---|---|
| MX | `dig +short MX dominio` | `Resolve-DnsName -Type MX dominio` |
| DMARC | `dig +short TXT _dmarc.dominio` | `Resolve-DnsName -Type TXT _dmarc.dominio` |
| SPF | `dig +short TXT dominio` | `Resolve-DnsName -Type TXT dominio` |

---

## 6. Ejemplos actuales

- **Verizon DBIR 2026:** el elemento humano interviene en ~62 % de las brechas; el ransomware aparece en ~48 % y el engaño por móvil crece.
- **Nevada (2025):** un empleado descargó malware desde un sitio falso; el ataque dejó 28 días de interrupción en más de 60 agencias estatales.
- **Vishing a SSO (2026):** campañas que llaman al empleado para que "valide" su acceso en un portal falso de Microsoft Entra; algunos casos atribuidos a Spectrum/Charter y Abbott aún son denuncias no confirmadas.
- **CERT.ar 2024:** 438 incidentes gestionados, 31 % phishing.
- **Históricos:** Uber 2022 (fatiga de MFA), Twitter 2020 (vishing a empleados), pandemia (+600 % de phishing), fraude del CEO.

---

## 7. Errores frecuentes

| Creencia | Realidad |
|---|---|
| "Tiene candado, es seguro" | HTTPS cifra la conexión, no garantiza honestidad |
| "Tiene el logo, es real" | Cualquiera puede copiar un logo |
| "Tengo antivirus" | El phishing explota decisiones, no solo software |
| "Virus = cualquier malware" | Virus es un tipo; malware es el paraguas |
| "Con MFA estoy a salvo" | AiTM puede robar el código en tiempo real |

---

## 8. Síntesis

1. El phishing explota a las personas: **pausá antes de actuar**.
2. Verificá **dirección y dominio**, no el nombre visible.
3. Las cabeceras y SPF/DKIM/DMARC dan **evidencia técnica**.
4. Malware es el paraguas: **ransomware, spyware y RAT** son los más frecuentes.
5. El beaconing delata al equipo infectado: **observá la red**.
6. Defensa **en capas**: personas, MFA, gestor, parches, backups 3-2-1, monitoreo.

**Puente a la Semana 5:** con las amenazas comunes identificadas, el paso siguiente es construir las defensas técnicas que las contienen.
