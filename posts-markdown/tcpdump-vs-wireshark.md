---
title: "tcpdump vs Wireshark: cuándo uso cada uno"
description: "Por qué sigo usando tcpdump en línea de comandos cuando ya tengo Wireshark instalado, y los filtros de captura que más repito para no tener que abrir la interfaz gráfica."
slug: "tcpdump-vs-wireshark"
category: "Redes"
tags: ["tcpdump", "wireshark", "análisis de tráfico", "redes"]
date: "2026-12-02"
level: "Intermedio"
---

## Por qué no cierro tcpdump y ya está

Ya escribí sobre Wireshark para análisis detallado de capturas. Pero hay situaciones donde ni siquiera abro la interfaz gráfica — sobre todo cuando estoy conectado por SSH a un servidor remoto sin entorno gráfico, o cuando solo necesito confirmar algo rápido sin analizar en profundidad. Ahí tcpdump en la propia terminal es más directo.

## Captura básica

```bash
sudo tcpdump -i eth0
```

Sin filtros, esto es puro ruido en cualquier red con algo de tráfico — lo primero que hago siempre es acotar.

## Filtros que más repito

```bash
# Solo tráfico hacia/desde un host concreto
sudo tcpdump -i eth0 host 192.168.1.10

# Solo un puerto específico
sudo tcpdump -i eth0 port 443

# Combinando host y puerto
sudo tcpdump -i eth0 host 192.168.1.10 and port 22

# Excluir tráfico ruidoso (por ejemplo, tu propia sesión SSH mientras capturas)
sudo tcpdump -i eth0 not port 22
```

## Guardar para analizar después en Wireshark

Este es el flujo que más uso en la práctica: capturar en el servidor remoto con tcpdump (sin interfaz gráfica disponible), y llevarme el archivo a mi máquina para el análisis visual con Wireshark después:

```bash
sudo tcpdump -i eth0 -w captura.pcap host 192.168.1.10
```

```bash
scp usuario@servidor:/ruta/captura.pcap .
```

`.pcap` es el formato nativo que ambas herramientas comparten sin conversión — lo que capturas con tcpdump se abre directamente en Wireshark sin ningún paso intermedio.

## Ver contenido legible sin exportar nada

Para una comprobación rápida sin sacar el archivo de la máquina, `-A` muestra el contenido en ASCII directamente en terminal:

```bash
sudo tcpdump -i eth0 -A port 80
```

Útil para confirmar rápido si hay tráfico HTTP en texto plano con datos legibles, sin necesitar abrir Wireshark para algo tan simple.

## Cuándo Wireshark gana claramente

Cualquier análisis que requiera seguir una conversación completa (Follow TCP/HTTP Stream), estadísticas visuales (Protocol Hierarchy, gráficas de IO), o detectar patrones que no son obvios línea por línea (como el escaneo de puertos o el ARP spoofing que ya until cubrí) — ahí la interfaz gráfica aporta muchísimo más que leer líneas de texto en una terminal. tcpdump es rápido y ligero para captura y filtrado in situ; Wireshark es la herramienta para el análisis real cuando hace falta entender qué está pasando, no solo confirmar que algo pasa.

## La regla práctica

Si tengo entorno gráfico y voy a analizar algo con detalle, Wireshark directamente. Si estoy en una terminal remota, necesito algo rápido, o solo quiero capturar para llevarme el archivo y analizarlo después con calma, tcpdump. No son sustitutos — en la práctica, tcpdump muchas veces es el primer paso y Wireshark el segundo, sobre el mismo archivo `.pcap`.