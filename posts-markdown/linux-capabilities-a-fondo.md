---
title: "Capabilities de Linux: el mecanismo que va más allá de SUID"
description: "Cómo funcionan las capabilities de Linux a nivel de kernel, por qué existen como alternativa a SUID, y las que más aparecen como vector de escalada de privilegios."
slug: "linux-capabilities-a-fondo"
category: "Linux"
tags: ["capabilities", "linux", "privilege escalation", "kernel"]
date: "2027-02-10"
level: "Avanzado"
---

## Por qué existen las capabilities

Ya until until until until until until until until until until until mencioné las capabilities de pasada en mi artículo de escalada de privilegios en Linux, tratándolas casi como "un SUID más granular". Merece la pena entender por qué existen de verdad: SUID da todos los privilegios de root al proceso mientras se ejecuta, sin matices — un binario SUID mal diseñado tiene acceso total al sistema aunque solo necesitara, por ejemplo, poder abrir puertos por debajo del 1024. Las capabilities dividen los privilegios de root en piezas independientes, para que un proceso solo tenga exactamente el permiso que necesita, no todos.

## Cómo funcionan a nivel de kernel

Linux divide lo que tradicionalmente era "ser root o no serlo" en más de 40 capabilities independientes. Algunas de las más relevantes desde el punto de vista de seguridad:

```text
CAP_SETUID       → cambiar el UID de un proceso a cualquier otro
CAP_SETGID       → cambiar el GID de un proceso
CAP_NET_BIND_SERVICE → abrir puertos por debajo de 1024 sin ser root
CAP_SYS_ADMIN    → una especie de "cajón de sastre" con permisos muy amplios,
                    la más peligrosa si aparece mal asignada
CAP_DAC_READ_SEARCH → saltarse comprobaciones de permisos de lectura de archivos
```

## Ver qué capabilities tiene un binario

```bash
getcap -r / 2>/dev/null
```

La salida muestra binarios con capabilities asignadas y cuáles exactamente:

```text
/usr/bin/python3.9 = cap_setuid+ep
```

El `+ep` indica que la capability está tanto en el conjunto "permitido" como "efectivo" — en la práctica, que está activa y disponible para el proceso cuando se ejecuta.

## Por qué CAP_SETUID es tan directa de explotar

Si un binario tiene `cap_setuid`, puede cambiar su propio UID a 0 (root) sin necesitar ningún otro privilegio adicional:

```bash
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

Si ese Python tiene la capability asignada, este comando te da una shell como root directamente — el mismo principio que un SUID en `/usr/bin/python3`, pero mediante el mecanismo de capabilities en vez de los bits SUID clásicos.

## Por qué esto se pasa por alto más que SUID

La mayoría de guías y checklists de escalada de privilegios se centran en `find / -perm -4000` como comando estándar, y muchos administradores de sistemas revisan y auditan binarios SUID de forma rutinaria — pero no siempre auditan capabilities con la misma disciplina, porque el mecanismo es más nuevo y menos conocido en la práctica de hardening tradicional. En sistemas donde han quitado SUID de binarios obvios como parte de un endurecimiento consciente, es habitual que las capabilities queden sin revisar de la misma forma.

## Asignar capabilities (para entender el otro lado)

Como referencia de cómo se configuran legítimamente (útil para reconocer configuraciones intencionadas frente a errores):

```bash
sudo setcap cap_net_bind_service=+ep /usr/bin/mi_servidor
```

Esto permite que `mi_servidor` abra un puerto por debajo de 1024 sin necesitar ejecutarse completo como root — el caso de uso legítimo real de las capabilities, y por qué existen: dar el permiso mínimo necesario, no todo o nada.

## Diferencia práctica con SUID en el análisis

SUID afecta al binario completo mientras se ejecuta — todos los privilegios de root, sin excepción. Las capabilities son granulares: un binario puede tener `cap_net_bind_service` sin tener `cap_setuid`, y en ese caso no es vector de escalada de privilegios directa aunque tenga "algo" de privilegio elevado. No basta con ver que un binario tiene *alguna* capability asignada — hay que identificar cuál exactamente, porque no todas son explotables de la misma forma. `cap_setuid` y `cap_dac_read_search` son las que más frecuentemente llevan a compromiso total; muchas otras son mucho más limitadas en lo que permiten hacer.