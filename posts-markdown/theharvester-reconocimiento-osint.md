---
title: "theHarvester: el primer comando que lanzo en cualquier reconocimiento"
description: "Cómo uso theHarvester para enumeración rápida de emails y subdominios antes de pasar a herramientas más pesadas como Maltego."
slug: "theharvester-reconocimiento-osint"
category: "OSINT"
tags: ["theHarvester", "OSINT", "reconocimiento"]
date: "2026-02-05"
level: "Principiante"
---

## Por qué esto antes que Maltego

theHarvester no tiene la interfaz gráfica vistosa de Maltego, pero por eso
mismo es lo primero que lanzo en cualquier reconocimiento: un solo comando,
sin montar nada, y en menos de un minuto tengo una vista general de qué hay
público sobre un dominio. Si lo que sale ahí justifica profundizar, paso a
herramientas más pesadas. Si no, ya he ahorrado el tiempo de montar un
grafo para nada.

> El uso de OSINT debe respetar la normativa de protección de datos
> aplicable. Esto es para reconocimiento autorizado, no para otra cosa.

## Instalación

En Kali viene preinstalado. Si no:

```bash
sudo apt update && sudo apt install theharvester -y
```

Si lo instalas desde el repositorio de GitHub directamente (recomendable si
quieres la versión más reciente, porque algunas fuentes cambian su API con
frecuencia y el paquete de apt se queda atrás):

```bash
git clone https://github.com/laramies/theHarvester.git
cd theHarvester
pip install -r requirements/base.txt
```

## El comando básico

```bash
theHarvester -d empresa.com -b all
```

`-b all` lanza la búsqueda contra todas las fuentes disponibles. La primera
vez que lo usé así, esperaba que tardara segundos y tardó varios minutos —
algunas fuentes (sobre todo las que dependen de APIs externas con rate
limiting) son notablemente más lentas que otras. Para resultados rápidos,
prefiero apuntar a fuentes específicas:

```bash
theHarvester -d empresa.com -b duckduckgo,crtsh,hackertarget
```

## Las fuentes que de verdad dan resultado

No todas las fuentes (`-b`) dan el mismo nivel de señal. Las que más uso:

| Fuente | Qué aporta |
|---|---|
| `crtsh` | Subdominios desde certificados SSL públicos — muy fiable, sin rate limit agresivo |
| `hackertarget` | Subdominios y reconocimiento básico de DNS |
| `duckduckgo` | Emails y nombres indexados, sin necesitar API key |
| `bing` | Similar a duckduckgo, complementa resultados |

Las fuentes que requieren API key (Shodan, Hunter.io, etc.) dan mejores
resultados pero necesitas configurar la clave en
`theHarvester/api-keys.yaml` antes. Sin esa clave, simplemente se omiten en
silencio — si esperas resultados de una fuente y no aparece nada, comprueba
si necesitaba API key configurada.

## Caso real: de subdominios a superficie de ataque

Un flujo que repito bastante:

```bash
# 1. Subdominios vía certificados (rápido y fiable)
theHarvester -d empresa.com -b crtsh

# 2. Verificar cuáles responden de verdad (theHarvester lista,
#    pero no siempre confirma que el host esté vivo)
cat subdominios.txt | httpx -silent

# 3. De los que responden, capturar tecnología/headers
httpx -silent -title -tech-detect -l vivos.txt
```

theHarvester por sí solo te da la lista. El paso de verificar con `httpx`
es el que de verdad te dice qué de esa lista importa — muchos subdominios
que aparecen en certificados llevan años sin servicio activo detrás.

## Exportar resultados

```bash
theHarvester -d empresa.com -b all -f resultado
# Genera resultado.json y resultado.html
```

El HTML es útil para una revisión visual rápida; para procesar los datos
con otro script, el JSON es el formato que realmente uso.

## La limitación que hay que tener clara

theHarvester agrega lo que las fuentes externas ya indexan — no descubre
nada por fuerza bruta ni hace nada activo contra el objetivo. Si una fuente
no tiene indexado un subdominio (porque es nuevo, porque no tiene
certificado público, etc.), theHarvester no lo va a encontrar. Para eso
hace falta combinar con herramientas de fuerza bruta de subdominios como
`gobuster dns` o `ffuf` en modo DNS, que sí prueban activamente contra
wordlists.

## Conclusión práctica

theHarvester es el primer paso, no el único. Le doy uso real combinándolo
con `httpx` para validar lo que encuentra, y reservo Maltego (o herramientas
similares) para cuando necesito visualizar relaciones entre múltiples tipos
de entidad, no solo listar subdominios y emails.
