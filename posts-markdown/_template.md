---
title: "Título directo, sin gancho de marketing (60-65 caracteres)"
description: "Qué vas a encontrar en el artículo, en una frase. 140-160 caracteres."
slug: "slug-en-minusculas-con-guiones"
category: "Pentesting"   # Pentesting | OSINT | Redes | Linux | Python | Certificaciones | Vulnerabilidades | Herramientas
tags: ["tag1", "tag2"]
date: "2024-01-01"
# author: se omite a propósito — si no se indica, se usa el autor de config/site.json.
# Solo añade "author" aquí si el artículo lo escribió alguien distinto.
level: "Intermedio"       # Principiante | Intermedio | Avanzado
---

<!--
============================================================
CÓMO ESCRIBIR UN ARTÍCULO PARA ESTE BLOG (no para Google)
============================================================
Esto NO es una plantilla de "introducción + 5 puntos + conclusión".
Esa estructura es la que hace que el contenido huela a IA. En su lugar:

1. Empieza por el problema concreto, no por una definición de diccionario.
   Mal:  "Nmap es una herramienta de escaneo de redes muy utilizada..."
   Bien: "Llevaba diez minutos viendo timeouts en un escaneo -p- y el
          problema era que me había olvidado el -T4."

2. Usa comandos que hayas ejecutado de verdad, con su output real
   (o un output plausible, no inventado a lo "Lorem ipsum").

3. Incluye al menos un error común o un "esto me la jugó una vez".
   Eso es lo que diferencia una nota técnica real de un resumen.

4. No cierres con "En conclusión, esta herramienta es fundamental para...".
   Cierra con algo útil: el siguiente paso lógico, un enlace a otra nota,
   o directamente no cierres nada si el artículo ya dijo lo que tenía que decir.

5. Tono: como si le explicaras esto a otro pentester por Slack, no como
   si rellenaras una ficha de producto.

Borra este bloque de comentario antes de publicar.
============================================================
-->

## [Plantea el problema o el contexto, no una definición]

Texto.

## [Apartado técnico con comandos reales]

```bash
comando --con-flags-reales
```

¿Qué hace exactamente cada flag? ¿Cuál es la trampa habitual aquí?

## Algo que se suele romper

Describe un error común, un mensaje de error real, o una decisión que
parece obvia pero no lo es.
