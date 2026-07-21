---
title: "Burp Suite: cómo lo uso en una auditoría web real"
description: "El flujo que sigo con Burp Suite Community para encontrar IDORs y otros fallos web, y por qué la versión gratuita se queda corta en cierto punto."
slug: "burp-suite-guia-esencial"
category: "Herramientas"
tags: ["burp suite", "pentesting web", "proxy"]
date: "2026-03-04"
level: "Principiante"
---

## Lo primero que se rompe: el certificado

La primera vez que configuré Burp en una máquina nueva, se me olvidó
instalar el certificado CA antes de navegar por HTTPS, y pasé diez minutos
viendo errores de "conexión no segura" en el navegador pensando que era un
problema de Burp. No lo era — era que no había importado el certificado.
Si te pasa esto, es casi siempre eso.

```text
1. Con el proxy de Burp activo, visita: http://burp
2. Descarga cacert.der
3. Impórtalo en el navegador como autoridad raíz de confianza
```

> Esto es para aplicaciones propias, entornos de laboratorio (PortSwigger
> Web Security Academy) o con autorización explícita por escrito.

## Configuración del proxy

Uso FoxyProxy para no tener que cambiar la configuración del navegador a
mano cada vez:

```text
IP: 127.0.0.1
Puerto: 8080
```

## Los módulos que realmente uso

De toda la interfaz, el 80% del trabajo pasa por tres pestañas:

| Módulo | Para qué |
|---|---|
| **Proxy** | Ver e interceptar todo lo que pasa |
| **Repeater** | Reenviar una petición modificada, una y otra vez, sin reescribirla entera |
| **Intruder** | Automatizar fuzzing sobre un parámetro |

Decoder y Comparer los uso, pero mucho menos — Decoder cuando necesito
decodificar Base64 o JWT rápido sin salir de Burp, Comparer cuando dos
respuestas se parecen mucho y necesito ver la diferencia exacta.

## Caso real: encontrar un IDOR

Esto es de un ejercicio de práctica, no de un cliente real, pero el patrón
es exactamente el que busco siempre:

```text
1. Inicio sesión como Usuario A
2. Intercepto la petición de mi propio perfil:
   GET /api/user/1234/profile

3. Envío a Repeater, cambio el ID:
   GET /api/user/1235/profile

4. Si la respuesta trae datos de otro usuario sin que se compruebe
   que el 1235 me pertenece → IDOR confirmado
```

Lo que parece obvio escrito así, pero no lo es tanto en la práctica: el
paso 4 falla a veces porque la API devuelve un 200 con un JSON vacío en
vez de un 403/404. Si solo miras el código de estado, te lo puedes saltar.
Hay que mirar también el contenido de la respuesta, no solo el status code.

## Repeater para probar una inyección SQL manual

```text
Petición original:
GET /producto?id=5 HTTP/1.1

Modificada en Repeater:
GET /producto?id=5' HTTP/1.1
```

Si la respuesta cambia a un error de sintaxis SQL visible (algo tipo
"you have an error in your SQL syntax"), ahí tienes una señal clara. Lo que
no hago es parar ahí y asumir que ya está — confirmar una SQLi de verdad
(no solo un error revelado) requiere más pasos, pero el error de sintaxis es
la señal que me dice "sigue por aquí".

## Intruder: la limitación que te vas a encontrar

Community Edition limita la velocidad de Intruder de forma notable. Para
una lista de pruebas pequeña (decenas de valores) no se nota. Para algo de
miles de entradas (un diccionario de contraseñas, por ejemplo), la
diferencia de tiempo frente a la versión Pro es considerable. Cuando
necesito volumen real, complemento con `ffuf` por línea de comandos, que no
tiene ese límite:

```bash
ffuf -u http://objetivo/login -X POST \
  -d "username=admin&password=FUZZ" \
  -w passwords.txt -fc 401
```

## Extensiones que uso de verdad

De toda la BApp Store, las que repito en casi cualquier auditoría:

- **JSON Web Tokens** — decodifica y permite editar JWTs sin salir de Burp
- **Param Miner** — encuentra parámetros ocultos que la app acepta aunque
  no estén documentados, útil para cache poisoning y parámetros de debug
  olvidados

## Cuándo Burp no es la herramienta

Si lo que necesito es un escaneo automatizado masivo de muchos hosts a la
vez, Burp (sobre todo en su versión Community, sin scanner activo) no es lo
más eficiente. Para ese caso uso herramientas de escaneo dirigidas a
volumen y dejo Burp para el análisis manual fino de una aplicación
concreta — son complementarios, no sustitutos.
