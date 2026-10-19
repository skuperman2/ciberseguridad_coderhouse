# Glosario de términos y fórmulas — Semana 5

## Diplomatura en Ciberseguridad — Criptografía práctica y gestión de identidad

---

## 1. El problema de las contraseñas

### 🔑 Contraseña / clave
> Secreto que demuestra "algo que sabés". Su seguridad depende de que sea **larga, aleatoria y única** por cuenta.

### ⚙ Fuerza bruta
> Probar combinaciones una tras otra, de forma automática. Con diccionarios y reglas ("password" → `P4ssw0rd!`) es mucho más rápida que probar al azar.

### 📂 Relleno de credenciales (credential stuffing)
> Usar pares usuario-contraseña **filtrados** de un sitio para entrar en otros. No adivina: aprovecha la **reutilización**.

### 🎣 Phishing
> Engaño para que entregues tu clave voluntariamente (Semana 4). Ni la contraseña más larga protege contra esto; sí lo hacen passkeys y FIDO2.

### 🔁 Reutilización de contraseñas
> Usar la misma clave en varios servicios. Convierte la brecha de un sitio débil en la llave de todos los demás ("efecto dominó").

### 🧮 Entropía
> Medida (en **bits**) de cuántas contraseñas posibles había al elegirla. Cada bit extra **duplica** el trabajo del atacante. Solo es válida si la elección fue **aleatoria**.

### 🎲 Diceware
> Método para generar frases con dados: cada palabra se elige al azar de una lista de **7.776 palabras** (6⁵). Cada palabra aporta ≈ **12,92 bits**.

### #️⃣ Hash
> Huella de longitud fija de un dato; no se puede revertir directamente. Los sitios guardan hashes de contraseñas, no las contraseñas.

### 🧂 Sal (salt)
> Valor aleatorio único por usuario que se mezcla con la contraseña antes de aplicar el hash. Evita que dos usuarios con la misma clave tengan el mismo hash y arruina las tablas precalculadas.

### ⏳ KDF (función de derivación de claves)
> Función **deliberadamente lenta y costosa** que transforma una contraseña en una clave o hash: **PBKDF2**, **scrypt**, **Argon2**. Encarece cada intento del atacante.

| Función | Característica |
|---|---|
| **SHA-256 simple** | Muy rápida: mala para guardar contraseñas |
| **PBKDF2** | Repite el cálculo miles de veces (iteraciones); recomendado hoy ≥ 600.000 con SHA-256 |
| **scrypt / Argon2** | Además consumen **memoria**, lo que castiga el hardware especializado (GPU/ASIC) |

### 🕵 Infostealer
> Malware que roba credenciales, cookies de sesión y datos guardados en el navegador. Alimenta el mercado de credenciales filtradas.

---

## 2. Gestores de contraseñas

### 🗄 Gestor de contraseñas
> Aplicación que **genera, guarda cifradas y autocompleta** contraseñas. Vos recordás una sola: la contraseña maestra.

| | Bitwarden | KeePassXC |
|---|---|---|
| Datos | Nube, cifrados de extremo a extremo | Archivo local `.kdbx` |
| Sincronización | Automática | Manual (USB, tu nube, Syncthing) |
| Código | Abierto | Abierto |
| Riesgo principal | Depende de la maestra y del servicio | Perder o no respaldar el archivo |

### 🔐 Contraseña maestra
> La única clave que descifra la bóveda. Debe ser una **frase larga y aleatoria** (5–6 palabras al azar), nunca una frase propia, famosa o copiada de un ejemplo.

### 🔒 Cifrado de extremo a extremo (E2EE) / conocimiento cero
> El proveedor guarda solo datos cifrados; la clave se deriva de tu contraseña maestra **en tu dispositivo** y nunca se envía. Si el proveedor es brechado, el atacante obtiene bloques cifrados.

### 🏛 Bóveda (vault)
> Base de datos cifrada que contiene tus credenciales.

### 🆘 Código de recuperación
> Valor entregado al crear la cuenta que permite recuperar el acceso si perdés la maestra. Se guarda **fuera de línea**.

### 🔍 Auditoría de la bóveda
> Informe de contraseñas débiles, reutilizadas o filtradas (por ejemplo, comparando con la base de Have I Been Pwned). Se revisa **una vez por mes**.

```bash
keepassxc-cli generate -L 20            # genera una contraseña de 20 caracteres
keepassxc-cli analyze -H hibp.txt boveda.kdbx   # busca contraseñas filtradas
```

---

## 3. MFA

### 🔐 MFA (autenticación multifactor)
> Exigir **dos o más factores de categorías distintas**.

