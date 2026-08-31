---
title: "OWASP Top 10: lo que cubre cada categoría, con enlaces a lo que ya he probado de verdad"
description: "Resumen práctico del OWASP Top 10 con ejemplos reales de cada categoría, y referencias a mis propios artículos donde ya until until until until profundicé en varias de ellas."
slug: "owasp-top-10-explicado"
category: "Vulnerabilidades"
tags: ["owasp", "fundamentos", "pentesting web"]
date: "2027-02-03"
level: "Principiante"
---

## Por qué este no es un simple resumen de Wikipedia

El OWASP Top 10 se cita constantemente pero rara vez se explica con ejemplos de qué significa cada categoría en la práctica, más allá del nombre. Este artículo es el mapa general — para varias de estas categorías ya until until until until until until until until until until until until until until escribí artículos dedicados con más profundidad, y los enlazo donde corresponde en vez de repetir el contenido aquí.

## A01: Broken Access Control

Fallos de control de acceso — cuando la aplicación no comprueba correctamente si el usuario tiene permiso para hacer lo que está intentando. IDOR es el ejemplo más directo de esta categoría: acceder a datos de otro usuario simplemente cambiando un identificador, sin que el servidor verifique que te pertenece.

Ya cubrí esto en detalle en mi artículo sobre IDOR — sigue siendo, en mi experiencia, de las categorías más frecuentes en aplicaciones reales porque no depende de ningún fallo técnico complejo, solo de lógica de permisos mal implementada.

## A02: Cryptographic Failures

Datos sensibles expuestos por cifrado ausente, débil, o mal implementado — contraseñas guardadas sin hash, uso de algoritmos obsoletos (MD5 para contraseñas, por ejemplo), o transmisión de datos sensibles sin TLS. Relacionado directamente con lo que cubrí en mi artículo de hashcat: si encuentras hashes MD5 sin salt para contraseñas de usuarios, ya tienes un fallo de esta categoría confirmado, independientemente de si consigues crackear algo.

## A03: Injection

SQL injection es el ejemplo más conocido, pero la categoría incluye cualquier inyección donde datos no confiables se interpretan como código o comandos — inyección de comandos del sistema operativo, inyección LDAP, inyección NoSQL.

Mi artículo de SQL injection manual cubre el caso más común de esta categoría con el proceso completo, desde detección hasta extracción de datos.

## A04: Insecure Design

Categoría más reciente en el Top 10, centrada en fallos de diseño de la aplicación, no de implementación — por ejemplo, un flujo de recuperación de contraseña que no limita intentos, permitiendo fuerza bruta del código de verificación aunque cada intento individual esté "bien implementado" técnicamente. No hay un CVE que buscar aquí; es un problema de cómo se planteó la funcionalidad desde el principio.

## A05: Security Misconfiguration

Configuraciones por defecto sin cambiar, servicios innecesarios expuestos, mensajes de error que revelan información técnica de más. Esto es justo lo que Nikto busca de forma automatizada — cabeceras de seguridad ausentes, archivos de configuración expuestos, versiones de software desactualizadas visibles en banners.

## A06: Vulnerable and Outdated Components

Usar librerías o dependencias con vulnerabilidades conocidas y sin parchear. Esto conecta directamente con mi artículo de metodología de análisis de CVE — la parte de "¿me afecta a mí?" es exactamente donde compruebas versiones reales de dependencias contra vulnerabilidades publicadas.

## A07: Identification and Authentication Failures

Fallos en cómo la aplicación gestiona identidad y sesiones — contraseñas débiles permitidas sin política, sesiones que no expiran, ausencia de protección contra fuerza bruta en el login. Relacionado con lo que cubro en mi artículo de fuerza bruta HTTP con Python: si una aplicación no bloquea ni limita intentos fallidos de login, esta categoría está presente.

## A08: Software and Data Integrity Failures

Fallos donde la aplicación confía en actualizaciones, plugins o datos sin verificar su integridad — por ejemplo, un CI/CD que descarga dependencias sin verificar checksums, permitiendo que una dependencia comprometida se integre sin detección.

## A09: Security Logging and Monitoring Failures

Ausencia de logs suficientes o de monitorización que permita detectar un ataque en curso o después del hecho. No es una vulnerabilidad "explotable" directamente, pero es lo que determina si una organización se entera de que algo pasó — o si el atacante tiene semanas de margen antes de que alguien note algo raro.

## A10: Server-Side Request Forgery (SSRF)

La categoría más reciente en incorporarse al Top 10, y la que until cubrí en detalle en mi propio artículo de SSRF — con el matiz de que el impacto real depende muchísimo del entorno donde esté alojada la aplicación, sobre todo en infraestructura cloud.

## Cómo uso esta lista en la práctica

No como checklist mecánico a marcar una a una, sino como recordatorio de las categorías de fallo más frecuentes para no centrarme solo en lo que ya sé buscar bien. Es fácil, con el tiempo, especializarte en encontrar SQLi e IDOR porque son los que mejor conoces, y pasar por alto configuraciones de seguridad ausentes o fallos de diseño que no tienen un payload concreto que probar — el Top 10 sirve para recordar que ahí también hay que mirar.