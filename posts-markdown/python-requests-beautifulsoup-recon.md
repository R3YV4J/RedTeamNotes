---
title: "Requests y BeautifulSoup para reconocimiento web automatizado"
description: "Cómo combino requests y BeautifulSoup para extraer enlaces, formularios y comentarios ocultos de una página, cuando necesito algo más flexible que un escáner ya hecho."
slug: "python-requests-beautifulsoup-recon"
category: "Python"
tags: ["python", "requests", "beautifulsoup", "reconocimiento web"]
date: "2027-01-13"
level: "Intermedio"
---

## Por qué escribo esto en vez de usar solo herramientas ya hechas

Ya cubrí mis scripts de Python para port scanning y verificación de subdominios. Este es el complemento del lado web: cuando necesito extraer algo muy específico de una página (todos los enlaces internos, todos los formularios con sus campos, comentarios HTML que a veces dejan información olvidada), escribir 15 líneas con `requests` + `BeautifulSoup` es más rápido que configurar una herramienta genérica para un caso puntual.

> Para aplicaciones propias o con autorización explícita.

## Lo básico: traer y parsear una página

```python
import requests
from bs4 import BeautifulSoup

url = "http://objetivo.com"
response = requests.get(url, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")
```

`timeout=10` no es opcional en la práctica — sin él, una petición contra un servidor lento o caído puede colgar el script indefinidamente en vez de fallar de forma controlada.

## Extraer todos los enlaces internos

```python
from urllib.parse import urljoin, urlparse

base_domain = urlparse(url).netloc
enlaces_internos = set()

for link in soup.find_all("a", href=True):
    full_url = urljoin(url, link["href"])
    if urlparse(full_url).netloc == base_domain:
        enlaces_internos.add(full_url)

for enlace in sorted(enlaces_internos):
    print(enlace)
```

`urljoin` resuelve enlaces relativos (`/pagina`, `../otra`) contra la URL base, y el filtro por `netloc` descarta enlaces que salen del dominio — lo que me interesa es mapear la superficie propia del sitio, no los enlaces externos que apuntan a redes sociales o terceros.

## Encontrar formularios y sus campos

```python
for form in soup.find_all("form"):
    print(f"Action: {form.get('action')}")
    print(f"Method: {form.get('method', 'GET').upper()}")
    for input_field in form.find_all("input"):
        print(f"  Campo: {input_field.get('name')} - Tipo: {input_field.get('type')}")
```

Antes de tocar Burp para probar algo manualmente, esto me da un mapa rápido de qué formularios existen y qué campos esperan, sin tener que navegar la página a mano buscándolos uno por uno.

## Buscar comentarios HTML olvidados

Sorprendentemente frecuente encontrar comentarios de desarrollo que quedaron en producción por descuido — rutas de debug, credenciales de prueba, notas internas:

```python
from bs4 import Comment

comentarios = soup.find_all(string=lambda text: isinstance(text, Comment))
for c in comentarios:
    if c.strip():
        print(c.strip())
```

## Recorrer varias páginas del sitio (con límites)

Para no convertir esto en un crawler descontrolado, limito explícitamente cuántas páginas visita y evito repetir URLs ya vistas:

```python
visitadas = set()
por_visitar = [url]
limite = 50

while por_visitar and len(visitadas) < limite:
    actual = por_visitar.pop(0)
    if actual in visitadas:
        continue
    visitadas.add(actual)

    try:
        r = requests.get(actual, timeout=10)
        s = BeautifulSoup(r.text, "html.parser")
        for link in s.find_all("a", href=True):
            full = urljoin(actual, link["href"])
            if urlparse(full).netloc == base_domain and full not in visitadas:
                por_visitar.append(full)
    except requests.RequestException:
        continue

print(f"Total de páginas mapeadas: {len(visitadas)}")
```

El `try/except` alrededor de la petición es necesario — en un recorrido de decenas de páginas, es cuestión de tiempo que alguna URL falle (timeout, redirección rota, 500) y sin ese control el script entero se cae por un solo enlace problemático.

## Cuándo esto no sustituye a herramientas dedicadas

Para descubrimiento de rutas no enlazadas (lo que hace gobuster o ffuf con fuerza bruta contra una wordlist), este enfoque no sirve — solo encuentra lo que ya está enlazado desde algún sitio que visitaste. Es un complemento al fuzzing, no un sustituto: uno encuentra lo oculto por fuerza bruta, el otro mapea la estructura visible con más detalle del que un escáner genérico suele mostrar por defecto.