| Factor | Ejemplos |
|---|---|
| **Sabés** | Contraseña, PIN |
| **Tenés** | Teléfono, llave de seguridad (YubiKey) |
| **Sos** | Huella, rostro |

> Contraseña + PIN **no** es MFA (mismo factor).

### 📊 Escalera de métodos
> **SMS < TOTP < FIDO2/passkey** (de menos a más seguro).

### 📱 SIM swapping
> Transferir el número de la víctima a una SIM del atacante engañando a la operadora, para recibir sus SMS y códigos.

### 🔢 HOTP / TOTP
> **HOTP** (RFC 4226): código basado en un **contador**. **TOTP** (RFC 6238): el contador es el **tiempo** en pasos de 30 s.

**Fórmula:**
```
T      = ⌊tiempo_unix / 30⌋
HMAC   = HMAC-SHA1(secreto, T)           (T en 8 bytes, big-endian)
offset = últimos 4 bits del HMAC
código = (4 bytes desde offset, sin el bit de signo) mod 10⁶
```

**Ejemplo de verificación:**
```bash
oathtool --totp -b JBSWY3DPEHPK3PXP -N "2023-11-14 22:13:20 UTC"   # 324550
python3 totp.py JBSWY3DPEHPK3PXP --en 1700000000                    # 324550
```

### 🕸 AiTM (adversario en el medio)
> Proxy que se interpone entre la víctima y el servicio real y captura contraseña **y** código (o la cookie de sesión) en tiempo real. TOTP y SMS no lo frenan; FIDO2 sí.

### 📲 Fatiga de MFA
> Enviar muchos pedidos de aprobación hasta que la víctima acepta por cansancio. Mitigación: *number matching*.

### 🔑 FIDO2 / WebAuthn
> Estándar de autenticación con **criptografía de clave pública**. La credencial está ligada al **dominio** (origen) del sitio.

---

## 4. Passkeys

### 🗝 Passkey
> Credencial FIDO2 sincronizable o ligada a un dispositivo: un **par de llaves**. Se desbloquea con huella, rostro o PIN **locales**.

| Llave | Dónde está | Función |
|---|---|---|
| **Pública** | En el servidor | Verificar firmas |
| **Privada** | En tu dispositivo | Firmar desafíos |

### 🎯 Desafío (challenge)
> Número aleatorio de **un solo uso** que envía el servidor. La firma lo incluye, lo que impide **repetir** una respuesta capturada.

### ✍ Firma digital
> Valor calculado con la llave privada que cualquiera puede comprobar con la pública. En passkeys se usa típicamente **ECDSA sobre P-256**.

### 🌐 Resistente al phishing
> El navegador informa el **origen real**; el autenticador no ofrece ni firma la credencial para otro dominio. No depende de que el usuario note el engaño.

### 📈 Datos de adopción (FIDO Passkey Index, octubre 2025)
> 36 % de las cuentas con passkey; 26 % de los inicios de sesión con passkey; éxito 93 % vs 63 %; 8,5 s vs 31,2 s; −81 % de incidentes de mesa de ayuda. Desde mayo de 2025 las cuentas nuevas de Microsoft son "sin contraseña" por defecto.

---

## 5. Cifrado de archivos: VeraCrypt

### 📦 Contenedor
> Archivo (`.hc`/`.tc`) de **tamaño fijo** que se monta como una unidad virtual.

### 🧬 Header (encabezado)
> Primeros bytes del volumen con las claves necesarias para descifrar. **Si se daña, el volumen no se abre** aunque tengas la clave. Se respalda aparte.

### ⚡ Cifrado "al vuelo" (on-the-fly)
> Los datos se descifran en memoria al leerse y se cifran al escribirse. No quedan versiones descifradas en el disco.

### 🔗 Montar / desmontar
> **Montar**: ingresar la clave y exponer el contenido como una unidad (Linux: un punto de montaje). **Desmontar**: borrar la llave de memoria y volver a dejar todo ilegible.

### 🧪 Entropía de Shannon (bytes)
> Medida de aleatoriedad de un archivo: ≈ **4,5 bits/byte** en texto, ≈ **8,0** en datos cifrados.

**Fórmula:** `H = − Σ p(x) · log₂ p(x)` sobre los 256 valores de byte.

### 🧰 Comandos en Debian 13 (consola)
| Objetivo | Comando |
|---|---|
| Crear contenedor | `veracrypt --text --create datos.hc --size=20M --volume-type=normal --encryption=AES --hash=SHA-512 --filesystem=ext4 --pim=0 --keyfiles="" --random-source=/dev/urandom` |
| Montar | `veracrypt --text --mount datos.hc /mnt/boveda` |
| Listar | `veracrypt --text --list` |
| Desmontar | `veracrypt --text --unmount /mnt/boveda` |
| Backup del header | `veracrypt --text --backup-headers datos.hc` |
| Restaurar header | `veracrypt --text --restore-headers datos.hc` |

