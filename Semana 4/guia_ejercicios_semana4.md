# Guía de ejercicios — Semana 4

## Diplomatura en Ciberseguridad — Amenazas comunes y phishing

Esta guía tiene 14 ejercicios: los primeros 5 trabajan phishing, banderas rojas y psicología del engaño; los siguientes 4 trabajan cómo viaja un correo (cabeceras, SPF/DKIM/DMARC, dominios parecidos); los siguientes 3 trabajan tipos de malware; y los últimos 2 trabajan malware en la red (beaconing) y programación en Python. Cada ejercicio incluye su resolución justificada.

---

### Ejercicio 1 — ¿Phishing o legítimo?

**Enunciado:** Clasificá cada mensaje como **sospechoso** o **probablemente legítimo** y justificá con al menos una señal:

a) SMS: "Correo Argentino: su paquete no pudo entregarse. Reprograme en https://correoarg-envios.top/r/8821 o será devuelto en 24 h."
b) Mail de tu banco, que no pediste, con el asunto "Verificá tu cuenta ahora o será bloqueada" y un botón "Ingresar".
c) Mail de restablecimiento de contraseña que llega 10 segundos después de que vos pulsaste "Olvidé mi contraseña" en el sitio oficial.
d) Llamada de "soporte de Microsoft" que dice que detectó un virus en tu PC y te pide instalar un programa para ayudarte.

**Resolución:**

| Ítem | Veredicto | Señales |
|---|---|---|
| a | Sospechoso | Dominio ajeno al del correo oficial (`.top`), urgencia (24 h), pide hacer clic desde un SMS |
| b | Sospechoso | Mensaje no solicitado, amenaza de bloqueo (miedo + urgencia), botón en lugar de pedirte entrar por tu cuenta |
| c | Probablemente legítimo | Fue **vos** quien inició la acción y el mensaje llega justo en ese momento. Igual: verificá que el enlace apunte al dominio correcto |
| d | Sospechoso | Microsoft no llama por teléfono por iniciativa propia; pedir instalar software de acceso remoto es la señal clásica de vishing |

---

### Ejercicio 2 — Las cinco banderas rojas

**Enunciado:** Nombrá las cinco banderas rojas de un mensaje de phishing y, para cada una, escribí un ejemplo concreto de frase o detalle que la ilustre.

**Resolución:**

| Bandera | Ejemplo |
|---|---|
| 1. Urgencia | "Tenés 24 horas o se cancelará su cuenta" |
| 2. Remitente raro | `soporte@banco-seguro-ar.com` en lugar del dominio oficial |
| 3. Enlace sospechoso | El texto dice `banco.com.ar` pero al pasar el mouse apunta a otra URL |
| 4. Pedido de datos sensibles | "Responda con su clave y el código que le llegó por SMS" |
| 5. Errores o formato extraño | Saludo genérico ("Estimado cliente"), faltas de ortografía, logo pixelado |

**Nota docente:** en 2026 la bandera 5 es la más débil: los atacantes usan IA para redactar mensajes sin errores. Por eso el peso recae en las otras cuatro, sobre todo urgencia y pedido de datos.

---

### Ejercicio 3 — Nombre vs. dirección

**Enunciado:** Un mail dice venir de "Banco Nación Seguridad". Al mirar el detalle, la dirección real es `alertas@bna-seguridad.help`. ¿Qué es lo que **no** debés mirar y qué es lo que **sí**? ¿Por qué?

**Resolución:**
- **No** confiar en el *nombre visible* ("Banco Nación Seguridad"): lo escribe el atacante libremente, es solo una etiqueta.
- **Sí** mirar la *dirección real* del remitente, y en particular el dominio después de la arroba: `bna-seguridad.help` no es el dominio oficial del banco.
- Lo mismo vale para enlaces: el *texto visible* del enlace puede decir una cosa y el *destino real* (que se ve al pasar el mouse) otra.

---

### Ejercicio 4 — Los gatillos psicológicos

**Enunciado:** Asociá cada mensaje con el gatillo psicológico que explota: **Urgencia, Miedo, Autoridad, Curiosidad, Codicia, Confianza/Reciprocidad.**

a) "Su cuenta será suspendida en 2 horas."
b) "Soy el gerente general, necesito esa transferencia hoy y no se lo cuentes a nadie."
c) "Ganaste un iPhone. Reclamalo ahora."
d) "Mirá esta foto tuya de ayer 😳 [enlace]"
e) Un mail de un "compañero de trabajo" que reenvía un documento con el que venían trabajando juntos.
f) "Detectamos actividad ilegal en su cuenta; será denunciado."

**Resolución:**
a) Urgencia · b) Autoridad (más urgencia y secreto) · c) Codicia · d) Curiosidad · e) Confianza · f) Miedo.

**Idea clave:** un mismo mensaje suele combinar varios gatillos. El objetivo del atacante es que actúes *antes* de pensar.

---

### Ejercicio 5 — Elegir el canal

**Enunciado:** Relacioná cada ataque con su canal y explicá en una línea por qué es especialmente peligroso:

| Término | Canal |
|---|---|
| Phishing | ? |
| Smishing | ? |
| Vishing | ? |
| Quishing | ? |

**Resolución:**

| Término | Canal | Por qué es peligroso |
|---|---|---|
| Phishing | Correo electrónico | Se envía a miles de personas a bajo costo |
| Smishing | SMS / mensajería | El mensaje llega al celular, donde miramos menos los detalles |
| Vishing | Llamada de voz | La voz genera confianza y presión en tiempo real; con IA se puede clonar una voz |
| Quishing | Código QR | El enlace no es legible a simple vista y evita los filtros de correo que analizan texto |

---

### Ejercicio 6 — Leyendo las cabeceras

**Enunciado:** Dado este fragmento de cabeceras de un mail, respondé:

```
From: "Soporte Banco" <soporte@banco-ejemplo.com>
Reply-To: ayuda.cuentas@mailfree-ar.xyz
Return-Path: <bounce@mail-masivo-8812.net>
Authentication-Results: mx.google.com;
    spf=fail smtp.mailfrom=mail-masivo-8812.net;
    dkim=none;
    dmarc=fail header.from=banco-ejemplo.com
```

a) ¿Cuántos dominios distintos aparecen y qué te indica eso?
b) ¿Qué significa cada resultado de autenticación?
c) ¿Cómo lo clasificás y qué hacés?

**Resolución:**
a) Aparecen **tres dominios** (`banco-ejemplo.com`, `mailfree-ar.xyz`, `mail-masivo-8812.net`). Un mail legítimo de un banco no mezcla remitente visible, dirección de respuesta y dirección de rebote de dominios sin relación.
b) `spf=fail`: el servidor que envió no está autorizado a enviar por ese dominio. `dkim=none`: el mensaje no tiene firma digital. `dmarc=fail`: el dominio del From no está alineado con SPF/DKIM, así que no pasa la política del dueño del dominio.
c) **Phishing con suplantación** (spoofing). Acción: no responder (la respuesta iría a `mailfree-ar.xyz`), no hacer clic, reportar a la mesa de seguridad y eliminar.

---

### Ejercicio 7 — SPF, DKIM y DMARC

**Enunciado:** Completá la tabla con la pregunta que responde cada mecanismo y una analogía.

| Mecanismo | Pregunta que responde | Analogía |
|---|---|---|
| SPF | ? | ? |
| DKIM | ? | ? |
| DMARC | ? | ? |

**Resolución:**

| Mecanismo | Pregunta que responde | Analogía |
|---|---|---|
| SPF | ¿Este servidor está autorizado a enviar correo en nombre del dominio? | Lista de choferes habilitados a retirar paquetes |
| DKIM | ¿El mensaje fue firmado por el dominio y llegó sin modificarse? | Sello de lacre que se rompe si alguien abre la carta |
| DMARC | ¿Qué hago si SPF/DKIM fallan y cómo lo informo al dueño? | La instrucción del dueño: "rechazá, mandá a spam o dejá pasar, y avisame" |

**Detalle:** DMARC exige además *alineación*: el dominio autenticado debe coincidir con el dominio del campo From visible.

---

### Ejercicio 8 — Consultando DNS desde la terminal

**Enunciado:** Escribí los comandos (Debian y Windows) para: a) ver el registro DMARC de `google.com`; b) ver los servidores de correo (MX) de `google.com`; c) ver el registro SPF.

**Resolución:**

```bash
# Debian (paquete dnsutils / bind9-dnsutils)
dig +short TXT _dmarc.google.com
dig +short MX google.com
dig +short TXT google.com | grep spf
```

```powershell
# Windows 11 (PowerShell)
Resolve-DnsName -Type TXT _dmarc.google.com
Resolve-DnsName -Type MX google.com
Resolve-DnsName -Type TXT google.com | Where-Object { $_.Strings -match "spf" }
```

El registro DMARC vive en un TXT del subdominio `_dmarc`. El SPF es un TXT del dominio que empieza con `v=spf1`.

---

### Ejercicio 9 — Dominios parecidos

**Enunciado:** Para cada dominio, decidí si es el oficial de `mercadolibre.com.ar` o una imitación, y nombrá la técnica.

a) `mercadolibre.com.ar.verificar-cuenta.net`
b) `mercadolibre.com.ar`
c) `rnercadolibre.com.ar`
d) `mercado-libre-promos.com.ar`
e) `mercadolíbre.com.ar` (con una *í* acentuada)

**Resolución:**

| Ítem | Veredicto | Técnica |
|---|---|---|
| a | Falso | **Subdominio engañoso**: el dominio real es lo que está justo antes del último punto (`verificar-cuenta.net`) |
| b | Oficial | — |
| c | Falso | **Typosquatting**: "rn" imita a "m" |
| d | Falso | Dominio nuevo con guiones y palabras gancho |
| e | Falso | **Ataque homógrafo**: un carácter Unicode parecido al original |

**Regla práctica:** leé el dominio **de derecha a izquierda** hasta el primer punto antes de la extensión.

---

### Ejercicio 10 — Malware: el paraguas

