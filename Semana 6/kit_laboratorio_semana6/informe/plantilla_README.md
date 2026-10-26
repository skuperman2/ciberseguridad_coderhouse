# Práctica: Wi-Fi segura — Informe de auditoría de red Wi-Fi insegura

> Autor/a: _tu nombre_ · Fecha: _AAAA-MM-DD_ · Entorno: Debian 13 (laboratorio virtual)

## 1. Introducción
_En 3–4 líneas: qué problema estudiás (redes Wi-Fi públicas) y por qué importa._

## 2. Sitio analizado
- URL / host: `http://neverssl.com` (sitio pensado para probar HTTP) y `http://tiendanova.test` (laboratorio)
- Herramientas: `curl -v`, `tcpdump`, `tshark`, `analizar_trafico.py`

## 3. Evidencia observada
Pegá fragmentos **cortos** de la salida (sin datos reales tuyos):

```text
$ curl -v http://neverssl.com
> GET / HTTP/1.1
> Host: neverssl.com
> User-Agent: curl/...
```

| Elemento | Valor observado |
|---|---|
| Protocolo | |
| Método | |
| Host | |
| Headers que envía tu cliente por sí solo | |
| ¿Qué vio el espía en HTTP? | |
| ¿Qué vio el espía en HTTPS? | |
| ¿Qué vio el espía con VPN? | |

## 4. Riesgos encontrados
- _Mínimo 3: qué se puede interceptar en HTTP, evil twin, MITM, DNS, etc._

## 5. Cómo ayuda una VPN
_Cifrado, túnel, qué ve el proveedor/espía, qué NO resuelve (cuenta iniciada, fingerprinting, confianza en el proveedor)._

## 6. Las 3 Reglas de Oro para Wi-Fi públicas
1.
2.
3.

## 7. Límites y honestidad técnica
_Qué no pudiste comprobar y qué supuestos hiciste._
