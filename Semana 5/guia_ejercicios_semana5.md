# Guía de ejercicios — Semana 5

## Diplomatura en Ciberseguridad — Criptografía práctica y gestión de identidad

Esta guía tiene 14 ejercicios: los primeros 4 trabajan contraseñas, ataques y entropía; los siguientes 3 trabajan gestores de contraseñas; los siguientes 3 trabajan MFA y TOTP; los siguientes 2 trabajan passkeys; y los últimos 2 trabajan VeraCrypt, integración y programación en Python. Cada ejercicio incluye su resolución justificada.

**Convenciones:** los tiempos de ataque se calculan con la **mitad del espacio de búsqueda** (en promedio el atacante encuentra la clave a mitad de camino) y con una velocidad de **10¹⁰ intentos/s** (10 mil millones por segundo, un atacante con varias GPU contra un hash rápido). 1 año ≈ 3,15 × 10⁷ s.

---

### Ejercicio 1 — Fuerza bruta vs. relleno de credenciales

**Enunciado:** Para cada situación indicá si es **fuerza bruta**, **relleno de credenciales** (credential stuffing) u **otra cosa**, y qué defensa es la más efectiva.

a) Un programa prueba `Boca2024`, `Boca2025`, `River2024`… contra el login de una tienda.
b) Se filtra la base de un foro de videojuegos; horas después hay miles de intentos de login en un banco con esos mismos correos y claves.
c) Un empleado recibe un mail que lo lleva a una página idéntica a su portal de correo y escribe su clave.
d) Un atacante obtiene el archivo de hashes de un sitio y los prueba offline con un diccionario.

**Resolución:**

| Ítem | Ataque | Defensa más efectiva |
|---|---|---|
| a | Fuerza bruta (con patrones, tipo diccionario con reglas) | Contraseña larga y aleatoria; bloqueo/limitación de intentos |
| b | Relleno de credenciales | **Contraseña única por sitio** (gestor) + MFA |
| c | Phishing (no es ni una ni otra) | Passkeys/FIDO2 (atadas al dominio) y gestor que no autocompleta en dominios falsos |
| d | Fuerza bruta **offline** contra hashes | Del lado del sitio: sal + función lenta (Argon2, scrypt, PBKDF2); del lado del usuario: clave larga y aleatoria |

**Idea clave:** el relleno de credenciales no "adivina" nada: aprovecha que **reutilizaste**. Por eso la regla número uno es una clave distinta en cada cuenta.

---

### Ejercicio 2 — Calculá la entropía

**Enunciado:** Usá **E = L × log₂(N)** para calcular la entropía de:

a) Una contraseña de 8 letras minúsculas.
b) Una contraseña de 8 caracteres elegidos al azar entre los 94 imprimibles.
c) Una contraseña de 16 caracteres al azar entre 94.
d) Una frase de 6 palabras elegidas al azar de una lista de 7.776 palabras (diceware).

Datos: log₂(26) ≈ 4,70 · log₂(94) ≈ 6,55 · log₂(7776) ≈ 12,92.

**Resolución:**

| Ítem | Cálculo | Entropía |
|---|---|---|
| a | 8 × 4,70 | **≈ 37,6 bits** |
| b | 8 × 6,55 | **≈ 52,4 bits** |
| c | 16 × 6,55 | **≈ 104,9 bits** |
| d | 6 × 12,92 | **≈ 77,5 bits** |

**Verificación con el kit:** `python3 entropia.py "abcdefgh"` y `python3 entropia.py --palabras 6`.

**Observación:** la frase de 6 palabras (77 bits) supera ampliamente a una clave aleatoria de 8 caracteres "con símbolos" (52 bits) y es mucho más fácil de recordar. **Cada carácter o palabra extra suma bits; más símbolos distintos suman poco.**

---

### Ejercicio 3 — Tiempo de ataque

**Enunciado:** Con un atacante de 10¹⁰ intentos/s, estimá el tiempo **promedio** para romper cada contraseña del ejercicio 2. Fórmula: **t = 2^E / 2 / velocidad**.

**Resolución:**

| Ítem | Entropía | Tiempo promedio |
|---|---|---|
| a | 37,6 bits | ≈ **10 segundos** |
| b | 52,4 bits | ≈ 3,0 × 10⁵ s ≈ **3,5 días** |
| c | 104,9 bits | ≈ 1,9 × 10²¹ s ≈ **6 × 10¹³ años** |
| d | 77,5 bits | ≈ **350.000 años** |