**Enunciado:** ¿Es correcto decir "me infecté con un virus" para cualquier malware? Explicá la diferencia entre *malware* y *virus* y nombrá cuatro tipos más.

**Resolución:**
No. **Malware** es el término general para cualquier software malicioso. **Virus** es un tipo específico: código que se replica adjuntándose a otros archivos y necesita que alguien lo ejecute. Otros tipos: **gusano** (se propaga solo por la red), **troyano** (parece útil pero oculta una función dañina), **ransomware**, **spyware**, **RAT**, **adware**, **botnet/bot**.

---

### Ejercicio 11 — Tres amenazas, tres escenarios

**Enunciado:** Identificá qué tipo de malware describe cada caso:

a) Un empleado abre un archivo y todos los documentos aparecen cifrados con una nota que pide pagar en Bitcoin.
b) Un programa instalado junto a un "crack" registra cada tecla que presiona el usuario y envía las contraseñas a un servidor remoto.
c) Un atacante, desde otro país, mueve el mouse de la víctima, activa la cámara y navega por sus archivos.
d) Además de cifrar los archivos, los criminales los copian y amenazan con publicarlos.

**Resolución:**
a) **Ransomware.** b) **Spyware** (keylogger). c) **RAT** (Remote Access Trojan). d) **Ransomware con doble extorsión**: aunque tengas backup para restaurar, te amenazan con filtrar los datos.

---

### Ejercicio 12 — Cuándo sirve el backup

**Enunciado:** Una empresa sufre ransomware. Tiene un backup en un disco externo que **siempre estaba conectado** al servidor. ¿Qué problema tiene? ¿Qué regla de backup debería seguir?

**Resolución:**
El ransomware suele cifrar también las unidades conectadas, incluyendo ese disco: el backup queda inutilizado. La regla es **3-2-1**: **3** copias de los datos, en **2** tipos de soporte distintos, con **1** copia fuera del sitio y desconectada o inmutable. Además, hay que **probar la restauración** periódicamente. Contra la doble extorsión el backup no alcanza: hace falta también cifrar los datos sensibles y limitar accesos.

---

### Ejercicio 13 — Beaconing: detectar el latido

**Enunciado:** Una captura muestra que una PC interna se conecta a `203.0.113.50:8080` en estos instantes (segundos): 0, 5.0, 10.1, 15.0, 20.0, 25.1, 30.0.

a) ¿Qué patrón ves y qué sugiere?
b) ¿Qué comando de `tshark` usarías para listar las conexiones nuevas con su hora?
c) ¿Qué hacés si ocurre en tu red?

**Resolución:**
a) Conexiones a intervalos casi exactos de 5 s: eso es **beaconing**, el "latido" con el que un equipo infectado consulta a su servidor de **comando y control (C2)**. Una persona navegando no genera ese ritmo regular.
b)
```bash
sudo tshark -r captura.pcap -Y "ip.dst==203.0.113.50 && tcp.flags.syn==1 && tcp.flags.ack==0" -T fields -e frame.time_relative -e ip.src -e tcp.dstport
```
c) Aislar el equipo de la red (sin apagarlo, para conservar evidencia en memoria), avisar al equipo de seguridad, bloquear la IP/dominio en el firewall/DNS, y revisar procesos y persistencia en esa máquina.

---

### Ejercicio 14 — Programación: clasificador de malware

**Enunciado:** Escribí en Python una función `clasificar_malware(descripcion)` que reciba una descripción en texto y devuelva `"ransomware"`, `"spyware"`, `"rat"` o `"desconocido"` según palabras clave:
- ransomware: "cifr", "rescate", "bitcoin"
- spyware: "tecla", "keylogger", "espía"
- rat: "remoto", "control", "cámara"

Probala con tres descripciones.

**Resolución:**

```python
REGLAS = {
    "ransomware": ["cifr", "rescate", "bitcoin"],
    "spyware": ["tecla", "keylogger", "espía", "espia"],
    "rat": ["remoto", "control", "cámara", "camara"],
}

def clasificar_malware(descripcion):
    texto = descripcion.lower()
    for tipo, claves in REGLAS.items():
        if any(clave in texto for clave in claves):
            return tipo
    return "desconocido"

pruebas = [
    "Cifra los archivos y pide un rescate en Bitcoin",
    "Registra cada tecla que presiona el usuario",
    "Permite el control remoto del equipo y activa la cámara",
    "Muestra publicidad en el navegador",
]
for d in pruebas:
    print(f"{clasificar_malware(d):12} <- {d}")
```

**Salida esperada:**
```
ransomware   <- Cifra los archivos y pide un rescate en Bitcoin
spyware      <- Registra cada tecla que presiona el usuario
rat          <- Permite el control remoto del equipo y activa la cámara
desconocido  <- Muestra publicidad en el navegador
```

**Discusión:** el orden del diccionario importa: una descripción que mezcle palabras de dos tipos devuelve el primero que coincide. Es un clasificador muy simple (basado en reglas); los antivirus modernos combinan firmas, heurísticas y análisis de comportamiento.
