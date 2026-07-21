---
title: "Maltego para OSINT: cuándo sirve y cuándo es perder el tiempo"
description: "Cómo monto un grafo en Maltego para reconocimiento de organizaciones, qué transforms uso de verdad y por qué la versión Community se queda corta rápido."
slug: "osint-maltego-tutorial"
category: "OSINT"
tags: ["OSINT", "maltego", "reconocimiento"]
date: "2026-02-19"
level: "Intermedio"
---

## Por qué uso Maltego (y por qué no siempre)

Maltego sirve para una cosa concreta: convertir una lista plana de datos
sueltos (dominios, emails, nombres) en un grafo donde las relaciones se ven
a simple vista. Es muy útil cuando tienes diez fragmentos de información de
una organización y necesitas ver qué conecta con qué. Es mucho menos útil si
solo necesitas resolver un dominio o buscar un email — para eso uso
`theHarvester` o una query directa, porque montar un grafo para eso es
gastar tiempo en la interfaz en vez de en la investigación.

> El uso de OSINT tiene que respetar la normativa de protección de datos
> aplicable (RGPD en la UE). Esto es para investigar con alcance autorizado,
> no para acosar a nadie ni saltarte consentimientos.

## Instalación

En Kali viene preinstalado. Si no:

```bash
sudo apt update && sudo apt install maltego -y
```

La alternativa es bajar la Community Edition desde la web oficial, que pide
registro y te limita a 12 resultados por transform. Esa limitación es el
motivo por el que en proyectos algo grandes acabas necesitando la versión de
pago — con 12 resultados no llegas a mapear ni los subdominios de una
empresa mediana.

## El flujo que realmente sigo

No empiezo lanzando transforms al azar. El orden que me funciona:

```text
1. Domain (empresa.com)
   → To DNS Name [DNS]        → subdominios
   → To IP Address            → infraestructura detrás de cada subdominio

2. De los subdominios "interesantes" (admin, vpn, mail, dev...)
   → To Website [Quick Lookup] → confirmar que responden y qué tecnología usan

3. Domain
   → To Email addresses        → empleados potenciales, suele dar ruido

4. Cada Email address con pinta real (no genérico tipo info@)
   → To Person                 → cruzar con perfiles públicos
```

El punto 3 es el que más ruido genera. `To Email addresses` te devuelve
cualquier cosa indexada por los motores que usa de fuente, incluyendo
direcciones de contacto genéricas que no aportan nada para mapear personal
real. Filtro a mano antes de seguir con el punto 4, si no el grafo se llena
de nodos que no significan nada.

## Transforms que uso de verdad

De la lista completa, estos son los que repito en casi cualquier investigación:

| Transform | Para qué |
|---|---|
| `To DNS Name [DNS]` | Subdominios — el punto de partida casi siempre |
| `To IP Address [DNS]` | Saber qué infraestructura hay detrás de cada subdominio |
| `To Website [Quick lookup]` | Confirmar que un host responde antes de seguir investigando |
| `To Email addresses` | Útil pero con ruido, filtrar después |
| `To Person [using Natural Name]` | Solo cuando ya tienes un email o nombre concreto, no a ciegas |

## Lo que no esperaba la primera vez: el límite de transforms gratuitos

Si usas la Community Edition con las transforms públicas estándar, te vas a
topar con el límite de 12 resultados bastante rápido en cualquier dominio
con presencia real. La sensación es que el grafo "se corta" sin avisar
mucho. No es un bug, es la licencia. Si necesitas profundidad real, hay dos
caminos: pagar la versión de pago, o montar tus propios transforms locales
con datos que ya tengas (por ejemplo, resultados de tu propio `theHarvester`
importados como CSV).

## Exportar para el informe

```text
File → Export → To Image (PNG/JPEG)
File → Export → To Table (CSV) — mejor para anexos de informe que la imagen
```

El CSV es lo que realmente uso en el entregable final; la imagen del grafo
queda bien para una vista general en la primera página, pero un cliente no
va a leer relaciones de un grafo con 80 nodos, va a leer una tabla.

## Cuándo no usar Maltego

Si la investigación es solo "¿este dominio tiene subdominios con un panel de
admin expuesto?", monta un escaneo directo con `subfinder` + `httpx` y ahorra
el tiempo de la interfaz gráfica. Maltego gana cuando el valor está en ver
relaciones entre múltiples entidades distintas, no cuando es un único tipo
de búsqueda repetida.