**Cuenta paso a paso (ítem d):** 2^77,5 ≈ 2,0 × 10²³ → dividido 2 = 1,0 × 10²³ → dividido 10¹⁰ = 1,0 × 10¹³ s → ÷ 3,15 × 10⁷ ≈ 3,5 × 10⁵ años.

**Idea clave:** pasar de 8 a 16 caracteres no "duplica" la seguridad: la **eleva al cuadrado**. Cada bit extra duplica el trabajo del atacante.

---

### Ejercicio 4 — La trampa de la fórmula

**Enunciado:** `P4ssw0rd!` tiene 9 caracteres de un conjunto de 94. Según la fórmula tiene ≈ 59 bits. ¿Por qué en la práctica se rompe en segundos? ¿Y por qué tampoco sirve como contraseña maestra la frase de ejemplo del material ("ElefanteAzulBailaBajoLaLluvia2024!")?

**Resolución:**
- La fórmula supone que **cada carácter se elige al azar e independientemente**. `P4ssw0rd!` es una palabra común ("password") con sustituciones previsibles (a→4, o→0) y un signo al final. Los diccionarios de los atacantes incluyen **reglas** que aplican justamente esas mutaciones: el espacio real de búsqueda es minúsculo.
- La frase de ejemplo parece fuerte (≈ 190 bits "por caracteres"), pero **ya está publicada** en un apunte: cualquier clave que haya aparecido en un documento, un libro o un sitio entra en los diccionarios. Además está compuesta por palabras elegidas por un humano, no por azar.
- La entropía **mide el proceso de elección**, no el aspecto de la clave. Una frase vale lo que valen sus palabras **al azar**: usá dados o un generador (diceware), nunca una frase propia o famosa.

---

### Ejercicio 5 — ¿Qué gestor elegir?

**Enunciado:** Recomendá un gestor (Bitwarden o KeePassXC) para cada perfil y justificá:

a) Una familia con 5 celulares y 2 computadoras que quiere compartir la clave del Wi-Fi y las suscripciones.
b) Un periodista que trabaja con fuentes sensibles y no quiere depender de ningún servidor externo.
c) Una pyme de 12 personas.

**Resolución:**

| Perfil | Recomendación | Justificación |
|---|---|---|
| a | **Bitwarden** (plan familiar) | Sincronización automática entre dispositivos y compartir elementos de forma sencilla; cifrado de extremo a extremo |
| b | **KeePassXC** | Archivo `.kdbx` local; sin servidor que pueda ser brechado; el costo es resolver vos la sincronización y los respaldos |
| c | **Bitwarden** (plan empresarial) o similar | Administración centralizada, altas y bajas, colecciones compartidas, auditoría |

**Idea clave:** no hay "el mejor": hay **comodidad y sincronización** (nube con E2EE) contra **control y cero dependencia** (local). Y en ambos, la seguridad real depende de la contraseña maestra y de los respaldos.

---

### Ejercicio 6 — Diseñá una contraseña maestra

**Enunciado:** (1) Explicá por qué una frase aleatoria de 6 palabras es mejor que `M1Cl@v3Segura!2026`. (2) Describí cómo la generarías sin usar tu cabeza. (3) ¿Qué harías para no olvidarla?

**Resolución:**
1. `M1Cl@v3Segura!2026` es un patrón humano (palabras + leet + año), vulnerable a diccionarios con reglas; las 6 palabras al azar dan ≈ 77 bits **reales** y son más fáciles de recordar.
2. Con **dados** y una lista diceware (5 tiradas por palabra), o con el generador de frases del gestor. Lo importante es que **el azar lo ponga un mecanismo, no vos**.
3. Repetirla al escribirla las primeras semanas; guardar **una copia en papel** en un lugar físico seguro (caja fuerte, sobre cerrado) y un **plan de recuperación** (código de recuperación del gestor guardado fuera de línea).

---

### Ejercicio 7 — El caso LastPass: ¿qué falló?

**Enunciado:** En 2022 se robaron bóvedas **cifradas** de LastPass. Años después, atacantes vaciaron carteras de criptomonedas (más de USD 35 millones rastreados por TRM Labs según su informe de diciembre de 2025). Si estaban cifradas, ¿cómo fue posible? ¿Qué debería haber hecho cada usuario?

