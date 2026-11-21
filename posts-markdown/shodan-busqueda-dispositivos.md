---
title: "Shodan: cómo lo uso más allá de buscar cámaras expuestas"
description: "Filtros de búsqueda en Shodan que uso de verdad para reconocimiento de infraestructura, y por qué complementa (no sustituye) a Google Dorking y theHarvester."
slug: "shodan-busqueda-dispositivos"
category: "OSINT"
tags: ["shodan", "OSINT", "reconocimiento"]
date: "2026-12-23"
level: "Principiante"
---

## Por qué esto no es "el buscador de cámaras hackeables"

La fama de Shodan viene de vídeos mostrando cámaras de seguridad sin contraseña, y eso hace que mucha gente lo trate como una curiosidad más que como herramienta de reconocimiento seria. En la práctica, lo uso para algo mucho más aburrido y útil: mapear qué servicios expone una organización a internet, sin tocar nada, antes de plantear cualquier otra fase de un reconocimiento.

> Buscar información ya indexada por Shodan no es ilegal. Conectarte o interactuar con los servicios que encuentras, sin autorización, sí lo es.

## Filtros básicos que más uso

```text
org:"Nombre Empresa"
  Todo lo que Shodan tiene indexado bajo esa organización según el registro
  del rango de IPs (WHOIS). Punto de partida casi siempre.

hostname:objetivo.com
  Dispositivos asociados a ese dominio concreto.

port:22
  Filtrar por puerto específico, útil combinado con org: para ver
  qué servicios SSH expuestos tiene una organización.

country:ES
  Acotar geográficamente, útil cuando org: da demasiado ruido de
  filiales internacionales que no son tu alcance.
```

## Combinando filtros para algo útil

```text
org:"Nombre Empresa" port:3389
```

Esto te da directamente qué IPs de esa organización tienen RDP expuesto a internet — información que, si aparece, ya es un hallazgo relevante por sí solo (RDP expuesto sin VPN de por medio suele ser mala práctica, independientemente de si hay una vulnerabilidad específica).

```text
org:"Nombre Empresa" product:"nginx"
```

Filtrar por producto y versión detectada te permite cruzar rápidamente con CVEs conocidos, siguiendo el mismo proceso que until describí en mi artículo sobre cómo leer un CVE — primero confirmas qué versión real está expuesta, después buscas si le afecta algo.

## Buscar paneles de administración expuestos

```text
org:"Nombre Empresa" http.title:"login"
```

`http.title` busca en el título de la página HTTP indexada — útil para encontrar paneles de acceso que quedaron expuestos sin que aparezcan enlazados desde ningún sitio público (a diferencia de Google Dorking, que depende de que Google haya rastreado el enlace).

## La diferencia real con Google Dorking

Google indexa contenido de páginas web rastreadas por su crawler. Shodan indexa **servicios y banners** de dispositivos que escanea directamente en internet, independientemente de si tienen una página web asociada o son rastreables. Un servidor SSH, una base de datos mal configurada, una cámara IP — nada de eso lo vas a encontrar con `site:` en Google, porque Google no indexa protocolos que no sean HTTP/HTTPS. Shodan sí.

## Dónde encaja en mi flujo de OSINT

Google Dorking primero para lo indexado en web pública. Shodan después para servicios expuestos que no dependen de tener página web. theHarvester en paralelo para emails y subdominios. Los tres dan piezas distintas del mismo mapa — ninguno sustituye a los otros dos, cada uno ve una capa distinta de lo que una organización tiene expuesto.

## La limitación de la cuenta gratuita

Sin cuenta de pago, los resultados de búsqueda están limitados y algunos filtros avanzados no están disponibles. Para reconocimiento puntual la cuenta gratuita basta; si necesitas monitorización continua o volumen de resultados grande, ahí sí se nota la diferencia con la versión de pago — similar a la limitación de 12 resultados por transform que ya until mencioné con Maltego Community.