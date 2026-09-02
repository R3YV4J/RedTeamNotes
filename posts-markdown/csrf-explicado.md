---
title: "CSRF: por qué sigue apareciendo aunque lleve años siendo conocido"
description: "Cross-Site Request Forgery explicado con un caso práctico, por qué las cookies SameSite no lo eliminan del todo, y cómo confirmo si una acción es realmente vulnerable."
slug: "csrf-explicado"
category: "Vulnerabilidades"
tags: ["csrf", "pentesting web", "fundamentos"]
date: "2027-01-27"
level: "Intermedio"
---

## Por qué pensaba que CSRF ya no era relevante

Con SameSite cookies siendo el comportamiento por defecto en navegadores modernos, until asumía que CSRF estaba prácticamente resuelto a nivel de plataforma. La realidad es más matizada: SameSite mitiga el caso más común, pero no todos — aplicaciones con configuraciones específicas, subdominios compartidos, o formularios que no dependen de cookies de sesión de la forma habitual, siguen siendo vulnerables.

## El mecanismo básico

CSRF aprovecha que el navegador envía automáticamente las cookies de sesión en cualquier petición hacia ese dominio, sin importar desde qué página se originó la petición. Si una aplicación no verifica que la petición vino realmente de su propio formulario (con un token anti-CSRF, por ejemplo), un atacante puede construir una página externa que fuerza al navegador de la víctima a hacer esa petición en su nombre.

```html
<!-- Página maliciosa alojada en cualquier otro sitio -->
<form action="http://banco-objetivo.com/transferir" method="POST">
  <input type="hidden" name="cuenta_destino" value="cuenta_atacante">
  <input type="hidden" name="cantidad" value="1000">
</form>
<script>document.forms[0].submit();</script>
```

Si la víctima tiene sesión activa en `banco-objetivo.com` y visita esta página externa, el navegador envía la petición con las cookies de sesión válidas incluidas automáticamente — la aplicación no tiene forma de distinguir esto de una petición legítima, a menos que implemente protección específica.

> Solo contra aplicaciones propias o con autorización explícita.

## Por qué GET es peor que POST para esto (y por qué POST tampoco te salva del todo)

Si una acción sensible se ejecuta con GET, el ataque es todavía más trivial — ni siquiera necesita un formulario, un simple `<img src="http://objetivo.com/borrar?id=5">` dispara la petición. Por eso una buena práctica básica es que acciones que modifican estado nunca vayan por GET. Pero cambiar a POST, por sí solo, no elimina el CSRF — solo elimina el vector más trivial; el formulario auto-enviado con JavaScript sigue funcionando igual contra POST si no hay ninguna otra protección.

## Cómo confirmo si una acción es vulnerable

Con Burp, intercepto la petición legítima de una acción sensible (cambio de email, transferencia, cambio de contraseña) y reviso si incluye algún token que cambia en cada sesión o petición:

```text
POST /cambiar-email
Cookie: session=abc123
csrf_token=x7f9a2b1...
new_email=nuevo@correo.com
```

Si ese `csrf_token` está presente y la aplicación lo valida server-side (no solo lo acepta sin comprobar), la acción está protegida. Confirmo la validación real quitando o alterando el token y reenviando — si la petición sigue funcionando igual sin el token correcto, la protección es cosmética, no real.

## SameSite cookies: qué protege y qué no

```text
Set-Cookie: session=abc123; SameSite=Strict
Set-Cookie: session=abc123; SameSite=Lax
Set-Cookie: session=abc123; SameSite=None
```

`Strict` bloquea el envío de la cookie en cualquier petición cross-site, incluida la navegación normal desde un enlace externo. `Lax` (el valor por defecto en navegadores modernos si no se especifica) permite el envío en navegación de nivel superior (como seguir un enlace) pero no en peticiones automáticas de formularios o `fetch` desde otro origen — lo que mitiga el caso clásico de CSRF, pero no elimina escenarios donde la propia navegación normal del usuario dispara la petición.

`None` desactiva la protección por completo, y requiere `Secure` obligatoriamente — a veces necesario en integraciones legítimas entre dominios distintos, pero reintroduce el riesgo de CSRF si la aplicación no compensa con otra protección.

## Cuándo sigo probándolo aunque vea SameSite activo

No doy por hecho que SameSite=Lax cierra el caso completamente. Reviso si hay subdominios que comparten el mismo dominio raíz (donde SameSite no protege entre ellos de la misma forma), y si existe algún endpoint que acepte la sesión por otro medio distinto a la cookie (un token en la URL, por ejemplo), lo cual reintroduce el vector aunque las cookies estén bien configuradas.

## Por qué esto sigue en cualquier checklist de pentest web

Porque la protección real depende de una implementación correcta de tokens anti-CSRF a nivel de aplicación, y SameSite es una red de seguridad del navegador, no un sustituto de esa implementación. Cuando una aplicación confía solo en SameSite sin tokens propios, sigue habiendo huecos — la comprobación manual con Burp de si el token existe y se valida de verdad sigue siendo necesaria, no solo mirar la cabecera de la cookie.