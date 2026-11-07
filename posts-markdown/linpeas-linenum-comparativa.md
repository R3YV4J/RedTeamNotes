---
title: "LinPEAS, LinEnum y linux-exploit-suggester: cuál lanzo primero"
description: "Diferencias reales entre las tres herramientas de enumeración de privilegios en Linux más usadas, y el orden en el que las combino según lo que ya vi con mi propio script."
slug: "linpeas-linenum-comparativa"
category: "Herramientas"
tags: ["linpeas", "linenum", "linux-exploit-suggester", "post-explotación"]
date: "2026-10-21"
level: "Intermedio"
---

## Por qué no lanzo las tres a la vez

Las tres hacen cosas parecidas — buscar vectores de escalada de privilegios en Linux — pero no son intercambiables ni redundantes del todo. Lanzarlas las tres de golpe en cada máquina es perder tiempo revisando salidas duplicadas. Ya escribí sobre mi propio script de enumeración básica, que uso primero; estas tres entran después, cuando ese script no encontró nada evidente.

## LinPEAS: la más completa, y la más ruidosa

```bash
./linpeas.sh -a
```

Es la que más cosas revisa — desde SUID y capabilities hasta contenedores, procesos, credenciales en archivos de configuración. El problema es justo eso: tanto volumen de salida (con colores para marcar "posiblemente interesante") que en máquinas con mucho software instalado, hay que dedicar tiempo real a leerla con calma, no solo buscar el rojo brillante.

```bash
# Guardar la salida sin colores para revisar después, o para grep
./linpeas.sh -a | tee linpeas_output.txt
```

## LinEnum: más simple, más rápida de leer

```bash
./LinEnum.sh -t
```

`-t` (thorough) activa comprobaciones adicionales. LinEnum es más antigua y menos mantenida que LinPEAS, pero justo por eso su salida es más corta y más fácil de leer de un vistazo — la uso cuando quiero una vista rápida sin el volumen de LinPEAS, sobre todo en máquinas donde ya sospecho por dónde va el vector y solo quiero confirmar.

## linux-exploit-suggester: específico para kernel exploits

A diferencia de las dos anteriores, esta no busca configuraciones mal hechas — busca específicamente si la versión de kernel tiene exploits públicos conocidos:

```bash
./linux-exploit-suggester.sh
```

La uso al final, no al principio — kernel exploits son el último recurso porque pueden colgar el sistema, así que no tiene sentido revisarlos antes de descartar vectores más seguros como SUID mal configurado o cron jobs con ruta relativa.

## El orden que sigo en la práctica

Mi script básico primero (segundos, cubre lo más común). Si no da nada evidente, LinPEAS con calma, leyendo la salida completa en vez de solo lo marcado en rojo. Si LinPEAS tampoco da nada claro, linux-exploit-suggester como último recurso antes de plantearme kernel exploits.

LinEnum la reservo para cuando ya tengo sospecha de por dónde va el vector y solo quiero una confirmación rápida sin el volumen de LinPEAS delante.

## Un matiz importante con las tres

Ninguna de las tres "encuentra" el vector por ti — te dan una lista de cosas potencialmente interesantes. La misma matización que hice con GTFOBins: encontrar el SUID o el kernel desactualizado es la parte fácil, confirmar que es explotable de verdad en ese contexto concreto sigue siendo trabajo manual.