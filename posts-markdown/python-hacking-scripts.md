---
title: "Los scripts de Python que reescribo en cada pentest"
description: "Port scanner multihilo, verificación de subdominios y por qué mi primer intento con threading se quedó colgado sin avisar."
slug: "python-hacking-scripts"
category: "Python"
tags: ["python", "scripting", "automatización"]
date: "2026-04-02"
level: "Intermedio"
---

## Por qué tener tus propios scripts

No uso Python para reinventar Nmap — para escaneo de puertos serio, Nmap
gana siempre. Lo uso para los huecos: cosas muy específicas de un engagement
concreto que no justifican instalar una herramienta nueva, o que necesito
adaptar sobre la marcha. El port scanner de abajo no compite con Nmap, es
para cuando estoy en un entorno restringido donde solo tengo Python
disponible (pasa más de lo que parece, en máquinas Windows sin privilegios
para instalar nada).

> Estos scripts son para entornos propios o con autorización explícita. El
> de fuerza bruta HTTP en particular puede generar bloqueos de cuenta o
> alertas si lo lanzas contra algo sin permiso.

## Port scanner: la versión que NO funciona bien

Esta es la versión "obvia" con sockets, secuencial:

```python
import socket

target = "192.168.1.1"

for port in range(1, 1025):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    if s.connect_ex((target, port)) == 0:
        print(f"Puerto {port}: abierto")
    s.close()
```

Funciona, pero con 1024 puertos y 0.5s de timeout en el peor caso estás
hablando de más de 8 minutos si la mayoría de puertos están filtrados (no
cerrados — filtrados, que es cuando el timeout se agota de verdad en vez de
recibir un RST inmediato). La primera vez que lo lancé contra una red con un
firewall agresivo, tardó casi 20 minutos para un solo host. Ahí entendí por
qué hace falta paralelizar.

## La versión con threads (y el problema que no vi venir)

```python
import socket
import threading
from queue import Queue

target = "192.168.1.1"
q = Queue()
open_ports = []
lock = threading.Lock()

def worker():
    while not q.empty():
        port = q.get()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        if s.connect_ex((target, port)) == 0:
            with lock:
                open_ports.append(port)
        s.close()
        q.task_done()

for port in range(1, 1025):
    q.put(port)

threads = [threading.Thread(target=worker) for _ in range(50)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Puertos abiertos: {sorted(open_ports)}")
```

Dos cosas que no puse en la primera versión y que me costaron un rato de
debug: el `lock` al escribir en `open_ports` (sin él, en condiciones de
carrera puedes perder algún resultado, aunque con listas en CPython es
menos grave que con otras estructuras gracias al GIL) y el hecho de que con
más de unos 100-150 threads en `socket`, empiezas a comerte errores de
"too many open files" en Linux si no subes el límite de descriptores
(`ulimit -n`). Con 50 threads no llegas a ese problema, pero si subes el
número pensando "más rápido", te vas a topar con eso tarde o temprano.

## Verificación de subdominios

Para una wordlist pequeña, esto es suficiente:

```python
import socket

domain = "ejemplo.com"
wordlist = ["www", "mail", "ftp", "admin", "api", "dev", "staging", "vpn"]

for sub in wordlist:
    full_domain = f"{sub}.{domain}"
    try:
        ip = socket.gethostbyname(full_domain)
        print(f"[+] {full_domain} -> {ip}")
    except socket.gaierror:
        pass
```

El problema aparece con wordlists grandes (miles de entradas): `gethostbyname`
es bloqueante y secuencial, así que para algo de ese tamaño esto se vuelve
tan lento como para no ser práctico. Para volumen real uso `dnspython` con
resolución asíncrona, o directamente delego en herramientas hechas para
esto como `subfinder` o `amass` — no tiene sentido reescribir su lógica en
Python cuando ya existen y son más rápidas.

## Fuerza bruta HTTP básico

```python
import requests

url = "http://192.168.1.1/login"
usuarios = ["admin", "root"]

with open("passwords.txt") as f:
    passwords = [line.strip() for line in f]

session = requests.Session()

for user in usuarios:
    for pwd in passwords:
        resp = session.post(url, data={"username": user, "password": pwd})
        if resp.status_code == 302 or "Bienvenido" in resp.text:
            print(f"[+] {user}:{pwd}")
            break
```

Usar `requests.Session()` en vez de `requests.post()` suelto importa más de
lo que parece: sin sesión, cada petición es una conexión TCP nueva, lo que
en una lista de contraseñas larga añade overhead notable. Con sesión se
reutiliza la conexión. También: muchas apps reales bloquean la cuenta o
añaden un captcha después de N intentos fallidos — si el script no detecta
eso, vas a seguir probando contraseñas contra un muro durante horas sin
saberlo. Vale la pena comprobar el código de respuesta cuando empieza a
repetirse igual en cada intento; suele ser la señal de que te han bloqueado.

## Librerías que uso, según para qué

| Librería | Cuándo la uso |
|---|---|
| `socket` | Cosas de bajo nivel, cuando no quiero la sobrecarga de `requests` |
| `requests` | Cualquier cosa HTTP/HTTPS, el 90% del tiempo |
| `scapy` | Manipulación de paquetes a nivel de capa 2/3, ARP spoofing casero |
| `paramiko` | Automatizar SSH cuando necesito ejecutar algo remoto desde un script |
| `dnspython` | Resolución DNS más allá de lo que da `socket.gethostbyname` |

Si vas a ampliar alguno de estos scripts, el siguiente paso lógico suele ser
exportar resultados a JSON en vez de solo imprimirlos — en cuanto necesitas
correlacionar datos de dos scripts distintos, tener output estructurado te
ahorra parsear texto con regex después.
