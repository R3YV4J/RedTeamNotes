---
title: "IDOR: cómo lo busco más allá de cambiar un número en la URL"
description: "El proceso que sigo para encontrar Insecure Direct Object References de verdad, más allá del caso obvio de cambiar un ID numérico, y por qué el status code no basta para confirmarlo."
slug: "idor-como-lo-busco"
category: "Vulnerabilidades"
tags: ["idor", "pentesting web", "burp suite", "control de acceso"]
date: "2026-11-18"
level: "Intermedio"
---

## Por qué IDOR no es solo "cambiar el ID en la URL"

Ya mencioné un caso de IDOR en mi artículo de Burp Suite — cambiar `/api/user/1234/profile` por `/api/user/1235/profile`. Ese es el ejemplo de manual, pero limitarte a eso te hace pasar por alto la mayoría de IDORs reales, que aparecen en sitios menos evidentes: IDs en el cuerpo de una petición POST, referencias indirectas en cabeceras personalizadas, o identificadores que no son numéricos secuenciales sino UUIDs (donde "probar el siguiente número" no funciona).

## Los sitios donde de verdad los busco

No solo la URL. Reviso sistemáticamente:

```text
- Parámetros en la URL (el caso obvio)
- Cuerpo de peticiones POST/PUT en formato JSON
- Cabeceras personalizadas (X-User-Id, X-Account-Id)
- Cookies que contienen algún identificador
- Nombres de archivo en descargas (/download?file=factura_1234.pdf)
```

## El error de confiar solo en el status code

Ya lo until mencioné de pasada en el artículo de Burp: una API puede devolver 200 con un JSON vacío o con un mensaje de error genérico dentro del cuerpo, en vez de un 403/404 claro. Si solo miro el código de estado, un IDOR real me puede pasar desapercibido porque "parece" que no funcionó.

```text
Respuesta con IDOR real (código 200, pero vacío):
{"data": null}

Respuesta sin IDOR (código 200, con datos de otro usuario):
{"data": {"nombre": "Otro Usuario", "email": "..."}}
```

Comparo siempre el **tamaño de la respuesta** y el **contenido real**, no solo el status code — en Burp, esto se hace fácilmente enviando la petición modificada a Repeater y mirando la pestaña de respuesta completa, no solo el header de estado.

## UUIDs no significan que estás a salvo

Un error común es pensar que si los IDs son UUIDs (`a1b2c3d4-...`) en vez de números secuenciales, no hay IDOR posible porque "no se pueden adivinar". Eso es cierto para adivinar un UUID al azar, pero no elimina el problema si puedes **obtener** UUIDs de otros usuarios por otra vía — por ejemplo, si aparecen en una respuesta de listado que sí tienes permiso de ver, o en un enlace compartido públicamente.

```text
GET /api/documents?shared=true
→ devuelve lista con UUIDs de documentos compartidos

GET /api/documents/<uuid_ajeno>/download
→ ¿comprueba realmente que el UUID te pertenece, o solo que el formato es válido?
```

## Probar tanto lectura como escritura

No me quedo solo en si puedo **ver** datos de otro usuario (IDOR de lectura) — también pruebo si puedo **modificar o borrar** algo que no es mío, que suele tener impacto mayor:

```text
PUT /api/user/1235/profile
{"email": "atacante@evil.com"}
```

Si esto funciona contra el ID de otro usuario, no es solo una fuga de información — es un IDOR de escritura que permite modificar cuentas ajenas, categoría de gravedad completamente distinta a solo poder leer un perfil.

## Automatizar la comprobación con Burp Intruder

Cuando tengo varios IDs candidatos (por ejemplo, de un listado previo), uso Intruder para probar en bloque en vez de cambiar el valor a mano cada vez:

```text
GET /api/user/§1234§/profile
```

Con una lista de IDs conocidos como payload, y comparando el tamaño de respuesta de cada intento — los que devuelven un tamaño distinto al esperado (ni el tamaño del "no autorizado" limpio, ni exactamente vacío) son los que reviso a mano después.

## Por qué esto tiene tanto impacto en un informe real

A diferencia de una SQLi o un XSS, un IDOR no necesita ningún exploit técnico complejo — es un fallo de lógica de control de acceso, y precisamente por eso muchos escáneres automatizados no lo detectan bien. Es de las vulnerabilidades donde el análisis manual y el pensar "¿qué pasa si cambio esto que parece mío por algo que no lo es?" vale más que cualquier herramienta automatizada.