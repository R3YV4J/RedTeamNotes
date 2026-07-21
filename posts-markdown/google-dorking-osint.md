---
title: "Google Dorking: encontrar información pública que nadie quiso exponer"
description: "Cómo uso operadores de búsqueda avanzados de Google para encontrar paneles de administración, archivos expuestos y configuraciones olvidadas sin tocar nada."
slug: "google-dorking-osint"
category: "OSINT"
tags: ["google dorking", "OSINT", "reconocimiento", "dorks"]
date: "2026-03-04"
level: "Principiante"
---

## Por qué Google es una herramienta de reconocimiento

Antes de hablar de Maltego, Shodan o cualquier herramienta especializada,
hay una cosa que cualquiera puede hacer con el navegador: buscar de forma
inteligente. Google indexa enormes cantidades de contenido que los
administradores de sistemas no tenían intención de exponer — archivos de
configuración, paneles de administración, listados de directorios, backups.

No hace falta instalar nada. Solo saber qué buscar.

> Buscar información pública disponible en Google no es ilegal. Acceder a
> sistemas sin autorización, aunque hayas llegado hasta ellos con un dork,
> sí lo es. La línea está en el momento en que interactúas con algo que no
> es tuyo.

## Los operadores básicos que más uso

```text
site:ejemplo.com
  Solo resultados de ese dominio.
  Útil para mapear qué tiene indexado una organización.

filetype:pdf site:ejemplo.com
  Busca archivos PDF en ese dominio.
  Funciona con: pdf, doc, xls, txt, xml, sql, log, conf...

intitle:"index of"
  Listados de directorios abiertos.
  Clásico para encontrar carpetas sin protección.

inurl:admin site:ejemplo.com
  URLs que contienen "admin" en ese dominio.
  Paneles de administración, formularios de login internos.

intext:"password" filetype:txt
  Archivos de texto que contienen literalmente la palabra "password".
  Encuentra cosas que no deberían ser públicas.
```

## Un ejemplo real de reconocimiento con dorks

Si estoy evaluando `empresa.com` (con autorización), el flujo que sigo:

```text
1. site:empresa.com
   → Miro cuántas páginas están indexadas y qué subdominios aparecen

2. site:empresa.com filetype:pdf OR filetype:doc OR filetype:xls
   → Documentos internos que quedaron públicos

3. site:empresa.com intitle:"index of"
   → Directorios sin protección

4. site:empresa.com inurl:login OR inurl:admin OR inurl:wp-admin
   → Paneles de acceso

5. "empresa.com" filetype:sql OR filetype:log OR filetype:env
   → Archivos sensibles indexados en cualquier servidor
```

El quinto es el que más sorpresas da: backups de bases de datos o archivos
`.env` con credenciales que alguien subió a un repositorio público sin
darse cuenta y Google indexó antes de que lo borraran.

## Google Hacking Database (GHDB)

Exploit-DB mantiene una base de datos pública de dorks organizados por
categoría (archivos sensibles, paneles de login, mensajes de error con
información de versiones, etc.). Es una referencia útil para ver qué tipo
de cosas se buscan habitualmente:

```text
https://www.exploit-db.com/google-hacking-database
```

No hace falta memorizar dorks — hace falta entender la lógica de los
operadores para construir los tuyos adaptados a lo que estés buscando.

## Lo que no encuentras con Google Dorking

Google no indexa todo. Contenido detrás de login, páginas dinámicas sin
URLs predecibles, y sitios que bloquean el crawler de Google quedan fuera.
Para eso hace falta complementar con otras herramientas: Shodan para
servicios expuestos, theHarvester para subdominios, o Wayback Machine para
versiones antiguas de páginas que ya no están indexadas.

El Dorking da el primer mapa. Las otras herramientas rellenan los huecos.
