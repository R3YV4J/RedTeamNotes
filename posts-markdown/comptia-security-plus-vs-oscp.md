---
title: "CompTIA Security+: ¿merece la pena antes del OSCP?"
description: "Por qué hice el Security+ antes de lanzarme al OSCP, qué cubre realmente, y en qué se diferencia de una certificación práctica de pentesting."
slug: "comptia-security-plus-vs-oscp"
category: "Certificaciones"
tags: ["Security+", "CompTIA", "certificaciones"]
date: "2026-06-11"
level: "Principiante"
---

## La pregunta que más me hacen sobre certificaciones

"¿Hago el Security+ o me lanzo directo al OSCP?" Depende de dónde partas,
pero mi experiencia fue: hice el Security+ primero, y no me arrepiento,
aunque no es por lo que la gente suele pensar. No fue por el contenido
técnico — fue porque me obligó a tener vocabulario y conceptos de
seguridad organizados antes de meterme en algo tan práctico y exigente
como el PEN-200.

## Qué es realmente el Security+

Es una certificación de **conceptos**, no de habilidades prácticas de
explotación. Es examen tipo test (con algunas preguntas de simulación
práctica, pero nada parecido a comprometer una máquina real). Cubre:

```text
- Conceptos generales de seguridad (CIA triad, gestión de riesgos)
- Amenazas, ataques y vulnerabilidades (tipos, no explotación)
- Arquitectura y diseño de seguridad
- Gestión de identidad y accesos
- Gestión de riesgos
- Criptografía y PKI (a nivel conceptual)
```

Si vienes de cero, esto te da el mapa mental de "qué es qué" en
ciberseguridad — términos que vas a encontrar constantemente en
documentación, advisories de CVE, o conversaciones con otros profesionales,
sin tener que aprenderlos sobre la marcha mientras intentas entender algo
más técnico.

## La diferencia real con el OSCP

| | Security+ | OSCP |
|---|---|---|
| Formato | Test de opción múltiple + simulaciones | Examen práctico de 23h45 |
| Qué mide | Conocimiento conceptual | Capacidad de comprometer sistemas reales |
| Dificultad de preparación | Memorización + comprensión | Práctica extensa en laboratorio |
| Vigencia | Requiere renovación (CEUs) | No caduca |
| Utilidad en pentesting puro | Limitada — es contexto, no habilidad | Directa |

Si tu objetivo final es pentesting ofensivo, el Security+ no te enseña a
hacerlo. Lo que aporta es el contexto: entender qué es un ataque de
"living off the land", qué diferencia hay entre IDS e IPS, qué implica
"zero trust" — conceptos que en el PEN-200 se asumen como ya conocidos y no
se explican desde cero.

## A quién le sirve más

Te sirve más el Security+ primero si:

- Vienes de fuera de IT y necesitas vocabulario base antes de nada técnico
- Quieres un puesto que combine seguridad con gestión/cumplimiento, no solo
  pentesting puro
- Tu empresa lo pide como requisito (es habitual en sector público y
  contratistas de EE.UU. por el DoD 8570)

Te conviene saltártelo e ir directo a práctica (TryHackMe, HackTheBox, y
luego OSCP) si:

- Ya tienes experiencia práctica en sistemas/redes
- Tu objetivo es pentesting ofensivo específicamente, no seguridad general
- Prefieres aprender haciendo en vez de memorizando definiciones primero

## Cómo me preparé

Usé el libro oficial de Sybex más práctica de preguntas (Jason Dion en
Udemy tiene un curso bastante completo y barato). Lo hice en unas 6 semanas
a tiempo parcial. La parte que más me costó no fue la técnica sino la
terminología de gestión de riesgos y cumplimiento (frameworks tipo NIST,
ISO 27001 a nivel superficial) — eso no lo había tocado antes y no es
intuitivo si vienes del lado puramente técnico.

## Lo que no haría igual

Si lo repitiera, no le dedicaría tanto tiempo a memorizar puertos y
protocolos específicos que el examen pregunta de forma muy literal (tipo
"¿qué puerto usa X protocolo") — eso se aprende solo con la práctica
posterior y memorizarlo sin contexto no se queda. Me hubiera enfocado más
en los conceptos de arquitectura y gestión de riesgo, que sí me costó
interiorizar y que sí se quedan siendo relevantes después, incluso en
pentesting puro (entender qué le importa de verdad a una organización
ayuda a priorizar qué reportar como crítico).

## Conclusión práctica

No es un escalón obligatorio hacia el OSCP, pero si vienes de fuera de un
perfil técnico puro, te ahorra fricción conceptual más adelante. Si ya
tienes esa base por otra vía (estudios de redes/sistemas, experiencia
previa en IT), probablemente estés perdiendo el tiempo con el Security+ y
te convenga ir directo a práctica.
