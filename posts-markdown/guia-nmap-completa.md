---
title: "Nmap en condiciones: lo que uso de verdad en un pentest"
description: "Los flags de Nmap que realmente uso, en qué orden, y los errores que me han hecho perder tiempo: timeouts, -p- olvidado, falsos negativos por filtrado."
slug: "guia-nmap-completa"
category: "Pentesting"
tags: ["nmap", "pentesting", "escaneo de puertos", "NSE", "kali linux", "recon"]
date: "2026-01-23"
level: "Principiante → Avanzado"
---

## El error que más se repite con Nmap

La primera vez que escaneé algo "en serio" lancé `nmap 192.168.1.1` a secas,
vi tres puertos abiertos, y seguí con la auditoría como si esos tres puertos
fueran todo lo que había. No lo eran. Sin `-p-`, Nmap solo mira los 1000
puertos más comunes. Me faltó un servicio en el puerto 8443 que tenía
exactamente la vulnerabilidad que necesitaba.

Desde entonces tengo un orden fijo para no repetir ese error, y es básicamente
de eso va este artículo: no una lista de todos los flags que existen, sino
los que uso en cada fase y por qué.

## Instalación

En Kali y Parrot ya viene. En Debian/Ubuntu:

```bash
sudo apt update && sudo apt install nmap -y
nmap --version
```

Si vas a compilar desde fuente porque necesitas una versión más reciente que
la del repositorio (pasa más de lo que debería, sobre todo con scripts NSE
nuevos), el proceso estándar de `./configure && make && make install`
funciona, pero asegúrate de tener `libssl-dev` instalado antes o la
detección de servicios SSL falla en silencio.

## Fase 1: descubrir qué hay vivo

Antes de escanear puertos, conviene saber qué responde. En una red `/24`
completa, lanzar `-p-` contra 254 hosts es lento y casi siempre innecesario:

```bash
sudo nmap -sn 192.168.1.0/24
```

Esto es un ping scan, no toca puertos. La salida te da una lista de hosts
vivos sin perder tiempo. El truco: en redes con firewall agresivo, `-sn`
puede dar falsos negativos porque bloquean ICMP. Si sospechas que te falta
algo, repite con `-PS22,80,443` para forzar un SYN a esos puertos como señal
de vida en vez de depender del ping.

## Fase 2: el escaneo que realmente importa

Esto es lo que lanzo casi siempre como primer escaneo serio:

```bash
sudo nmap -sV -sC -p- -T4 -oA full_scan 192.168.1.1
```

Desglosado:

- **`-sV`** detección de versión. Sin esto ves el puerto abierto pero no
  sabes si es Apache 2.4.52 o nginx 1.24 — y la versión es lo que te dice
  si hay un CVE aplicable.
- **`-sC`** scripts por defecto. Bastante ruido a veces, pero detecta cosas
  como vhosts ocultos en HTTP o anon login en FTP sin que tengas que
  pedirlo explícitamente.
- **`-p-`** todos los puertos, no los 1000 de siempre. Esto es lo que me
  faltó la primera vez que escribí arriba.
- **`-T4`** velocidad agresiva. En redes internas está bien; contra
  infraestructura con WAF o rate limiting, bájalo a `-T2` o vas a empezar
  a ver `filtered` en puertos que en realidad están abiertos.
- **`-oA full_scan`** guarda en los tres formatos (`.nmap`, `.xml`, `.gnmap`).
  El XML es el que vas a querer si luego importas esto a otra herramienta.

## La trampa de `open|filtered`

Si ves esto en la salida, no es un puerto a medias — es que Nmap no pudo
determinar el estado con certeza, normalmente porque no llegó respuesta y no
sabe si es porque el puerto está cerrado o porque algo lo está filtrando.
Pasa mucho con UDP:

```bash
sudo nmap -sU --top-ports 100 192.168.1.1
```

UDP es no orientado a conexión, así que Nmap no tiene un ACK que confirmar.
Si necesitas certeza en un puerto UDP específico, mándale un payload que el
servicio espere (por ejemplo, una query DNS al puerto 53) en vez de fiarte
del escaneo genérico.

## Scripts NSE que uso de verdad

De los 600+ scripts que trae Nmap, en el día a día repito un puñado:

```bash
# Vulnerabilidades conocidas, rápido de lanzar contra puertos ya identificados
nmap --script=vuln -p 80,443,445 192.168.1.1

# SMB — esto te dice en diez segundos si hay algo tipo EternalBlue
nmap --script=smb-vuln* -p 445 192.168.1.1

# Enumeración HTTP básica (vhosts, headers, métodos permitidos)
nmap --script=http-title,http-headers,http-methods -p 80,443 192.168.1.1
```

`--script=vuln` es cómodo pero genera falsos positivos con cierta frecuencia
— te marca algo como vulnerable basándose solo en la versión reportada, sin
confirmar el comportamiento real. Tómalo como punto de partida para
investigar, no como confirmación.

## Evasión: cuándo merece la pena y cuándo no

En un pentest con alcance autorizado y sin necesidad de sigilo, evadir nada
es perder tiempo. Pero si el ejercicio incluye evaluar detección (red team
de verdad, no solo "encuentra vulnerabilidades"):

```bash
# Fragmentación de paquetes
sudo nmap -f 192.168.1.1

# Bajar la velocidad para no disparar umbrales de IDS
nmap -T2 192.168.1.1

# Decoys — ojo, esto genera mucho ruido y a veces delata más que ayuda
sudo nmap -D RND:10 192.168.1.1
```

El decoy con `-D` suena bien en teoría pero en redes pequeñas es bastante
obvio: si el rango de IPs decoy no es plausible para esa red, el analista
del otro lado lo detecta de inmediato. Lo uso poco.

## Guardar resultados (y por qué el XML importa)

```bash
nmap -oA resultados 192.168.1.1
```

El `.gnmap` parece útil para grep rápido pero está deprecado en la práctica
— mejor te acostumbras a parsear el XML con `xml.etree` en Python o con
herramientas como `nmap-parse-output` si necesitas automatizar algo.

## Lo que no cambiaría de esta metodología

`-sn` para descubrir, `-sV -sC -p- -T4 -oA` como escaneo base, y scripts NSE
específicos según lo que aparezca. No hay magia adicional — el 90% del valor
de Nmap está en no saltarte el `-p-` y en leer la salida con calma en vez de
lanzar el comando y pasar al siguiente paso sin revisar qué dijo.
