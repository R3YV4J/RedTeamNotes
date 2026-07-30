---
title: "Gobuster: los tres modos que uso más allá del descubrimiento de directorios"
description: "Modo dir, dns y vhost de gobuster explicados con ejemplos reales, y por qué cada uno resuelve un problema distinto que ffuf también cubre pero con sintaxis diferente."
slug: "gobuster-guia-completa"
category: "Herramientas"
tags: ["gobuster", "fuzzing", "pentesting web", "reconocimiento"]
date: "2026-12-09"
level: "Principiante"
---

## Por qué tengo tanto gobuster como ffuf

Ya escribí sobre ffuf, que es más flexible en muchos aspectos. Pero gobuster sigue teniendo su sitio: su sintaxis específica por modo (`dir`, `dns`, `vhost`) hace que ciertas tareas sean más rápidas de escribir sin tener que montar los flags genéricos de ffuf desde cero cada vez. No es que uno sea mejor que el otro en abstracto — cada uno tiene su momento.

## Modo dir: descubrimiento de directorios

```bash
gobuster dir -u http://objetivo.com -w /usr/share/seclists/Discovery/Web-Content/common.txt
```

La diferencia práctica con ffuf en este modo es mínima — ambos hacen esencialmente lo mismo. La ventaja de gobuster aquí es la sintaxis más corta y directa cuando no necesitas el nivel de personalización de filtrado que ffuf permite.

```bash
# Con extensiones y filtrando por código de estado
gobuster dir -u http://objetivo.com -w common.txt -x php,bak,txt -b 404,403
```

`-b` excluye (blacklist) los códigos de estado indicados, en vez de tener que especificar qué incluir.

## Modo dns: fuerza bruta de subdominios

Este es el que uso con más frecuencia respecto a ffuf, porque gobuster tiene el modo DNS integrado de forma nativa, sin tener que simular la petición con cabeceras manuales:

```bash
gobuster dns -d objetivo.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

Con resolución de IPs incluida directamente en la salida, útil para ver de un vistazo qué subdominios responden y a qué apuntan:

```bash
gobuster dns -d objetivo.com -w subdomains.txt -i
```

`-i` muestra las IPs resueltas junto a cada subdominio encontrado, ahorrando el paso extra de resolver cada uno por separado después.

## Modo vhost: virtual hosts

El equivalente al fuzzing de vhost que hice con ffuf usando la cabecera Host manual, pero con sintaxis dedicada:

```bash
gobuster vhost -u http://objetivo.com -w subdomains.txt --append-domain
```

`--append-domain` añade automáticamente el dominio base a cada palabra de la wordlist, evitando tener que preparar la wordlist con el dominio completo ya incluido en cada línea.

## Diferencia real de rendimiento con ffuf

En la práctica, para volúmenes grandes de wordlist, ffuf suele ser algo más rápido por cómo maneja la concurrencia, pero la diferencia no es dramática en la mayoría de casos de uso normales. La elección entre uno u otro para mí depende más de qué sintaxis tengo más fresca en la cabeza en el momento, o si necesito el filtrado más fino que ffuf permite con `-fs`/`-fw`/`-fl` combinados.

## Cuándo prefiero gobuster sobre ffuf

Cuando el objetivo es simple y directo — un descubrimiento de directorios estándar sin necesidad de filtrado complejo, o una fuerza bruta de subdominios donde quiero la resolución de IP integrada sin pasos extra. Para cualquier caso donde necesito filtrar resultados por tamaño de respuesta de forma precisa (aplicaciones con páginas "no encontrado" personalizadas que devuelven 200), ffuf me da más control directo.