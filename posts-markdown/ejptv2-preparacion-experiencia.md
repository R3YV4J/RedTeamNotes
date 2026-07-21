---
title: "eJPTv2: lo que aprendes de verdad preparándola y lo que no esperaba del examen"
description: "Mi experiencia con la eJPTv2 de eLearnSecurity: qué cubre, cómo es el examen real, y por qué es mejor punto de entrada que el Security+ si ya sabes algo de redes."
slug: "ejptv2-preparacion-experiencia"
category: "Certificaciones"
tags: ["eJPTv2", "eLearnSecurity", "certificaciones", "pentesting"]
date: "2026-06-11"
level: "Principiante"
---

## Por qué la eJPTv2 y no empezar directamente con algo más gordo

Cuando empecé a mirar certificaciones de pentesting, la respuesta obvia de
todo el mundo era "OSCP o nada". El problema: el OSCP asume que ya sabes
moverte por una red, explotar cosas básicas y documentar hallazgos. Yo no
tenía esa base, y pagar 1500€ para descubrirlo a las malas no me parecía
plan. La eJPTv2 cuesta mucho menos, cubre esa base de forma práctica, y
el examen es suficientemente real como para que no sea solo memorizar test.

Resultado: la hice, la aprobé, y me dio exactamente el contexto que me
faltaba para entender qué estaba haciendo en los laboratorios.

## Qué cubre el curso (INE Security Junior Penetration Tester)

El material oficial de INE que acompaña a la certificación toca:

```text
- Fundamentos de redes: TCP/IP, protocolos, routing básico
- Reconocimiento: Nmap, enumeración de servicios, footprinting
- Explotación: Metasploit como framework principal
- Web: SQLi básica, XSS, directory traversal
- Post-explotación: pivoting básico, transferencia de archivos
- Sistemas: Windows y Linux, diferencias en la metodología
```

No profundiza mucho en ningún área — es intencionalmente amplio y accesible.
Si ya tienes experiencia en redes o sistemas, la parte teórica la puedes
repasar rápido. Lo que de verdad importa son los laboratorios prácticos.

## Cómo es el examen de verdad

72 horas de acceso a una red con varias máquinas y un cuestionario de
preguntas sobre lo que encuentras. No es "compromete estas máquinas y
envía un informe" — es más tipo "¿qué servicio corre en el puerto X del
host Y?" mientras exploras la red activamente.

Eso lo hace más accesible que el OSCP, pero también significa que puedes
superar el examen siendo más metódico que creativo. Lo que sí te obliga a
hacer de verdad: enumerar bien, no saltarte pasos, documentar lo que
encuentras mientras avanzas.

Lo que no esperaba: hay más pivoting de lo que el temario sugiere. Si no
tienes claro cómo moverse entre segmentos de red, el examen se complica
más de lo que debería para el nivel que se supone que evalúa.

## Lo que haría diferente en la preparación

Metasploit lo usé demasiado en la preparación y demasiado poco en el examen
(irónicamente). En los laboratorios de INE, Metasploit resuelve muchas cosas
de forma automática que en el examen conviene entender manualmente, porque
a veces el framework no funciona exactamente como esperas en un entorno
diferente y necesitas saber qué está pasando por debajo.

Mi recomendación: practica los laboratorios de INE, pero también haz algunas
máquinas de TryHackMe del path "Jr Penetration Tester" sin Metasploit para
entender la mecánica manual. Eso me hubiera ahorrado confusión en el examen.

## ¿Vale la pena en el CV?

Depende de para qué. Para entrar en empresas grandes con departamentos de
seguridad maduros, el nombre no pesa mucho comparado con el OSCP o el CRTO.
Para demos de que tienes interés real y base técnica mínima verificada, sí
hace su papel. Yo lo veo como un paso intermedio honesto: demuestra que
sabes lo básico de forma práctica, no solo que has memorizado definiciones.

Si estás empezando y quieres una certificación que te enseñe cosas útiles
(no solo que te evalúe cosas que ya sabes), la eJPTv2 cumple.