**Resolución:**
- Con la bóveda **robada**, el atacante puede probar contraseñas maestras **offline**, sin límite de intentos, durante años. La protección depende de **(1)** la fortaleza de la maestra y **(2)** la lentitud de la función de derivación (KDF).
- Las bóvedas protegidas por maestras **cortas o previsibles** (y, en cuentas antiguas, con pocas iteraciones) se descifraron. El cifrado no falló: **la clave del usuario no alcanzó**.
- Usuario: maestra **larga y aleatoria**, KDF fuerte (Argon2/PBKDF2 con muchas iteraciones), MFA, y **rotar** las claves y semillas guardadas cuando el proveedor informa una brecha. Las frases semilla de criptomonedas no deberían vivir solo en una bóveda en línea.

---

### Ejercicio 8 — Los tres factores y MFA

**Enunciado:** Clasificá cada elemento en **sabés / tenés / sos** y decidí si el par indicado es MFA:

a) Contraseña + PIN.
b) Contraseña + código SMS.
c) Contraseña + llave USB FIDO2.
d) Huella + reconocimiento facial.
e) PIN del teléfono + huella.

**Resolución:**

| Ítem | Factores | ¿MFA? |
|---|---|---|
| a | sabés + sabés | **No**: mismo factor |
| b | sabés + tenés | **Sí** (aunque el SMS es el método más débil) |
| c | sabés + tenés | **Sí** (y muy robusto) |
| d | sos + sos | **No**: ambos son biométricos |
| e | sabés + sos | **Sí** |

**Idea clave:** MFA exige **categorías distintas**, no "más pasos".

---

### Ejercicio 9 — SIM swapping y ordenar métodos

**Enunciado:** (1) Explicá cómo un SIM swap permite entrar a una cuenta protegida con SMS. (2) Ordená de **menos a más seguro**: SMS, llave FIDO2, TOTP. (3) Relacioná con el caso de la cuenta de X de la SEC.

**Resolución:**
1. El atacante engaña a la operadora para que transfiera tu número a una SIM suya; desde ese momento recibe tus SMS, incluidos los códigos de verificación y los de "recuperar contraseña".
2. **SMS < TOTP < FIDO2**: el SMS viaja por la red celular y depende de la operadora; el TOTP se calcula en tu dispositivo; FIDO2 está atada criptográficamente al dominio legítimo.
3. En el caso de la SEC, la cuenta fue tomada y se anunció falsamente la aprobación de los ETF de bitcoin (el precio subió más de USD 1.000 y luego cayó más de USD 2.000). Uno de los participantes (quien ejecutó el SIM swap) se declaró culpable en febrero de 2025 y fue condenado en mayo de 2025 a 14 meses de prisión. Un SMS demuestra que controlás un **número**, no que seas **vos**.

---

### Ejercicio 10 — Calculá un TOTP

**Enunciado:** TOTP usa pasos de 30 segundos: **T = ⌊tiempo_unix / 30⌋**, y el código es HMAC-SHA1(secreto, T) truncado a 6 dígitos. Con el secreto base32 `JBSWY3DPEHPK3PXP`:

a) ¿Cuál es el contador T para el instante Unix 1700000000?
b) ¿Cuánto falta para que cambie el código en ese instante?
c) ¿Qué código se obtiene en ese instante y 29 segundos después?
d) ¿Por qué un servidor suele aceptar también el código del paso anterior y del siguiente?

**Resolución:**
a) 1700000000 ÷ 30 = 56.666.666,67 → **T = 56.666.666**.
b) 1700000000 mod 30 = 20 → transcurrieron 20 s del paso; faltan **10 s**.
c) En 1700000000: **324550**. En 1700000029 (ya en el paso siguiente): **367665**.
d) Los relojes del servidor y del teléfono pueden diferir unos segundos; aceptar una **ventana de ±1 paso** tolera esa deriva y el tiempo que tarda el usuario en escribir el código.

**Verificación:**
```bash
oathtool --totp -b JBSWY3DPEHPK3PXP -N "2023-11-14 22:13:20 UTC"
python3 totp.py JBSWY3DPEHPK3PXP --en 1700000000
```
Ambos deben dar **324550**.

---

### Ejercicio 11 — Límites de MFA

**Enunciado:** Dos ataques que superan SMS y TOTP: **AiTM** y **fatiga de MFA**. Describí cada uno y qué método los frena.

**Resolución:**
- **AiTM (adversario en el medio):** un proxy muestra la página real y captura contraseña y código en tiempo real, y reenvía todo al sitio verdadero; también puede robar la cookie de sesión. Frenado por **FIDO2/passkeys**, porque la firma incluye el dominio y el proxy tiene otro.
- **Fatiga de MFA:** el atacante, con la clave robada, dispara decenas de pedidos de aprobación hasta que la víctima acepta por cansancio (caso Uber 2022). Mitigación: **number matching** (ingresar un número que se ve en la pantalla de login) y métodos resistentes al phishing.

