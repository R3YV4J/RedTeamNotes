#!/usr/bin/env python3
"""
============================================================
 RedTeamNotes — Generador de imágenes Open Graph
============================================================
Genera una imagen OG (1200x630px) por cada artículo en
posts-markdown/, usando scripts/og-template/template.html como
base y los datos de config/site.json + el frontmatter de cada
artículo.

Requiere wkhtmltoimage instalado en el sistema:
    sudo apt install wkhtmltopdf   (incluye wkhtmltoimage)

USO:
    python3 scripts/generate_og_images.py

Se ejecuta de forma independiente al build principal porque
requiere un binario externo (wkhtmltoimage) que no todos los
entornos de CI tienen disponible por defecto. El workflow de
GitHub Actions incluye un paso para instalarlo.
============================================================
"""

import re
import sys
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_MD_DIR = ROOT / "posts-markdown"
TEMPLATE_PATH = ROOT / "scripts" / "og-template" / "template.html"
OUTPUT_DIR = ROOT / "assets" / "images"
CONFIG_PATH = ROOT / "config" / "site.json"


def check_wkhtmltoimage():
    if shutil.which("wkhtmltoimage") is None:
        sys.exit(
            "❌ wkhtmltoimage no está instalado.\n"
            "   Instálalo con: sudo apt install wkhtmltopdf\n"
            "   (el paquete wkhtmltopdf incluye el binario wkhtmltoimage)"
        )


def parse_frontmatter(raw_text):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw_text, re.DOTALL)
    if not match:
        return {}
    import yaml
    return yaml.safe_load(match.group(1)) or {}


def html_escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main():
    check_wkhtmltoimage()

    if not CONFIG_PATH.exists():
        sys.exit(f"❌ No existe {CONFIG_PATH}")
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    author_name = config["author"]["name"]

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = [f for f in POSTS_MD_DIR.glob("*.md") if not f.name.startswith("_")]
    if not md_files:
        print("⚠️  No hay artículos en posts-markdown/. Nada que generar.")
        return

    print(f"\n🖼  Generando {len(md_files)} imagen(es) OG...\n")

    tmp_dir = ROOT / ".og-tmp"
    tmp_dir.mkdir(exist_ok=True)

    generated = 0
    for md_file in md_files:
        meta = parse_frontmatter(md_file.read_text(encoding="utf-8"))
        slug = meta.get("slug")
        title = meta.get("title", "")
        category = meta.get("category", "")

        if not slug:
            print(f"  ✗ {md_file.name}: sin 'slug' en el frontmatter, se omite")
            continue

        out_path = OUTPUT_DIR / f"og-{slug}.png"
        if out_path.exists():
            print(f"  · og-{slug}.png ya existe, se omite")
            continue

        html = template
        html = html.replace("{{TITLE}}", html_escape(title))
        html = html.replace("{{CATEGORY}}", html_escape(category))
        html = html.replace("{{AUTHOR}}", html_escape(author_name))

        tmp_html = tmp_dir / f"{slug}.html"
        tmp_html.write_text(html, encoding="utf-8")

        result = subprocess.run(
            [
                "wkhtmltoimage",
                "--width", "1200",
                "--height", "630",
                "--javascript-delay", "300",
                "--disable-smart-width",
                "--enable-local-file-access",
                str(tmp_html),
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )

        if out_path.exists():
            # Las imágenes que genera wkhtmltoimage pesan varios MB por
            # defecto aunque son solo texto sobre fondo plano. Las
            # recomprimimos con una paleta reducida si ImageMagick está
            # disponible — sin pérdida visual perceptible, reduce el peso
            # en más de un 99% (de ~3MB a ~17KB).
            if shutil.which("convert"):
                subprocess.run(
                    ["convert", str(out_path), "-strip", "-colors", "64", "-depth", "8", str(out_path)],
                    capture_output=True,
                )
            print(f"  ✓ og-{slug}.png")
            generated += 1
        else:
            print(f"  ✗ {slug}: fallo al generar — {result.stderr.strip()[:200]}")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"\n✅ {generated}/{len(md_files)} imágenes OG generadas en assets/images/\n")


if __name__ == "__main__":
    main()
