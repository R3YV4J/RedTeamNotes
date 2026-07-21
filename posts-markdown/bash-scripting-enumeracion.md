---
title: "Bash para enumeración: el script que reutilizo en cada máquina"
description: "El script bash que monto al ganar acceso a una máquina para enumerar lo básico, y por qué dejé de usar uno descargado de internet sin entenderlo."
slug: "bash-scripting-enumeracion"
category: "Linux"
tags: ["bash", "scripting", "enumeración", "post-explotación"]
date: "2026-04-22"
level: "Intermedio"
---

## Por qué dejé de copiar scripts de enumeración de internet

Durante un tiempo usé scripts de enumeración descargados directamente de
GitHub sin leerlos antes — total, "son de confianza, los usa todo el
mundo". Hasta que uno de esos scripts tardó casi cinco minutos en una
máquina con muchos archivos, y no tenía ni idea de qué estaba comprobando
durante ese tiempo ni si se había colgado. Desde entonces escribo mi propio
script de enumeración inicial, más corto, que entiendo línea por línea, y
que sé exactamente qué hace y cuánto debería tardar.

> Para máquinas de laboratorio o con autorización. Igual que cualquier otro
> artículo de esta categoría.

## El script base que uso

```bash
#!/bin/bash
# enum_basico.sh — enumeración inicial al ganar acceso

echo "=== Usuario y permisos ==="
whoami
id
sudo -l 2>/dev/null

echo -e "\n=== Sistema ==="
uname -a
cat /etc/os-release 2>/dev/null | head -2

echo -e "\n=== SUID ==="
find / -perm -4000 -type f 2>/dev/null

echo -e "\n=== Capabilities ==="
getcap -r / 2>/dev/null

echo -e "\n=== Cron jobs ==="
cat /etc/crontab 2>/dev/null
ls -la /etc/cron.d/ 2>/dev/null

echo -e "\n=== Procesos como root ==="
ps aux | grep "^root"

echo -e "\n=== Archivos con escritura para 'otros' en rutas interesantes ==="
find /opt /etc /var -writable -type f 2>/dev/null

echo -e "\n=== Conexiones de red activas ==="
ss -tulnp 2>/dev/null || netstat -tulnp 2>/dev/null
```

Tarda segundos, no minutos, porque no intenta ser exhaustivo — cubre lo que
en mi experiencia da resultado el 80% de las veces. Si esto no encuentra
nada, ahí sí lanzo algo más completo como LinPEAS.

## El error de `2>/dev/null` puesto sin pensar

Al principio metía `2>/dev/null` en todo por costumbre, copiado de otros
scripts. El problema: en una máquina donde `find /` falla por permisos en
muchos directorios, silenciar todos los errores también esconde mensajes
que sí importaban (por ejemplo, si `getcap` no está instalado, el error te
lo dice; con todo silenciado, simplemente no ves nada y asumes que no hay
resultados, cuando en realidad el comando ni se ejecutó).

Ahora soy más selectivo: silencio el ruido esperado (permisos denegados en
`find /`) pero dejo visibles los errores de "comando no encontrado", que sí
necesito ver.

```bash
# Mejor: silenciar solo "Permission denied", no todo
find / -perm -4000 -type f 2>&1 | grep -v "Permission denied"
```

## Un script más específico: buscar credenciales en archivos de config

Este lo añadí después de encontrar una contraseña de base de datos en texto
plano en un `.env` olvidado:

```bash
#!/bin/bash
# buscar_creds.sh

echo "=== Buscando patrones de credenciales en configs comunes ==="
grep -ril "password\|passwd\|secret\|api_key" \
  /var/www /opt /etc 2>/dev/null \
  --include="*.env" --include="*.conf" --include="*.config" --include="*.yml" \
  --include="*.yaml" --include="*.json" 2>/dev/null

echo -e "\n=== Archivos .bash_history con contenido ==="
find / -name ".bash_history" -size +0c 2>/dev/null
```

`.bash_history` con contenido es sorprendentemente frecuente como vector —
mucha gente ejecuta comandos con contraseñas en línea de comandos
(`mysql -u root -pMiContraseña`) sin pensar que quedan registrados.

## Por qué no automatizo esto con un framework más grande

Podría empaquetar esto como una herramienta más sofisticada con flags y
opciones, pero deliberadamente lo mantengo como scripts sueltos y simples.
La razón: cuando estoy en una máquina con shell limitada (sin bash
completo, por ejemplo, solo `sh`), necesito poder copiar y pegar fragmentos
pequeños que sé que van a funcionar, no depender de un script grande que
puede fallar por una dependencia que no está disponible en ese entorno
concreto.

## Cuándo paso a herramientas más completas

Si la enumeración básica no da nada obvio, ahí sí lanzo LinPEAS o
linux-exploit-suggester — son más lentos pero mucho más exhaustivos. La
lógica es la misma que con theHarvester antes de Maltego: empieza por lo
rápido y específico, escala a lo pesado solo si hace falta.