---

### Ejercicio 12 — Passkeys: el flujo y por qué resisten el phishing

**Enunciado:** (1) Ordená los pasos de un login con passkey: *el sitio verifica con la llave pública · el sitio envía un desafío · el dispositivo firma con la llave privada · desbloqueás con huella o PIN*. (2) ¿Qué guarda el servidor? (3) Si el atacante te manda a `tiendanova-login.test`, ¿qué ocurre?

**Resolución:**
1. **Desafío → desbloqueo → firma → verificación.**
2. Solo la **llave pública** (y un identificador de credencial). No hay secreto compartido que robar.
3. La passkey está asociada al dominio `tiendanova.test`. El **navegador** informa el dominio real al autenticador: no hay credencial para `tiendanova-login.test` y la firma no sirve para otro origen. **El engaño no funciona** porque no depende de que vos lo detectes.

**Laboratorio:** `passkey_sim.py` reproduce estos casos con ECDSA P-256 real.

---

### Ejercicio 13 — VeraCrypt: contenedor, header y flujo

**Enunciado:** (1) Un contenedor de 500 MB con 20 MB de datos, ¿cuánto pesa? (2) ¿Qué es el header y qué pasa si se daña? (3) Ordená: *desmontar · montar · trabajar · elegir contenedor*. (4) ¿Qué pasa si se pierde la clave?

**Resolución:**
1. **500 MB**: el tamaño es fijo (no revela cuánto hay adentro).
2. Son los primeros bytes: contienen las claves que permiten descifrar. Si se daña, **no se puede abrir** ni con la clave correcta. Por eso se hace **backup del header** fuera del equipo.
3. **Elegir contenedor → montar → trabajar → desmontar.**
4. No hay recuperación: los datos se pierden. Guardar la clave en el gestor (con su propio respaldo).

**Extra:** un contenedor cifrado se ve como ruido: `python3 entropia_archivo.py contenedor.hc` da ≈ 8,0 bits/byte; un texto común ronda 4,5.

---

### Ejercicio 14 — Python: automatizar VeraCrypt y plan de recuperación

**Enunciado:** (1) Completá `mount_volume` y `unmount_volume`. (2) El material usa `--drive` y `--dismount`, pero la consola de VeraCrypt en Linux usa otra sintaxis: investigala. (3) Escribí un plan de recuperación para la bóveda de TiendaNova.

**Resolución:**

(1) y (2) La sintaxis real en Debian es:

```python
import subprocess

def comando_montar(ruta, punto, clave):
    return [
        "veracrypt", "--text", "--mount", ruta, punto,
        f"--password={clave}", "--pim=0", "--keyfiles=",
        "--protect-hidden=no", "--non-interactive",
    ]

def comando_desmontar(punto):
    return ["veracrypt", "--text", "--unmount", punto]

def mount_volume(ruta, punto, clave):
    r = subprocess.run(comando_montar(ruta, punto, clave),
                       capture_output=True, text=True)
    return r.returncode == 0

def unmount_volume(punto):
    r = subprocess.run(comando_desmontar(punto),
                       capture_output=True, text=True)
    return r.returncode == 0
```

Notas: en Windows la unidad se identifica con una letra (`/l X`, `/d X`), en Linux con un **punto de montaje**. `--dismount` está en desuso en favor de `--unmount`. Pasar la clave en `--password=` la deja visible en la lista de procesos: en producción usá `--stdin` o ingresala por consola.

(3) Plan de recuperación (ejemplo):

| Qué | Dónde | Frecuencia |
|---|---|---|
| Contraseña maestra | Memoria + copia en papel en caja fuerte | Una vez; revisar al año |
| Código de recuperación del gestor | Fuera de línea (papel/USB cifrado) | Al crear la cuenta |
| Backup de la bóveda (`.kdbx` o exportación cifrada) | 2 soportes distintos, 1 fuera del sitio (regla 3-2-1) | Semanal |
| Backup del header de VeraCrypt | USB separado del contenedor | Al crear y tras cambiar la clave |
| Clave del contenedor | Dentro del gestor | Siempre |
| Prueba de restauración | Montar el backup en otro equipo | Trimestral |

**Cierre de la guía:** las tres propiedades que protegiste fueron **confidencialidad** (VeraCrypt y bóvedas), **integridad** (hashes, header) y **autenticidad** (MFA y passkeys). Si una capa falla, las otras siguen: eso es defensa en capas.
