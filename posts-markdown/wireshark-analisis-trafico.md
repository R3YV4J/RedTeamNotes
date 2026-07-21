---
title: "Wireshark: cómo encuentro un escaneo o un ARP spoof en una captura"
description: "Los filtros que uso de verdad en Wireshark para detectar escaneos de puertos y ARP spoofing, y por qué capturar 'todo' en una red grande es mala idea."
slug: "wireshark-analisis-trafico"
category: "Redes"
tags: ["wireshark", "redes", "análisis de tráfico"]
date: "2026-01-08"
level: "Intermedio"
---

## El error de capturar sin filtro

La primera vez que abrí Wireshark en una red corporativa de prácticas sin
poner ningún filtro de captura, el archivo pesaba varios GB en menos de
diez minutos y mi portátil empezó a sufrir solo para desplazarse por la
lista de paquetes. Desde entonces, antes de darle a "Start capturing" me
pregunto qué estoy buscando exactamente, y pongo un filtro de captura
acorde — no analizo "todo el tráfico" si en realidad solo necesito ver qué
le pasa al puerto 445 de un host concreto.

> Capturar tráfico de redes que no son tuyas, sin autorización, puede ser
> ilegal según dónde estés. Esto es para tu propio laboratorio o con
> permiso explícito.

## Instalación

```bash
sudo apt update && sudo apt install wireshark -y
sudo usermod -aG wireshark $USER
```

Ese segundo comando es el que la gente se salta y luego no entiende por qué
Wireshark le pide permisos de root cada vez que intenta capturar. Tienes que
cerrar sesión y volver a entrar para que el cambio de grupo surta efecto —
si sigues viendo el aviso después de añadirte al grupo, normalmente es eso.

## Filtro de captura vs filtro de visualización

Esto confunde a casi todo el mundo al principio porque la sintaxis se parece
pero no es la misma:

| Tipo | Cuándo se aplica | Ejemplo |
|---|---|---|
| Captura | Antes de capturar, decide qué se guarda | `host 192.168.1.1` |
| Visualización | Después, filtra lo ya capturado | `ip.addr == 192.168.1.1` |

Si pones la sintaxis de visualización en el campo de captura, Wireshark
directamente no te deja empezar — el campo se pone en rojo. Si te pasa eso,
es casi siempre que mezclaste las dos sintaxis.

## Detectar un escaneo de puertos

El patrón es bastante reconocible: muchos SYN sin ACK, hacia distintos
puertos del mismo host, en muy poco tiempo.

```text
Filtro de visualización:
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

Lo que de verdad me ayuda a confirmarlo rápido es ir a
**Statistics → Conversations** y ordenar por número de puertos destino
distintos para la misma IP origen. Si una sola IP está tocando cien puertos
distintos en treinta segundos, no es tráfico normal de aplicación, es un
escaneo.

## Detectar ARP spoofing

Esto es la base de la mayoría de ataques MITM en redes locales, y Wireshark
lo señala solo a veces (lo marca en amarillo si detecta IPs duplicadas), pero
conviene saber buscarlo a mano también:

```text
Filtro:
arp

Qué buscar:
- Varias respuestas "is-at" para la misma IP pero con MAC distinta
- Aparece de forma repetida, no una vez aislada (eso podría ser solo
  un cambio de DHCP/reconexión legítima)
```

La distinción entre "una vez" y "repetido" importa: una sola respuesta ARP
duplicada puede ser ruido de red normal (alguien reconectó un dispositivo).
El patrón de ataque es que se repite de forma constante, normalmente cada
pocos segundos, porque el spoofer necesita mantener el envenenamiento activo.

## Ver credenciales en texto claro (para entender por qué importa HTTPS)

Un ejercicio que hago en cualquier sesión de concienciación:

```text
Filtro: http.request.method == "POST"
Clic derecho sobre el paquete → Follow → HTTP Stream
```

Esto reconstruye la conversación completa. Verlo una vez con tus propios
ojos — usuario y contraseña en texto plano, legibles sin ningún esfuerzo —
convence más que cualquier explicación teórica de por qué HTTP sin TLS es
un problema.

## Estadísticas que reviso primero, antes de filtrar nada

Cuando recibo una captura de otra persona (un cliente, un compañero) y no sé
qué estoy buscando, empiezo siempre por:

- **Protocol Hierarchy** — qué porcentaje es de cada protocolo, te da una
  idea rápida de si hay algo raro (por ejemplo, un volumen de DNS
  desproporcionado puede indicar exfiltración por DNS tunneling)
- **Conversations** — qué hosts hablan más entre sí
- **IO Graph** — si hay un pico de tráfico muy localizado en el tiempo, eso
  es lo primero que voy a investigar

## Exportar para evidencia

```text
File → Export Specified Packets → marca "Displayed" si quieres
exportar solo lo que tienes filtrado, no la captura entera
```

Guarda siempre en `.pcapng`, no en el formato antiguo `.pcap` — mantiene
metadata que el formato viejo descarta y que a veces necesitas después.

## Cómo practico esto sin necesitar una red ajena

Monto dos máquinas virtuales en la misma red interna y provoco yo mismo los
escenarios: un escaneo con Nmap desde una hacia la otra, un ARP spoof con
`bettercap`, una petición HTTP simple a un servidor de pruebas. Verlo
generado por ti mismo en Wireshark, sabiendo exactamente qué provocó cada
paquete, es la forma más rápida de aprender a reconocerlo cuando aparece en
una captura real que no has generado tú.