> **Aviso:** la sintaxis del material (`--drive`, `--dismount LETRA`) es simplificada. En Linux se usa un **punto de montaje**, y `--dismount` está en desuso en favor de `--unmount`.

---

## 6. Fórmulas de la semana

| Concepto | Fórmula | Ejemplo |
|---|---|---|
| Entropía de caracteres | `E = L × log₂(N)` | 16 × log₂(94) ≈ 104,9 bits |
| Entropía diceware | `E = palabras × log₂(7776)` | 6 × 12,92 ≈ 77,5 bits |
| Espacio de búsqueda | `2^E` | 2^77,5 ≈ 2,0 × 10²³ |
| Tiempo promedio de ataque | `t = 2^E / 2 / velocidad` | 77,5 bits a 10¹⁰/s ≈ 350.000 años |
| Contador TOTP | `T = ⌊tiempo / 30⌋` | 1700000000 → 56.666.666 |
| Código TOTP | `HMAC-SHA1(secreto, T)` → truncar → `mod 10⁶` | 324550 |
| Entropía de Shannon | `H = −Σ p·log₂ p` | texto ≈ 4,5 · cifrado ≈ 8,0 |
| Costo de KDF | `iteraciones × costo de una operación` | PBKDF2 600.000 iteraciones |

---

## 7. Ejemplos actuales

- **FIDO Passkey Index (oct. 2025):** passkeys con 93 % de éxito vs 63 % y 8,5 s vs 31,2 s de inicio de sesión; −81 % de incidentes de mesa de ayuda.
- **LastPass:** brecha de 2022; **más de USD 35 millones** en criptomonedas robados que TRM Labs vinculó a bóvedas descifradas (informe de diciembre de 2025); multa de la ICO británica de USD 1,6 millones.
- **Verizon DBIR 2026** (según el resumen de SpyCloud, fuente secundaria): abuso de credenciales en el 39 % de las brechas; explotación de vulnerabilidades 31 % como vía inicial; 73 % de las víctimas de ransomware tenía credenciales o infostealer el año anterior.
- **Microsoft (mayo de 2025):** cuentas nuevas sin contraseña por defecto.
- **Cuenta de X de la SEC:** SIM swap; el ejecutor se declaró culpable en febrero de 2025 y fue condenado a 14 meses en mayo de 2025.
- **VeraCrypt 1.26.29 (9 de junio de 2026):** incluye paquete de consola para Debian 13.
- **Históricos:** Uber 2022 (fatiga de MFA, Semana 4).

---

## 8. Errores frecuentes

| Creencia | Realidad |
|---|---|
| "El gestor del navegador alcanza" | Con acceso a tu perfil suele verse todo; usá un gestor dedicado |
| "Una contraseña con símbolos es fuerte" | Solo si es **aleatoria**; `P4ssw0rd!` es un patrón conocido |
| "El SMS es MFA suficiente" | Sirve contra el relleno, pero se intercepta (SIM swap) |
| "Con MFA estoy a salvo" | AiTM y fatiga de MFA lo evaden; passkeys/FIDO2 no |
| "Cifré el pendrive, listo" | Sin backup del header ni de la clave, un fallo es pérdida total |
| "Dejé el contenedor montado, no pasa nada" | Montado = abierto: desmontá antes de dejar el equipo |
| "Si el proveedor tiene E2EE, la maestra no importa" | Si roban la bóveda, la maestra y la KDF son la única barrera |
| "Una frase mía o famosa es buena maestra" | Debe ser aleatoria; las frases humanas están en los diccionarios |

---

## 9. Síntesis

1. **Una contraseña distinta y aleatoria por cuenta**, guardada en un gestor.
2. **Maestra = frase de 5–6 palabras al azar**, con plan de recuperación.
3. **MFA siempre**; SMS < TOTP < FIDO2; no es infalible.
4. **Passkeys:** par de llaves, atadas al dominio, sin secreto en el servidor.
5. **VeraCrypt:** montar, trabajar, **desmontar**; backup del header.
6. **CIA:** confidencialidad (cifrado), integridad (hashes, firmas), autenticidad (MFA/passkeys).
7. **Capas:** identidad → gestor → datos cifrados → recuperación.

**Puente a la Semana 6:** con la identidad y los datos protegidos, el paso siguiente es extender la protección a los entornos donde esa información circula y se almacena (ajustar según el temario de la Semana 6).
