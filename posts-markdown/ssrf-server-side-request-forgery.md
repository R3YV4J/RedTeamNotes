---
title: "SSRF: cómo lo busco y por qué el impacto depende de dónde estés alojado"
description: "Server-Side Request Forgery explicado con ejemplos prácticos: de la URL controlada al acceso a metadatos de instancia en la nube, y por qué el mismo bug tiene impacto muy distinto según el entorno."
slug: "ssrf-server-side-request-forgery"
category: "Vulnerabilidades"
tags: ["ssrf", "pentesting web", "cloud security"]
date: "2027-01-20"
level: "Intermedio"
---

## Por qué el mismo bug puede ser "molesto" o "crítico"

La primera vez que until encontré un SSRF lo reporté como severidad media — al fin y al cabo, "solo" permitía que el servidor hiciera una petición a una URL que yo controlaba. Lo que no until until until until until until until until entendí hasta después es que en un entorno cloud (AWS, GCP, Azure), ese mismo bug puede escalar a robo de credenciales completas de la instancia, simplemente porque hay un endpoint de metadatos interno accesible solo desde el propio servidor — que es justo lo que el SSRF te permite alcanzar.

## Qué es, en la práctica

Un SSRF ocurre cuando una aplicación acepta una URL (o algo que se convierte en una) como parámetro y hace una petición HTTP a esa URL desde el propio servidor, sin validar suficientemente a dónde apunta:

```text
POST /api/generar-miniatura
{"url": "http://ejemplo.com/imagen.jpg"}
```

Si la aplicación descarga esa imagen para procesarla, y no valida que la URL apunte a un dominio permitido, puedes sustituirla por algo que el servidor sí puede alcanzar pero que tú no puedes desde fuera.

> Solo contra aplicaciones propias o con autorización explícita.

## El caso clásico: metadatos de instancia cloud

En AWS (y de forma similar en otros proveedores), cada instancia tiene un endpoint interno de metadatos accesible solo desde dentro de la propia red de la instancia:

```text
http://169.254.169.254/latest/meta-data/
```

Si el SSRF te permite hacer que el servidor pida esa URL en tu lugar, y te devuelve la respuesta (o parte de ella), puedes acabar leyendo credenciales temporales de IAM asociadas a esa instancia:

```text
{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}
```

Con esas credenciales, dependiendo de qué permisos tenga el rol asociado a la instancia, el impacto puede escalar de "leer una respuesta interna" a "control sobre recursos de la cuenta cloud completa" — de ahí que la severidad real dependa tanto del entorno de alojamiento, no solo del bug en sí.

## Otros objetivos internos, no solo cloud

```text
{"url": "http://localhost:6379/"}    → posible Redis interno sin autenticación
{"url": "http://192.168.1.5:8080/"}  → servicio interno no accesible desde fuera
{"url": "file:///etc/passwd"}        → si el esquema file:// no está bloqueado
```

El SSRF no solo sirve para llegar a metadatos cloud — es una forma de usar el servidor como proxy hacia cualquier red interna a la que él sí tiene acceso pero tú no.

## Bypasses comunes cuando hay un filtro de dominio

Muchas aplicaciones intentan mitigar SSRF con una lista blanca de dominios permitidos, pero la validación a veces es incompleta:

```text
http://dominio-permitido.com@169.254.169.254/
  → algunos parsers de URL leen esto como "usuario@host", validando
    solo la parte antes de la @ pero conectando al host real después

http://169.254.169.254#dominio-permitido.com
  → el fragmento después de # a veces se ignora en la validación
    pero no en la conexión real

http://[::ffff:169.254.169.254]/
  → representación IPv6 de una IP IPv4, que algunos filtros no reconocen
```

Ninguno de estos funciona siempre — depende completamente de cómo esté implementada la validación del lado servidor, pero son los primeros que pruebo cuando veo un filtro de dominio aparentemente bien hecho.

## Confirmar SSRF ciego con un servicio propio

Cuando la aplicación no refleja la respuesta de vuelta (SSRF ciego), uso un servicio que registra peticiones entrantes (Burp Collaborator, o un servidor propio con `netcat` escuchando) para confirmar que la petición efectivamente salió del servidor objetivo:

```bash
nc -lvnp 8888
```

```text
{"url": "http://tu-ip:8888/confirmacion-ssrf"}
```

Si ves la conexión entrante en tu listener, tienes confirmación de que el servidor hizo la petición, aunque nunca veas la respuesta en la aplicación.

## Por qué esto no aparece siempre en escáneres automáticos

Un escáner genérico no sabe qué URL interna tiene sentido probar en tu contexto específico — el endpoint de metadatos cloud, un servicio interno concreto de la infraestructura del objetivo, son cosas que dependen de conocer o suponer la arquitectura real detrás. Por eso SSRF es de las vulnerabilidades donde entender el entorno de despliegue (¿está en AWS? ¿en un datacenter propio? ¿qué servicios internos podría tener?) importa tanto como encontrar el parámetro vulnerable en sí.