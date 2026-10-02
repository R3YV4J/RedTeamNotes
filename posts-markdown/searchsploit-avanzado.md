---
title: "SearchSploit más allá de la búsqueda básica"
description: "Cómo filtro resultados, actualizo la base de datos local y copio exploits directamente con SearchSploit, en vez de depender de buscar en Exploit-DB desde el navegador."
slug: "searchsploit-avanzado"
category: "Herramientas"
tags: ["searchsploit", "exploit-db", "pentesting"]
date: "2026-12-16"
level: "Principiante"
---

## Por qué prefiero esto sobre buscar en el navegador

Ya menciono `searchsploit` de pasada en varios de mis artículos — para verificación de versiones de kernel, para buscar exploits de productos concretos. Lo que no había explicado es cómo lo uso más allá de una búsqueda simple, que es donde de verdad ahorra tiempo respecto a ir a la web de Exploit-DB cada vez.

## Actualizar la base de datos local primero

SearchSploit trabaja contra una copia local de Exploit-DB, así que si llevas tiempo sin actualizarla, te puedes perder exploits publicados recientemente:

```bash
searchsploit -u
```

Vale la pena correrlo al empezar cualquier sesión de trabajo nueva, no asumir que la base local está al día.

## Búsqueda básica y por qué el orden de palabras importa

```bash
searchsploit apache 2.4.49
```

SearchSploit busca coincidencias en el título del exploit, así que el orden y la especificidad de los términos cambia bastante los resultados. Una búsqueda demasiado genérica (`apache`) devuelve páginas de resultados irrelevantes; una demasiado específica puede no encontrar nada si el título del exploit no coincide exactamente con la versión que buscas.

## Filtrar por tipo

```bash
searchsploit -t apache
```

`-t` busca solo en el título, más restrictivo que la búsqueda por defecto que también mira en el cuerpo del exploit.

```bash
searchsploit --exclude="dos" apache
```

Excluyo exploits de tipo denial-of-service cuando lo que busco es explotación real (RCE, privilege escalation) — en un pentest con alcance limitado, tumbar un servicio con un DoS casi nunca es lo que necesitas confirmar.

## Ver el código del exploit sin salir de la terminal

```bash
searchsploit -x 50383
```

`-x` (examine) abre el exploit directamente en el editor por defecto sin tener que buscarlo manualmente en el sistema de archivos primero. Esto es lo que hago siempre antes de usar cualquier exploit — igual que mencioné con los PoCs de CVEs, leerlo completo antes de ejecutarlo, no fiarme solo del título.

## Copiar el exploit a tu directorio de trabajo

```bash
searchsploit -m 50383
```

`-m` (mirror) copia el exploit del repositorio local a tu directorio actual, listo para modificar (casi siempre hay que ajustar IP, puerto, o algún offset específico del entorno) sin tocar la copia maestra del repositorio.

## Buscar por CVE directamente

```bash
searchsploit --cve CVE-2021-44228
```

Cuando ya tienes el identificador CVE de tu proceso de análisis de vulnerabilidades (el que until describí en mi artículo sobre cómo leer un CVE), esto es más directo que buscar por nombre de producto y esperar que el título coincida.

## Combinarlo con el flujo de análisis de CVE

El proceso completo que sigo: identifico el CVE por la fuente primaria (NVD, advisory del proveedor), confirmo que la versión afectada coincide con lo que tengo delante, y solo entonces uso `searchsploit --cve` para ver si hay un PoC público disponible — en ese orden, no al revés. Buscar el exploit antes de confirmar que el CVE aplica de verdad es exactamente el error que until describí al principio de aquel artículo.