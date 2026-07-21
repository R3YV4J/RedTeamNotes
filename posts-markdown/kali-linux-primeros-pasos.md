---
title: "Kali Linux: lo primero que configuro después de instalarlo"
description: "Qué hago nada más instalar Kali Linux antes de empezar a practicar: actualizaciones, herramientas que faltan, y errores típicos al principio."
slug: "kali-linux-primeros-pasos"
category: "Linux"
tags: ["kali linux", "linux", "configuración"]
date: "2026-02-19"
level: "Principiante"
---

## Por qué Kali recién instalado no está listo para usarse

Kali Linux tiene fama de ser la distro de hacking por excelencia, pero la
instalación base está pensada para ser liviana — no viene con todo
configurado y listo. La primera vez que lo instalé esperaba poder lanzar
herramientas directamente y me encontré con que faltaban paquetes, el
repositorio no estaba actualizado, y la configuración por defecto tiene
cosas que conviene cambiar antes de empezar.

## Lo primero: actualizar antes de cualquier otra cosa

```bash
sudo apt update && sudo apt upgrade -y
```

Sin esto, muchas herramientas están en versiones antiguas y algunas
dependencias no coinciden. Tarda un rato, pero es el paso que más se
salta la gente y más problemas da después.

## Herramientas que instalo siempre al principio

Las que vienen preinstaladas cubren mucho, pero hay algunas que uso tanto
que las añado en cualquier instalación nueva:

```bash
# Para gestión de conexiones y túneles
sudo apt install -y netcat-traditional openssh-server

# Para capturas de paquetes sin necesitar root siempre
sudo apt install -y wireshark
sudo usermod -aG wireshark $USER

# Utilidades de texto que siempre necesito
sudo apt install -y jq curl wget git vim

# Para entornos de Python aislados (útil para herramientas con dependencias raras)
sudo apt install -y python3-venv python3-pip
```

El grupo `wireshark` es el que más se olvida — sin él, cada vez que quieres
capturar tienes que arrancar Wireshark como root, lo cual es mala práctica
y también un poco molesto.

## Configurar el teclado en español

Si instalas con teclado en inglés y luego lo usas en español, el layout
causa muchos errores raros al escribir comandos. Mejor cambiarlo desde el
principio:

```bash
sudo dpkg-reconfigure keyboard-configuration
# Selecciona: Generic 105-key PC → Spanish → Spanish
```

Y para el entorno gráfico (si usas Kali con escritorio):

```bash
setxkbmap es
```

## El problema más común al empezar: ejecutar todo como root

Kali en versiones antiguas usaba root por defecto, lo que ha hecho que mucha
gente tenga el hábito de trabajar siempre como root. En las versiones
modernas ya crea un usuario normal durante la instalación, que es la forma
correcta. El error que veo más seguido: lanzar herramientas con `sudo`
cuando no hace falta, o lanzar el escritorio entero como root porque
"así funciona todo sin problemas". Funciona, pero pierdes el aislamiento
que te protege si algo sale mal.

## Snapshot antes de instalar cosas raras

Si usas Kali en VirtualBox o VMware (que es lo recomendable para empezar),
haz un snapshot limpio después de la configuración inicial y antes de
instalar cualquier herramienta nueva de fuentes no oficiales. Restaurar
un snapshot es mucho más rápido que reinstalar desde cero cuando algo
rompe el sistema, y pasa.

## Una cosa que no esperaba al empezar con Kali

Que el 90% del tiempo lo pasas en la terminal, no en interfaces gráficas.
Invertir una semana en aprender bash básico (navegación, pipes, redirección,
variables) antes de intentar usar herramientas de seguridad hace que todo lo
demás sea mucho más fácil. Sin esa base, cada comando de Nmap o Metasploit
es un misterio parcial.
