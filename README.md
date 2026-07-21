# RedTeamNotes

Blog estático de pentesting y seguridad ofensiva, escrito por R3yv4j.
Optimizado para SEO, preparado para Google AdSense, con publicación de
artículos automatizada vía Markdown. 100% GitHub Pages, sin backend, sin
coste de hosting.

---

## Configuración central: `config/site.json`

Todo el branding (nombre del sitio, autor, enlaces sociales, dominio) vive
en un único archivo:

```json
{
  "site_name": "RedTeamNotes",
  "domain": "https://redteamnotes.github.io",
  "author": {
    "name": "R3yv4j",
    "bio": "...",
    "github": "https://github.com/r3yv4j",
    "linkedin": "https://linkedin.com/in/r3yv4j",
    "portfolio": "https://r3yv4j.dev",
    "email": "r3yv4j@gmail.com"
  }
}
```

**`scripts/build.py` lee este archivo en cada ejecución** y propaga esos
valores a todos los artículos generados (meta tags, schema.org, caja de
autor con enlaces). Si cambias de nombre, de autor o de dominio, edita
`config/site.json` y vuelve a correr el build — no hay nada de branding
hardcodeado dentro de `scripts/build.py` ni de `templates/article.html`.

Las páginas estáticas (`index.html`, `pages/*.html`, `categories/*.html`)
no se regeneran automáticamente a partir de este archivo — si cambias de
nombre o dominio otra vez, esas páginas necesitan una actualización manual
(son pocas y el cambio es mecánico, buscar y reemplazar).

---

## Estructura del proyecto

```
redteamnotes/
├── index.html                     # Página principal
├── 404.html                       # Página de error
├── robots.txt
├── sitemap.xml                    # Generado por build.py
├── feed.xml                       # RSS generado por build.py
│
├── config/
│   └── site.json                  # Branding, autor, enlaces — fuente única de verdad
│
├── posts-markdown/                # ARTÍCULOS FUENTE (edita aquí)
│   ├── _template.md               # Plantilla + guía de tono editorial
│   ├── guia-nmap-completa.md
│   ├── osint-maltego-tutorial.md
│   ├── python-hacking-scripts.md
│   ├── oscp-guia-preparacion.md
│   ├── wireshark-analisis-trafico.md
│   ├── linux-privilege-escalation.md
│   ├── como-analizar-cve-metodologia.md
│   └── burp-suite-guia-esencial.md
│
├── posts/                         # HTML generado (NO editar a mano)
│
├── templates-static/               # FUENTE de las páginas estáticas
│   ├── index.html                  # (con placeholders {{SITE_NAME}}, etc.)
│   ├── 404.html
│   ├── categories/                 # 8 páginas de categoría (fuente)
│   └── pages/
│       ├── blog.html
│       ├── sobre-mi.html
│       ├── privacidad.html
│       ├── cookies.html
│       └── aviso-legal.html
│
├── categories/                    # ⚙️ GENERADO — no editar a mano
├── pages/                         # ⚙️ GENERADO — no editar a mano
├── index.html                     # ⚙️ GENERADO — no editar a mano
├── 404.html                       # ⚙️ GENERADO — no editar a mano
│
├── templates/
│   └── article.html                # Plantilla HTML usada por build.py
│
├── scripts/
│   └── build.py                    # Generación de artículos + sitemap + RSS
│
├── assets/
│   ├── css/main.css
│   ├── js/main.js
│   ├── js/posts-index.js           # Índice de artículos, autogenerado
│   └── images/favicon.svg
│
└── .github/workflows/deploy.yml    # CI/CD: build + deploy automático
```

> ⚠️ **Regla importante:** `index.html`, `404.html`, `categories/*.html` y
> `pages/*.html` se SOBRESCRIBEN en cada `python3 scripts/build.py`. Si
> necesitas cambiar el texto de esas páginas, edita la fuente
> correspondiente en `templates-static/`, nunca el archivo final
> directamente — cualquier edición manual ahí se pierde en el siguiente
> build. Esto es lo que permite que un cambio en `config/site.json` (tu
> nombre, GitHub, LinkedIn...) se propague a todo el sitio de una vez,
> las veces que haga falta.

---

## Despliegue en GitHub Pages

### 1. Rellena `config/site.json` con tus datos reales

Antes de nada. Nombre, dominio, GitHub, LinkedIn, portfolio, email. Esto
alimenta todo lo demás.

### 2. Crea el repositorio

