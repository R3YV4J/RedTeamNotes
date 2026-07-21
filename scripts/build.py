#!/usr/bin/env python3
"""
============================================================
 RedTeamNotes — Build Script
============================================================
Convierte artículos en Markdown (carpeta /posts-markdown) en
páginas HTML completas (carpeta /posts), y regenera:

  - sitemap.xml
  - assets/js/posts-index.js   (índice para el buscador)
  - feed.xml                   (RSS)
  - pages/blog.html            (listado paginado de artículos)

El nombre del sitio, el autor y los enlaces sociales se leen de
config/site.json — no hay nada hardcodeado en este script.
Si cambias de nombre, de autor o de dominio, edita solo ese archivo.

USO:
    python3 scripts/build.py

REQUISITOS:
    pip install markdown pyyaml --break-system-packages

FLUJO DE TRABAJO EDITORIAL:
    1. Escribes (o redactas a partir de tus notas) un artículo en
       Markdown siguiendo la plantilla en posts-markdown/_template.md
    2. Lo guardas en posts-markdown/mi-articulo.md
    3. Ejecutas: python3 scripts/build.py
    4. git add . && git commit -m "Nuevo artículo" && git push
    5. GitHub Pages publica automáticamente (o usa el workflow
       de GitHub Actions incluido para que el build se haga solo).
============================================================
"""

import os
import re
import sys
import json
import html
import shutil
from pathlib import Path
from datetime import datetime, timezone

try:
    import markdown
except ImportError:
    sys.exit("❌ Falta la librería 'markdown'. Instala con:\n   pip install markdown pyyaml --break-system-packages")

try:
    import yaml
except ImportError:
    sys.exit("❌ Falta la librería 'pyyaml'. Instala con:\n   pip install markdown pyyaml --break-system-packages")


# ============================================================
# CONFIGURACIÓN CENTRAL (config/site.json)
# ============================================================
ROOT = Path(__file__).resolve().parent.parent
POSTS_MD_DIR = ROOT / "posts-markdown"
POSTS_HTML_DIR = ROOT / "posts"
TEMPLATE_PATH = ROOT / "templates" / "article.html"
CONFIG_PATH = ROOT / "config" / "site.json"
POSTS_PER_PAGE = 9

if not CONFIG_PATH.exists():
    sys.exit(f"❌ No existe {CONFIG_PATH}. Crea config/site.json (ver config/site.example.json).")

with open(CONFIG_PATH, encoding="utf-8") as f:
    SITE_CONFIG = json.load(f)

SITE_URL = SITE_CONFIG["domain"].rstrip("/")
SITE_NAME = SITE_CONFIG["site_name"]
SITE_TAGLINE = SITE_CONFIG.get("site_tagline", "")
SITE_DESCRIPTION = SITE_CONFIG.get("site_description", "")
AUTHOR = SITE_CONFIG["author"]
# BASE_PATH: subcarpeta del sitio (ej: "/RedTeamNotes" si el repo no es usuario.github.io)
# Vacío ("") si el sitio está en la raíz del dominio.
BASE_PATH = SITE_CONFIG.get("base_path", "").rstrip("/")
# URL completa del sitio (dominio + subcarpeta si la hay)
FULL_URL = SITE_URL.rstrip("/") + BASE_PATH
AUTHOR_NAME = AUTHOR["name"]

CATEGORY_SLUGS = {
    "Pentesting": "pentesting",
    "OSINT": "osint",
    "Redes": "redes",
    "Linux": "linux",
    "Python": "python",
    "Certificaciones": "certificaciones",
    "Vulnerabilidades": "vulnerabilidades",
    "Herramientas": "herramientas",
}

CATEGORY_ICONS = {
    "Pentesting": "⚔️", "OSINT": "🔍", "Redes": "🌐", "Linux": "🐧",
    "Python": "🐍", "Certificaciones": "🏆", "Vulnerabilidades": "🛡️",
    "Herramientas": "🔧",
}

MONTHS_ES = ["enero","febrero","marzo","abril","mayo","junio","julio",
             "agosto","septiembre","octubre","noviembre","diciembre"]


