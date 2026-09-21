---
title: "Metadatos EXIF: lo que se puede sacar de una imagen sin tocarla"
description: "Cómo extraigo metadatos EXIF con exiftool, qué información revela realmente una foto (y qué ya no, por las políticas de las redes sociales) y el caso donde la geolocalización delató más de lo esperado."
slug: "metadatos-exif-osint"
category: "OSINT"
tags: ["exif", "metadatos", "OSINT", "exiftool"]
date: "2027-01-06"
level: "Principiante"
---

## Por qué esto sigue siendo relevante aunque las redes sociales limpien metadatos

La mayoría de plataformas grandes (Twitter/X, Instagram, Facebook) eliminan los metadatos EXIF al subir una imagen, precisamente para evitar filtraciones de ubicación no intencionadas. Pero eso no aplica a fotos compartidas directamente (por email, por WhatsApp sin comprimir, subidas a un sitio propio sin ese procesamiento), que es donde este tipo de análisis todavía da resultados reales.

> Analizar metadatos de imágenes que son públicas o que tienes autorización para revisar. Esto no es una vía para investigar a alguien sin motivo legítimo.

## Extracción básica con exiftool

```bash
exiftool imagen.jpg
```

La salida incluye desde lo más básico (fecha, hora, modelo de cámara o teléfono) hasta, si está presente, coordenadas GPS exactas.

```bash
exiftool -GPSLatitude -GPSLongitude imagen.jpg
```

Filtrar directamente a las coordenadas si eso es lo único que te interesa de la salida completa.

## Convertir las coordenadas a algo usable

exiftool devuelve las coordenadas en formato de grados/minutos/segundos, no directamente en el formato decimal que necesitas para pegar en Google Maps:

```bash
exiftool -c "%.6f" -GPSLatitude -GPSLongitude imagen.jpg
```

`-c "%.6f"` fuerza el formato decimal con 6 decimales de precisión, listo para copiar directamente en cualquier mapa.

## El caso donde la geolocalización delató más de lo esperado

En un ejercicio de OSINT autorizado, una imagen de un empleado compartida en un contexto interno (no en redes sociales, así que sin el filtrado de metadatos) tenía coordenadas GPS precisas que correspondían a las oficinas de la empresa — información que, combinada con la hora exacta del archivo, confirmaba horarios de presencia física que no eran públicos en ningún otro sitio. No era el objetivo de la investigación, pero mostró de forma directa por qué las políticas de compartir imágenes sin revisar importan tanto como cualquier otra medida de seguridad.

## Metadatos más allá del GPS

No solo ubicación — el software usado para editar la imagen, el modelo exacto de cámara o teléfono, y a veces el nombre de usuario del sistema operativo donde se procesó (típico en capturas de pantalla o archivos generados por ciertos programas):

```bash
exiftool -Software -Make -Model imagen.jpg
```

Esto puede confirmar, por ejemplo, si varias imágenes atribuidas a fuentes distintas fueron editadas con el mismo software y la misma configuración — indicio de que provienen de la misma persona u organización, aunque se presenten como independientes.

## Ver todos los metadatos sin filtrar nada

```bash
exiftool -a -u -g1 imagen.jpg
```

`-a` muestra todas las etiquetas incluso duplicadas, `-u` incluye etiquetas no conocidas, `-g1` agrupa por categoría — útil cuando quiero una vista exhaustiva en vez de solo los campos más comunes, por si algo relevante está en un campo poco habitual que no consultaría por defecto.

## Limpiar metadatos, el otro lado de esto

Si el objetivo es proteger tu propia información antes de compartir una imagen:

```bash
exiftool -all= imagen.jpg
```

Elimina todos los metadatos de golpe. Vale la pena tenerlo en cuenta no solo como técnica de investigación sino como higiene básica antes de compartir cualquier imagen propia fuera de plataformas que ya hacen esa limpieza automáticamente.