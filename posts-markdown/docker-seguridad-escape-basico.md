---
title: "Docker: lo básico de seguridad que reviso antes de dar por seguro un contenedor"
description: "Configuraciones de Docker que abren la puerta a un escape de contenedor, y el caso del socket de Docker montado dentro del propio contenedor que da control total sobre el host."
slug: "docker-seguridad-escape-basico"
category: "Linux"
tags: ["docker", "contenedores", "escape de contenedor", "post-explotación"]
date: "2027-08-17"
level: "Avanzado"
---

## Por qué "está en un contenedor" no significa "está aislado"

Al principio asumía que tener acceso dentro de un contenedor era, por definición, un compromiso limitado — al fin y al cabo, un contenedor no es la máquina host completa. La realidad es que hay configuraciones bastante comunes que rompen ese aislamiento por completo, y no requieren ningún exploit de kernel sofisticado, solo saber qué buscar dentro del contenedor.

> Para entornos de laboratorio propios o pentests con autorización.

## Lo primero que reviso al tener acceso a un contenedor

```bash
cat /proc/1/cgroup
ls -la /.dockerenv
```

Confirma que efectivamente estás dentro de un contenedor y no en el host directamente — el primer paso antes de plantear cualquier vía de escape.

## El caso más directo: el socket de Docker montado dentro

Esta es la configuración que, cuando aparece, da control total sobre el host casi sin esfuerzo:

```bash
ls -la /var/run/docker.sock
```

Si ese socket existe dentro del contenedor (montado explícitamente, algo que a veces se hace por comodidad para herramientas de CI/CD dentro de contenedores, sin pensar en la implicación de seguridad), puedes usarlo para hablar directamente con el daemon de Docker del host **desde dentro del contenedor**:

```bash
docker -H unix:///var/run/docker.sock ps
```

Y si puedes listar contenedores, puedes crear uno nuevo montando el sistema de archivos raíz del host:

```bash
docker -H unix:///var/run/docker.sock run -v /:/host -it alpine chroot /host
```

Esto te da una shell con acceso completo al sistema de archivos del host, efectivamente escapando del contenedor original — no porque haya un fallo de Docker, sino porque el socket montado te da la misma autoridad que tendría cualquier proceso legítimo del host que hable con el daemon.

## Contenedores en modo privileged

```bash
cat /proc/self/status | grep CapEff
```

Si el contenedor se lanzó con `--privileged`, tiene prácticamente todas las capabilities del kernel disponibles, casi anulando el aislamiento que Docker normalmente proporciona. Con eso, montar dispositivos del host directamente suele ser posible:

```bash
fdisk -l
mkdir /mnt/host
mount /dev/sda1 /mnt/host
```

Si el disco del host es accesible y montable desde dentro del contenedor privilegiado, tienes acceso de lectura/escritura al sistema de archivos completo del host sin necesitar el socket de Docker en absoluto.

## Capabilities específicas peligrosas dentro de contenedores

Sin llegar a `--privileged` completo, ciertas capabilities individuales asignadas de forma suelta también son problemáticas — `SYS_ADMIN` es la más citada porque habilita un rango amplio de operaciones que en conjunto pueden llevar a escape, dependiendo de qué más esté disponible en el contenedor.

```bash
capsh --print
```

Revisar qué capabilities tiene el proceso actual dentro del contenedor te dice qué margen real de maniobra existe más allá de lo evidente a simple vista.

## Variables de entorno con credenciales

Esto no es específico de Docker pero aparece constantemente en contenedores mal gestionados — credenciales de base de datos, tokens de API, claves de servicios cloud pasadas como variables de entorno en vez de gestionadas con un secreto adecuado:

```bash
env | grep -i -E "password|key|token|secret"
```

Frecuentemente esas mismas credenciales dan acceso a recursos fuera del propio contenedor (una base de datos compartida, un bucket cloud), ampliando el impacto más allá del contenedor comprometido.

## Lo que reviso siempre, en orden

Confirmar que estoy en un contenedor, comprobar si el socket de Docker está accesible, revisar si el contenedor corre en modo privilegiado o con capabilities sueltas peligrosas, y por último buscar credenciales en variables de entorno. El patrón general es el mismo que en escalada de privilegios tradicional — no busco un exploit complejo primero, busco configuraciones que ya rompen el aislamiento por diseño antes de plantear nada más sofisticado.