# ============================================================
# UTILIDADES
# ============================================================
def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[áàä]", "a", text)
    text = re.sub(r"[éèë]", "e", text)
    text = re.sub(r"[íìï]", "i", text)
    text = re.sub(r"[óòö]", "o", text)
    text = re.sub(r"[úùü]", "u", text)
    text = re.sub(r"[ñ]", "n", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_frontmatter(raw_text):
    """Separa el frontmatter YAML del contenido Markdown."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_text, re.DOTALL)
    if not match:
        sys.exit("❌ El archivo no tiene frontmatter válido (---). Revisa el formato.")
    meta = yaml.safe_load(match.group(1))
    body = match.group(2)
    return meta, body


def date_human(date_str):
    """2024-01-15 -> 15 Enero 2024"""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{d.day} {MONTHS_ES[d.month-1].capitalize()} {d.year}"


def estimate_read_time(text):
    words = len(re.findall(r"\w+", text))
    return max(1, round(words / 200))


def add_heading_ids(html_content):
    """Añade id= a cada h2/h3 para que el TOC funcione (anchors)."""
    def repl(m):
        tag, attrs, text = m.group(1), m.group(2) or "", m.group(3)
        clean_text = re.sub(r"<[^>]+>", "", text)
        hid = slugify(clean_text)
        return f'<{tag}{attrs} id="{hid}">{text}</{tag}>'
    return re.sub(r"<(h2|h3)([^>]*)>(.*?)</\1>", repl, html_content)


def extract_toc(html_content):
    """Extrae h2/h3 con sus IDs para construir el índice (TOC)."""
    toc = []
    for m in re.finditer(r'<(h2|h3)\s+id="([^"]+)">(.*?)</\1>', html_content):
        tag, hid, text = m.groups()
        clean_text = re.sub(r"<[^>]+>", "", text)
        toc.append((tag, hid, clean_text))
    return toc


def render_toc_html(toc):
    items = []
    for tag, hid, text in toc:
        cls = ' class="toc-h3"' if tag == "h3" else ""
        items.append(f'<li><a href="#{hid}"{cls}>{html.escape(text)}</a></li>')
    return "\n".join(items)


def html_attr_escape(text):
    """Escapa texto para uso seguro dentro de atributos HTML (comillas dobles, etc.)."""
    return html.escape(str(text), quote=True)


def json_escape(text):
    """Escapa texto para uso seguro dentro de un string JSON ya embebido en HTML."""
    # json.dumps añade comillas envolventes que no queremos aquí, solo el contenido escapado
    return json.dumps(str(text), ensure_ascii=False)[1:-1]


def render_tags_html(tags):
    return "\n".join(f'<a href="#" class="tag">{html.escape(t)}</a>' for t in tags)


# ============================================================
# BUILD: UN ARTÍCULO
# ============================================================
def build_article(md_path, template):
    raw = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)

    required = ["title", "description", "slug", "category", "date"]
    for field in required:
        if field not in meta:
            sys.exit(f"❌ Falta el campo obligatorio '{field}' en {md_path.name}")

    slug = meta["slug"]
    category = meta["category"]
    category_slug = CATEGORY_SLUGS.get(category, slugify(category))
    tags = meta.get("tags", [])
    level = meta.get("level", "General")
    # El autor es opcional en el frontmatter: si no se indica, se usa
    # el autor por defecto definido en config/site.json
    author_name = meta.get("author", AUTHOR_NAME)

    # Convertir Markdown -> HTML
    md_converter = markdown.Markdown(extensions=["extra", "tables", "fenced_code", "sane_lists"])
    content_html = md_converter.convert(body)
    content_html = add_heading_ids(content_html)
    toc = extract_toc(content_html)
    toc_html = render_toc_html(toc)

    read_time = estimate_read_time(body)
    date_iso = meta["date"]
    date_h = date_human(date_iso)

    # Reemplazos en la plantilla
    # NOTA: los campos de texto libre (title, description, author, category,
    # keywords) se HTML-escapan por defecto porque se insertan tanto en
    # atributos HTML como en texto plano. Para los bloques <script type="
    # application/ld+json"> existen variantes "_JSON" con escaping específico
    # de cadenas JSON, para evitar romper el HTML o el JSON si el contenido
    # contiene comillas, símbolos & u otros caracteres especiales.
    title_safe = html_attr_escape(meta["title"])
    description_safe = html_attr_escape(meta["description"])
    author_safe = html_attr_escape(author_name)
    category_safe = html_attr_escape(category)
    keywords_safe = html_attr_escape(", ".join(tags))

    replacements = {
        "{{TITLE}}": title_safe,
        "{{TITLE_SHORT}}": html_attr_escape(meta["title"][:60]),
        "{{TITLE_ENCODED}}": html.escape(meta["title"]).replace(" ", "%20"),
        "{{TITLE_JSON}}": json_escape(meta["title"]),
        "{{DESCRIPTION}}": description_safe,
        "{{DESCRIPTION_JSON}}": json_escape(meta["description"]),
        "{{KEYWORDS}}": keywords_safe,
        "{{KEYWORDS_JSON}}": json_escape(", ".join(tags)),
        "{{AUTHOR}}": author_safe,
        "{{AUTHOR_JSON}}": json_escape(author_name),
        "{{AUTHOR_BIO}}": html_attr_escape(AUTHOR.get("bio", "")),
        "{{AUTHOR_AVATAR}}": AUTHOR.get("avatar", "🐧"),
        "{{AUTHOR_GITHUB}}": AUTHOR.get("github", "#"),
        "{{AUTHOR_LINKEDIN}}": AUTHOR.get("linkedin", "#"),
        "{{AUTHOR_PORTFOLIO}}": AUTHOR.get("portfolio", "#"),
        "{{SITE_NAME}}": html_attr_escape(SITE_NAME),
        "{{SLUG}}": slug,
        "{{CATEGORY}}": category_safe,
        "{{CATEGORY_JSON}}": json_escape(category),
        "{{CATEGORY_SLUG}}": category_slug,
        "{{DATE_ISO}}": date_iso,
        "{{DATE_MODIFIED_ISO}}": meta.get("date_modified", date_iso),
        "{{DATE_HUMAN}}": date_h,
        "{{READ_TIME}}": str(read_time),
        "{{LEVEL}}": html_attr_escape(level),
        "{{CONTENT}}": content_html,
        "{{TAGS_HTML}}": render_tags_html(tags),
        "{{TAGS_OG}}": keywords_safe,
        "{{URL_ENCODED}}": f"{FULL_URL}/posts/{slug}.html",
        "{{SITE_URL}}": FULL_URL,
        "{{BASE_PATH}}": BASE_PATH,
        "{{BASE_PATH}}": BASE_PATH,
    }

    output = template
    for key, val in replacements.items():
        output = output.replace(key, val)

    # Inyectar TOC (sección principal + sidebar)
    output = output.replace(
        '<ul class="toc-list" id="toc-list">\n            <!-- Populated by JS -->\n          </ul>',
        f'<ul class="toc-list" id="toc-list">{toc_html}</ul>'
    )
    output = output.replace(
        '<ul class="toc-list" id="toc-sidebar">\n            <!-- Populated by JS -->\n          </ul>',
        f'<ul class="toc-list" id="toc-sidebar">{toc_html}</ul>'
    )

    out_path = POSTS_HTML_DIR / f"{slug}.html"
    out_path.write_text(output, encoding="utf-8")
    print(f"  ✓ {slug}.html")

    excerpt = re.sub(r"<[^>]+>", "", content_html)[:160].strip() + "..."

    # Detecta si existe una imagen de portada para este artículo
    cover_path_png  = ROOT / "assets" / "images" / f"cover-{slug}.png"
    cover_path_jpg  = ROOT / "assets" / "images" / f"cover-{slug}.jpg"
    cover_path_jpeg = ROOT / "assets" / "images" / f"cover-{slug}.jpeg"
    has_cover = cover_path_png.exists() or cover_path_jpg.exists() or cover_path_jpeg.exists()
    # Determinar extensión real para que el JS use la URL correcta
    if cover_path_png.exists():
        cover_ext = "png"
    elif cover_path_jpg.exists():
        cover_ext = "jpg"
    elif cover_path_jpeg.exists():
        cover_ext = "jpeg"
    else:
        cover_ext = "png"

    return {
        "title": meta["title"],
        "slug": slug,
        "url": f"{BASE_PATH}/posts/{slug}.html",
        "hasCover": has_cover,
        "coverExt": cover_ext,
        "category": category,
        "categorySlug": category_slug,
        "tags": tags,
        "date": date_iso,
        "dateHuman": date_h,
        "readTime": f"{read_time} min",
        "author": author_name,
        "excerpt": meta["description"],
    }


# ============================================================
# BUILD: ÍNDICE DE POSTS (para buscador JS)
# ============================================================
def write_posts_index(posts):
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)
    js_content = "// Auto-generado por scripts/build.py — NO EDITAR A MANO\n"
    js_content += f"window.POSTS_INDEX = {json.dumps(posts_sorted, ensure_ascii=False, indent=2)};\n"
    out_path = ROOT / "assets" / "js" / "posts-index.js"
    out_path.write_text(js_content, encoding="utf-8")
    print(f"  ✓ assets/js/posts-index.js ({len(posts)} artículos)")


# ============================================================
# BUILD: SITEMAP.XML
# ============================================================
def write_sitemap(posts):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [
        (f"{FULL_URL}/", "1.0", "daily"),
        (f"{FULL_URL}/pages/blog.html", "0.9", "daily"),
        (f"{FULL_URL}/pages/sobre-mi.html", "0.5", "monthly"),
    ]
    for cat_slug in CATEGORY_SLUGS.values():
        urls.append((f"{FULL_URL}/categories/{cat_slug}.html", "0.7", "weekly"))

    entries = []
    for loc, priority, freq in urls:
        entries.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    for p in posts:
        entries.append(f"""  <url>
    <loc>{FULL_URL}/posts/{p['slug']}.html</loc>
    <lastmod>{p['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(entries)}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"  ✓ sitemap.xml ({len(urls) + len(posts)} URLs)")


# ============================================================
# BUILD: RSS FEED
# ============================================================
def write_rss(posts):
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)[:20]
    items = []
    for p in posts_sorted:
        pub_date = datetime.strptime(p["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")
        items.append(f"""    <item>
      <title>{html.escape(p['title'])}</title>
      <link>{FULL_URL}/posts/{p['slug']}.html</link>
      <guid>{FULL_URL}/posts/{p['slug']}.html</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{html.escape(p['excerpt'])}</description>
      <category>{html.escape(p['category'])}</category>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_NAME}</title>
    <link>{FULL_URL}/</link>
    <description>{html.escape(SITE_DESCRIPTION)}</description>
    <language>es</language>
    <atom:link href="{FULL_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(rss, encoding="utf-8")
    print(f"  ✓ feed.xml ({len(items)} artículos)")


# ============================================================
# MAIN
# ============================================================

# ============================================================
# BUILD: PÁGINAS ESTÁTICAS (home, categorías, legales...)
# ============================================================
STATIC_SRC_DIR = ROOT / "templates-static"

def process_static_pages():
    """
    Lee las páginas fuente de templates-static/ (que contienen
    placeholders {{SITE_NAME}}, {{SITE_URL}}, {{AUTHOR_NAME}},
    {{AUTHOR_GITHUB}}, {{AUTHOR_LINKEDIN}}, {{AUTHOR_PORTFOLIO}}) y
    escribe la versión final ya rellenada en su ubicación pública
    (raíz del sitio, categories/, pages/).

    IMPORTANTE: las páginas fuente viven en templates-static/, NUNCA
    en index.html/404.html/categories/.../pages/... directamente.
    Esos archivos finales se SOBRESCRIBEN en cada build — cualquier
    edición manual hecha ahí se perderá. Para cambiar el contenido de
    una página estática, edita su fuente en templates-static/.

    Esto es lo que permite que cambiar config/site.json se propague
    a TODO el sitio (no solo a los artículos) con un solo build,
    las veces que haga falta, sin que los placeholders se "gasten".
    """
    if not STATIC_SRC_DIR.exists():
        print("  ⚠️  No existe templates-static/, se omite el procesado de páginas estáticas")
        return

    replacements = {
        "{{SITE_NAME}}":       SITE_NAME,
        "{{SITE_URL}}":        FULL_URL,
        "{{BASE_PATH}}":       BASE_PATH,
        "{{AUTHOR_NAME}}":     html_attr_escape(AUTHOR_NAME),
        "{{AUTHOR_GITHUB}}":   AUTHOR.get("github", "#"),
        "{{AUTHOR_LINKEDIN}}": AUTHOR.get("linkedin", "#"),
        "{{AUTHOR_PORTFOLIO}}": AUTHOR.get("portfolio", "#"),
        "{{AUTHOR_EMAIL}}": AUTHOR.get("email", ""),
    }

    src_files = list(STATIC_SRC_DIR.rglob("*.html"))
    updated = 0
    for src_path in src_files:
        rel_path = src_path.relative_to(STATIC_SRC_DIR)
        dest_path = ROOT / rel_path

        text = src_path.read_text(encoding="utf-8")
        for key, val in replacements.items():
            text = text.replace(key, val)

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(text, encoding="utf-8")
        updated += 1

    print(f"  ✓ {updated} páginas estáticas regeneradas desde templates-static/")


def main():
    print(f"\n🔧 {SITE_NAME} — Build iniciado\n{'='*40}")

    if not POSTS_MD_DIR.exists():
        sys.exit(f"❌ No existe la carpeta {POSTS_MD_DIR}")

    POSTS_HTML_DIR.mkdir(exist_ok=True)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    md_files = sorted(POSTS_MD_DIR.glob("*.md"))
    md_files = [f for f in md_files if not f.name.startswith("_")]  # ignorar plantillas

    if not md_files:
        print("⚠️  No se encontraron artículos en posts-markdown/. Nada que construir.")
        return

    print(f"\n📝 Procesando {len(md_files)} artículo(s):\n")
    posts = []
    for md_file in md_files:
        try:
            post_data = build_article(md_file, template)
            posts.append(post_data)
        except Exception as e:
            print(f"  ✗ ERROR en {md_file.name}: {e}")

    print(f"\n📦 Generando archivos derivados:\n")
    write_posts_index(posts)
    write_sitemap(posts)
    write_rss(posts)
    process_static_pages()

    print(f"\n{'='*40}")
    print(f"✅ Build completado: {len(posts)} artículo(s) publicados.\n")


if __name__ == "__main__":
    main()
