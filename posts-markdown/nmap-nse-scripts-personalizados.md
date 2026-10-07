---
title: "Scripts NSE personalizados en Nmap: cuándo escribo el mío propio"
description: "Cómo estructuro un script NSE básico cuando los que trae Nmap por defecto no cubren lo que necesito, y el caso donde me ahorró repetir la misma comprobación manual en 20 hosts."
slug: "nmap-nse-scripts-personalizados"
category: "Pentesting"
tags: ["nmap", "nse", "lua", "automatización"]
date: "2026-11-25"
level: "Avanzado"
---

## El caso que me hizo escribir mi primer script NSE

Ya cubrí en mi guía de Nmap los scripts NSE que uso de los que ya vienen incluidos. Pero hubo un caso concreto donde ninguno cubría lo que necesitaba: tenía que comprobar, en una red de 20 hosts, si un endpoint HTTP interno específico devolvía cierto texto en la respuesta — algo tan específico que no existía ningún script público para ello. Hacerlo a mano host por host con `curl` era viable pero tedioso; escribir un script NSE de 15 líneas resolvió el problema en un solo comando contra toda la red.

## Estructura básica de un script NSE

Los scripts NSE están escritos en Lua. La estructura mínima:

```lua
local shortport = require "shortport"
local http = require "http"
local stdnse = require "stdnse"

description = [[
Comprueba si un endpoint interno específico devuelve un texto conocido.
]]

author = "R3yv4j"
license = "Same as Nmap--See https://nmap.org/book/man-legal.html"
categories = {"discovery", "safe"}

portrule = shortport.http

action = function(host, port)
  local response = http.get(host, port, "/api/internal/status")
  if response and response.body and string.find(response.body, "modo_debug_activo") then
    return "VULNERABLE: endpoint expone modo debug"
  end
  return nil
end
```

`portrule` define contra qué puertos aplica el script (aquí, cualquier puerto detectado como HTTP). `action` es la lógica que se ejecuta contra cada host que cumpla la regla.

## Lanzarlo

```bash
nmap --script /ruta/a/mi_script.nse -p 80,8080,8443 192.168.1.0/24
```

No hace falta instalar el script en la ruta oficial de Nmap para probarlo — apuntar directamente a la ruta del archivo funciona igual, útil mientras estás iterando y depurando el script.

## Combinando con NSE ya existente

En vez de escribir todo desde cero, muchas veces reutilizo librerías que Nmap ya trae (`http`, `shortport`, `stdnse`, `json` para parsear respuestas). Por ejemplo, para comprobar una API que devuelve JSON:

```lua
local json = require "json"

action = function(host, port)
  local response = http.get(host, port, "/api/version")
  if response and response.body then
    local ok, parsed = json.parse(response.body)
    if ok and parsed.version and parsed.version < "2.0" then
      return "VULNERABLE: versión desactualizada detectada: " .. parsed.version
    end
  end
  return nil
end
```

## Depurar cuando algo no funciona

Lo más útil mientras escribo un script nuevo es `stdnse.debug`, que imprime información solo cuando lanzas Nmap con verbosidad de debug activada, sin ensuciar la salida normal:

```lua
stdnse.debug1("Respuesta recibida: %s", response.body)
```

```bash
nmap --script mi_script.nse -d -p 80 192.168.1.10
```

`-d` activa el modo debug, que muestra esos mensajes — sin ese flag, quedan silenciados y no interfieren con el uso normal del script.

## Cuándo merece la pena escribir uno propio

Solo cuando la comprobación es lo bastante específica y la vas a repetir contra muchos hosts — para algo puntual contra un solo objetivo, un `curl` manual es más rápido que escribir, depurar y probar un script Lua. El punto de equilibrio suele estar en si vas a lanzar la misma comprobación más de un puñado de veces; si es así, automatizarla en NSE se amortiza rápido.