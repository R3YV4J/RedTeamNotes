---
title: "Preparando la eWPT: lo que cubre y cómo lo estoy enfocando"
description: "Notas sobre la preparación de la eWPT de eLearnSecurity: qué diferencia hay con la eJPTv2, qué partes del temario son más densas y cómo estoy practicando."
slug: "ewpt-preparacion"
category: "Certificaciones"
tags: ["eWPT", "eLearnSecurity", "certificaciones", "pentesting web"]
date: "2026-07-01"
level: "Intermedio"
---

## Qué es la eWPT y por qué después de la eJPTv2

La eWPT (eLearnSecurity Web Application Penetration Tester) es un paso
natural después de la eJPTv2 si quieres especializarte en aplicaciones web.
Mientras la eJPTv2 toca todo un poco (redes, sistemas, web), la eWPT se
centra específicamente en vulnerabilidades web y cómo explotarlas de forma
metódica.

Estoy en preparación ahora mismo, así que esto no es un "lo hice y te
cuento" — es lo que voy aprendiendo mientras avanzo.

## Qué cubre el temario

El curso oficial de INE para la eWPT toca estas áreas principales:

```text
- Fundamentos de HTTP/HTTPS: métodos, headers, cookies, sesiones
- Reconocimiento web: fingerprinting, enumeración de directorios
- Vulnerabilidades de inyección: SQLi, XSS, XXE, SSTI
- Vulnerabilidades de autenticación: broken auth, IDOR, JWT
- Lógica de negocio: encontrar fallos que los escáneres no detectan
- Burp Suite como herramienta principal de todo el proceso
```

La diferencia con la eJPTv2 en la parte web es notable: aquí no es "prueba
este payload hasta que algo funcione", sino que hay un énfasis real en
entender por qué funciona cada técnica y cómo confirmar el impacto real,
no solo la existencia del fallo.

## Lo que más me está costando hasta ahora

La lógica de negocio. Las vulnerabilidades de inyección tienen un patrón
reconocible: pruebas, observas la respuesta, confirmas. Las vulnerabilidades
de lógica de negocio dependen de entender qué se supone que hace la
aplicación y qué asunciones incorrectas hace el desarrollador sobre cómo
se va a usar. No hay un payload estándar para eso.

También estoy dedicando bastante tiempo a Burp Suite más allá de lo básico —
el Intruder y el Repeater los tenía bastante asumidos de la eJPTv2, pero
el análisis manual de lógica de sesiones y JWT es territorio nuevo.

## Cómo estoy practicando

Combino el material oficial de INE con los laboratorios de PortSwigger Web
Security Academy, que son gratuitos y están organizados exactamente por los
tipos de vulnerabilidades que cubre el temario. Para SQLi y XSS, PortSwigger
tiene más variedad de escenarios que los laboratorios de INE, así que uso
ambos en paralelo.

También tengo montado un servidor vulnerable local (DVWA y WebGoat) para
poder probar cosas sin depender de estar conectado a un laboratorio en la
nube.

## Cuándo espero presentarme

Próximamente. Cuando lo haga, actualizaré esto con cómo fue el examen real.
Si ya lo aprobé cuando estás leyendo esto y no lo actualicé, es que me
olvidé — o que no fue tan bien como esperaba y necesité tiempo para escribir
sobre ello.