```bash
git init
git add .
git commit -m "Primera versión"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

> Si quieres el dominio `usuario.github.io` directamente, el repo debe
> llamarse exactamente `TU_USUARIO.github.io`. Con otro nombre, el sitio
> queda en `usuario.github.io/nombre-repo/` y las rutas absolutas
> (`/assets/...`, `/categories/...`) necesitan ese prefijo.

### 3. Activa GitHub Pages

Settings → Pages → Build and deployment → Source: **GitHub Actions**.
El workflow en `.github/workflows/deploy.yml` hace el resto en cada push.

### 4. Rellena config/site.json y genera el sitio

`config/site.json` alimenta tanto los artículos como las páginas estáticas
(home, categorías, legales). Rellena tus datos reales ahí y ejecuta el
build — esto regenera `index.html`, `404.html`, `categories/*.html` y
`pages/*.html` con tus datos ya aplicados en todo el sitio de una vez:

```bash
pip install markdown pyyaml
python3 scripts/build.py
```

---

## Flujo de publicación de artículos

**No se edita HTML a mano.** Todo artículo nace en Markdown.

### Línea editorial

`posts-markdown/_template.md` no es solo una plantilla de campos — incluye
una guía de estilo: empezar por un problema concreto en vez de una
definición de diccionario, usar comandos reales, incluir al menos un error
o limitación real, no cerrar con una "conclusión" genérica de resumen. Es
la diferencia entre una nota técnica que suena a experiencia real y un
artículo de relleno tipo folleto — conviene mantenerla en cualquier
artículo nuevo, venga de donde venga el primer borrador.

### Paso a paso

**1. Crea el archivo** en `posts-markdown/mi-articulo.md` con frontmatter:

```yaml
---
title: "Título directo, sin gancho de marketing"
description: "Qué vas a encontrar, en una frase"
slug: "mi-articulo"
category: "Pentesting"
tags: ["tag1", "tag2"]
date: "2024-XX-XX"
level: "Intermedio"
# author: opcional — si se omite, usa el autor de config/site.json
---
```

**2. Ejecuta el build** (opcional, para previsualizar):

```bash
pip install markdown pyyaml
python3 scripts/build.py
```

Esto genera `posts/mi-articulo.html` con SEO, schema.org, TOC, breadcrumbs,
caja de autor con tus enlaces — y actualiza `sitemap.xml`, `feed.xml` y
`assets/js/posts-index.js`.

**3. Publica:**

```bash
git add .
git commit -m "Nuevo artículo: mi articulo"
git push
```

El workflow de GitHub Actions ya corre `build.py` en cada push, así que en
la práctica puedes subir directamente el `.md` sin correr el build local —
GitHub genera el HTML, el sitemap y el feed, y hace commit + deploy solo.

### Campos del frontmatter

| Campo | Obligatorio | Descripción |
|---|---|---|
| `title` | sí | Directo, sin gancho de marketing |
| `description` | sí | Qué vas a encontrar, en una frase |
| `slug` | sí | URL amigable, minúsculas y guiones |
| `category` | sí | Una de las 8 categorías predefinidas |
| `date` | sí | Formato `YYYY-MM-DD` |
| `tags` | no | Para el buscador y la tag cloud |
| `level` | no | Principiante / Intermedio / Avanzado |
| `author` | no | Si se omite, usa el autor de `config/site.json` |

---

## Activar Google AdSense

Los espacios publicitarios están preparados pero ocultos (`display:none`)
para no afectar Core Web Vitals mientras no hay tráfico.

### 1. Solicita la cuenta
[google.com/adsense](https://www.google.com/adsense). Necesitarás
contenido suficiente y tráfico mínimo para que te aprueben.

### 2. Añade el script en el `<head>`
En `index.html` y `templates/article.html`, descomenta:

```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
```

### 3. Activa los slots
Busca las clases `.ad-slot` (6 ubicaciones: home, sidebar, dentro de
artículos) y reemplaza:

```html
<!-- Antes -->
<div class="ad-slot ad-slot-leaderboard" style="display:none"></div>

<!-- Después -->
<div class="ad-slot ad-slot-leaderboard">
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
       data-ad-slot="1234567890"
       data-ad-format="auto"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
```

---

## Sobre el contacto

No hay página ni formulario de contacto en el sitio — se decidió no incluir
una vía de contacto directa desde la web. Si en algún momento quieres
añadir una, las opciones más simples sin backend propio son
[Formspree](https://formspree.io) (formulario que envía a tu email) o
simplemente enlazar tu perfil de GitHub/LinkedIn para que la gente
contacte por ahí, que es lo que se usa actualmente.

### Sobre el newsletter

De momento no hay newsletter en el sitio — se quitó porque sin un proveedor
real conectado (Mailchimp, Buttondown, ConvertKit...) el formulario solo
simulaba el envío sin guardar nada. Tiene sentido añadirlo cuando haya
tráfico real que lo justifique. Si llegas a ese punto:

1. Crea una cuenta en un proveedor (Buttondown es el más simple para blogs).
2. Añade un formulario nuevo en la home apuntando a la URL que te dé el
   proveedor (sustituyendo el `action="#"` por la suya).
3. Actualiza `pages/privacidad.html` para mencionar el proveedor elegido —
   la política de privacidad solo debe describir lo que el sitio realmente
   hace.

---

## SEO implementado

- `sitemap.xml` y `feed.xml` autogenerados en cada build
- `robots.txt` apuntando al sitemap
- Open Graph y Twitter Cards en todas las páginas
- Schema.org: `Article`, `BlogPosting`, `BreadcrumbList`, `WebSite`, `Person`
- URLs amigables, canonical en todas las páginas
- TOC autogenerada desde H2/H3, breadcrumbs visibles + schema
- Escaping HTML/JSON-LD robusto: comillas, `&`, `<`, `>` en títulos no
  rompen el `<head>` ni el schema.org

### Después de desplegar
1. Verifica en [Google Search Console](https://search.google.com/search-console) y envía el sitemap.
2. Genera imágenes Open Graph reales (1200x630px) en `assets/images/og-{slug}.png`.

---

## Stack técnico

HTML5 + CSS3 + JavaScript vanilla. Python 3 (`markdown` + `pyyaml`) para el
build. GitHub Pages + GitHub Actions para hosting y CI/CD. JetBrains Mono +
Inter como tipografías.

Coste de infraestructura: 0€/mes.

---

## Checklist antes de publicar

- [ ] `config/site.json` con tus datos reales (no los de ejemplo de este repo)
- [ ] Tras rellenar config/site.json, ejecutado `python3 scripts/build.py`
- [ ] Datos reales en `pages/privacidad.html` y `pages/aviso-legal.html`
- [ ] Imágenes Open Graph para cada artículo
- [ ] Sitio verificado en Google Search Console
- [ ] Más adelante: Google AdSense y activar los slots
