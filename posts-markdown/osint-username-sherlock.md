---
title: "Buscar una persona por su nombre de usuario: Sherlock y sus límites"
description: "Cómo uso Sherlock para encontrar perfiles de un mismo username en distintas plataformas, y por qué los falsos positivos son más frecuentes de lo que la herramienta admite."
slug: "osint-username-sherlock"
category: "OSINT"
tags: ["sherlock", "OSINT", "reconocimiento", "username enumeration"]
date: "2026-12-30"
level: "Principiante"
---

## Por qué esto es más útil de lo que parece al principio

La gente reutiliza el mismo nombre de usuario en varias plataformas más de lo que cree. Un username poco común encontrado en un contexto (un foro técnico, un commit de GitHub) muchas veces lleva directamente a un perfil de Twitter, Instagram o LinkedIn de la misma persona, simplemente porque nunca cambió el hábito de usar el mismo alias en todas partes.

> Esto es para reconocimiento de superficie de ataque en un pentest con alcance autorizado, o para tu propia higiene digital comprobando tu propia exposición. Usarlo para acosar o investigar a alguien sin motivo legítimo tiene implicaciones legales y éticas serias.

## Instalación y uso básico

```bash
git clone https://github.com/sherlock-project/sherlock.git
cd sherlock
pip install -r requirements.txt
python3 sherlock usuario_objetivo
```

Lanza comprobaciones en paralelo contra cientos de plataformas, y te devuelve una lista de URLs donde ese username existe.

## El problema de los falsos positivos

Esto es lo que más me hizo desconfiar de fiarme del resultado sin comprobar: algunas plataformas devuelven una página con código 200 incluso cuando el usuario no existe (por ejemplo, redirigiendo a una página genérica en vez de un 404 real). Sherlock detecta esto para las plataformas más comunes, pero no para todas — de una lista de 50 resultados "positivos", he tenido casos donde 3 o 4 eran falsos, y solo lo confirmas visitando el enlace a mano.

```bash
python3 sherlock usuario_objetivo --print-found
```

`--print-found` limita la salida a lo que Sherlock considera confirmado, pero sigo abriendo cada resultado relevante manualmente antes de darlo por bueno en cualquier informe.

## Filtrar por categoría de plataforma

```bash
python3 sherlock usuario_objetivo --site github --site twitter --site instagram
```

En vez de lanzar contra las cientos de plataformas que Sherlock conoce (muchas irrelevantes según el contexto de la investigación), limito a las que tienen sentido para el caso — si busco actividad técnica de alguien, priorizo GitHub, GitLab, Stack Overflow por encima de plataformas de citas o gaming que no aportan nada al objetivo.

## Exportar resultados

```bash
python3 sherlock usuario_objetivo --output resultado.txt
```

Para cruzar después con otras fuentes — por ejemplo, si un perfil de GitHub confirmado revela un email en el `README` o en commits públicos, eso alimenta directamente una búsqueda posterior con theHarvester o Google Dorking sobre ese email concreto.

## Variaciones del username que Sherlock no prueba solo

Sherlock busca el username exacto que le das. Si sospechas que la persona usa variaciones (con punto, con guión bajo, con un número al final), hay que lanzarlo varias veces con cada variante — la herramienta no genera automáticamente esas combinaciones por ti.

```bash
python3 sherlock usuario_objetivo usuario.objetivo usuario_objetivo1 --print-found
```

## Lo que Sherlock no te dice

Que un username exista en una plataforma no confirma que sea la misma persona que estás investigando — mucha gente usa alias genéricos o comunes que coinciden por casualidad entre usuarios distintos sin ninguna relación. La confirmación real viene de cruzar varias fuentes (foto de perfil coincidente, biografía con datos consistentes, actividad temporal alineada), no de un solo resultado de Sherlock por sí solo.