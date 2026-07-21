---
title: "SSH tunneling: cómo pivoto cuando el objetivo no tiene salida directa"
description: "Port forwarding local, remoto y dinámico con SSH, y el caso en el que confundí -L con -R y perdí media hora en una máquina de HTB."
slug: "ssh-tunneling-pivoting"
category: "Redes"
tags: ["ssh", "pivoting", "tunneling", "redes"]
date: "2026-05-27"
level: "Intermedio"
---

## El día que confundí -L con -R

Estaba en una máquina con dos interfaces de red — una accesible desde mi
Kali, otra solo visible desde dentro de la propia máquina comprometida — y
necesitaba llegar a un servicio interno que solo escuchaba en esa segunda
red. Monté un túnel con `-L` pensando que bastaría, y durante diez minutos
no entendía por qué no llegaba nada. El problema era conceptual: `-L` expone
algo del lado remoto hacia mi máquina local, pero yo necesitaba lo
contrario en ese punto del pivote. Cambié a `-R` y funcionó al momento.

Desde entonces tengo clarísimo cuál es cuál, porque memorizarlos sin
entender la dirección del flujo es la forma más rápida de perder tiempo
con esto.

> Esto es para máquinas de laboratorio o con autorización. Pivotar a redes
> internas sin permiso es ilegal en la mayoría de jurisdicciones.

## El truco para no confundirlos nunca más

```text
-L (Local):  "quiero ver ALGO REMOTO como si estuviera en mi máquina"
-R (Remote): "quiero que ALGO MÍO sea visible desde la máquina remota"
```

Si lo que necesitas es alcanzar un servicio que está del otro lado, usa
`-L`. Si lo que necesitas es que la máquina remota pueda alcanzar algo tuyo
(por ejemplo, para que ejecute un payload que se conecte de vuelta a ti),
usa `-R`.

## Port forwarding local (-L)

El caso típico: tienes acceso SSH a un host, y ese host puede llegar a un
servicio (por ejemplo, una base de datos en el puerto 3306) que tú no
alcanzas directamente.

```bash
ssh -L 3306:localhost:3306 usuario@host-intermedio

# Ahora, en TU máquina:
mysql -h 127.0.0.1 -P 3306 -u root -p
```

Esto crea un túnel: lo que mandes a `localhost:3306` en tu máquina viaja
por la conexión SSH y sale por el lado del host intermedio hacia
`localhost:3306` *de ese host*. Si el servicio real está en otra IP vista
desde el host intermedio, ajusta el destino:

```bash
ssh -L 3306:192.168.50.10:3306 usuario@host-intermedio
```

## Port forwarding remoto (-R)

El caso inverso: tienes una máquina comprometida que no puede iniciar
conexiones salientes libremente, pero sí tiene una sesión SSH activa hacia
ti (o puedes forzarla). Quieres que algo de tu lado sea accesible desde
ahí.

```bash
ssh -R 8080:localhost:80 usuario@tu-servidor
```

Esto hace que, desde el lado de `tu-servidor`, conectarse a
`localhost:8080` te lleve al puerto 80 de tu máquina local. Lo uso sobre
todo para exponer un listener de Metasploit o un servidor HTTP simple
cuando el pivote es más cómodo en esa dirección.

## Dynamic port forwarding: el SOCKS proxy con -D

Esta es la opción que más utilizo en post-explotación, porque no se limita
a un solo puerto/servicio — crea un proxy SOCKS que puedes apuntar a
cualquier herramienta:

```bash
ssh -D 1080 usuario@host-comprometido
```

Con eso, configurando `proxychains` para usar `socks5 127.0.0.1 1080`,
puedes redirigir prácticamente cualquier herramienta a través del pivote:

```bash
# /etc/proxychains.conf
socks5 127.0.0.1 1080

# Uso
proxychains nmap -sT -p 80,443 192.168.50.0/24
proxychains curl http://192.168.50.10
```

> Nota práctica: con proxychains, el escaneo de Nmap tiene que ser `-sT`
> (TCP connect), no `-sS` (SYN scan) — el SYN scan necesita acceso crudo a
> sockets que proxychains no puede interceptar.

## Encadenar varios saltos

Cuando el pivote tiene más de un salto (máquina A → máquina B → red
objetivo), encadenar túneles SSH puede ponerse confuso rápido. Para dos
saltos, lo más simple suele ser un `ProxyJump`:

```bash
ssh -J usuario@maquinaA usuario@maquinaB
```

Esto te conecta directamente a B usando A como salto intermedio, sin tener
que abrir manualmente una sesión en A primero y otra desde ahí. Si
necesitas además un SOCKS proxy en ese segundo salto:

```bash
ssh -J usuario@maquinaA -D 1080 usuario@maquinaB
```

## Cuándo SSH no es suficiente

Para pivotes más complejos (múltiples redes, necesidad de UDP, o cuando no
tienes una sesión SSH real sino solo una shell), uso `chisel` o `ligolo-ng`
en vez de forzar SSH a hacer algo para lo que no está pensado. SSH
tunneling cubre el 80% de los casos de pivote simple; para el resto, estas
herramientas están diseñadas específicamente para eso y ahorran bastante
fricción.
