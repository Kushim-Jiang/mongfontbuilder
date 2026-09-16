#!/usr/bin/env python3
r"""Render the Astro docs site into a single PDF.

Prints every documentation page, in the same order as the site's sidebar, into
one PDF with:

  * a table of contents whose entries carry their real page numbers,
  * a page-numbered footer ("N / M") on every content page,
  * PDF bookmarks (WeasyPrint auto-generates an outline from h1–h6).

It renders the *built* site in `dist/`, so run `npm run build` first, or pass
`--build` to do it here.

Usage:
    npm run pdf                     # dist/ -> temp/mongolian-utn.pdf
    npm run pdf -- --build          # run `npm run build` first
    python tools/make_pdf.py --out out.pdf
"""

from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT_DEFAULT = ROOT / "temp" / "mongolian-utn.pdf"
ASTRO_CONFIG = ROOT / "astro.config.ts"


def _pango_dir() -> str | None:
    r"""The directory carrying the Pango/GLib DLLs, if one can be found.

    Only Windows needs this: elsewhere WeasyPrint loads the system Pango by name. On
    Windows `WEASYPRINT_DLL_DIR` names the directory outright; failing that the usual
    MSYS2 location is tried, and failing that the DLL is looked for along `PATH`, which
    finds a GTK build that shipped with some other program. WeasyPrint locates the DLL
    itself on `PATH`, but its own dependencies are only resolved once the directory is
    in the DLL search path, which is what `add_dll_directory` arranges.
    """

    _MSYS64_BIN = r"C:\msys64\ucrt64\bin"
    _PANGO_DLL = "libpango-1.0-0.dll"

    if os.name != "nt":
        return None
    if named := os.environ.get("WEASYPRINT_DLL_DIR"):
        return named
    if Path(_MSYS64_BIN).is_dir():
        return _MSYS64_BIN
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if entry and (Path(entry) / _PANGO_DLL).is_file():
            return entry
    return None


def _setup_weasyprint() -> None:
    """Make the Pango/GLib DLLs discoverable before importing WeasyPrint."""
    if (bin_dir := _pango_dir()) is None:
        return
    try:
        os.add_dll_directory(bin_dir)  # Python >= 3.8
    except OSError:
        pass
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")


_setup_weasyprint()

import lxml.etree as etree  # noqa: E402
from lxml import html as lhtml  # noqa: E402
from weasyprint import HTML  # noqa: E402

# --------------------------------------------------------------------------- #
# astro.config.ts parsing
# --------------------------------------------------------------------------- #


def parse_site_title() -> str:
    text = ASTRO_CONFIG.read_text(encoding="utf-8")
    m = re.search(r'title:\s*"([^"]+)"', text)
    return m.group(1) if m else "Mongolian Font Builder"


def parse_sidebar_slugs() -> list[str]:
    """Return the doc slugs in the exact order of the Starlight `sidebar` array."""
    text = ASTRO_CONFIG.read_text(encoding="utf-8")
    m = re.search(r"sidebar\s*:\s*\[", text)
    if not m:
        raise SystemExit("could not find `sidebar: [` in astro.config.ts")
    start = m.end() - 1  # index of '['
    depth = 0
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise SystemExit("unbalanced `sidebar` array in astro.config.ts")
    block = text[start : end + 1]

    slugs: list[str] = []
    for mm in re.finditer(r'"((?:[^"\\]|\\.)*)"', block):
        prefix = block[: mm.start()].rstrip()
        # Skip object keys (e.g. `label: "Writing systems"`); everything else
        # inside the sidebar array is a page slug.
        if re.search(r"\b(?:label|icon|text|link|href)\s*:\s*$", prefix):
            continue
        slugs.append(mm.group(1))
    return slugs


# --------------------------------------------------------------------------- #
# dist/ reading
# --------------------------------------------------------------------------- #


def page_html_path(slug: str) -> Path:
    return DIST / "index.html" if slug == "index" else DIST / slug / "index.html"


CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(/[^'\")\s]+)\1\s*\)")


def _rewrite_css_url(m: re.Match[str]) -> str:
    quote, path = m.group(1), m.group(2)
    target = (DIST / path.lstrip("/")).resolve()
    return f"url({quote}{target.as_uri()}{quote})"


def rewrite_css_urls(css_text: str) -> str:
    """Turn root-absolute `url(/...)` references into absolute file:// URLs."""
    return CSS_URL_RE.sub(_rewrite_css_url, css_text)


def collect_css(doc, seen: dict[str, str]) -> None:
    """Inline the page's stylesheets and <style> blocks into a deduped dict."""
    root = doc.getroot()
    for link in root.xpath('//link[@rel="stylesheet"]'):
        href = link.get("href", "")
        media = (link.get("media") or "").strip()
        if media == "print":
            continue  # we supply our own print.css
        if href.startswith(("http://", "https://", "data:", "mailto:")):
            continue
        fp = DIST / href.lstrip("/")
        if href not in seen and fp.is_file():
            seen[href] = rewrite_css_urls(fp.read_text(encoding="utf-8"))
    for style in root.xpath("//style"):
        text = style.text_content() or ""
        if text.strip():
            seen.setdefault(f"inline:{hash(text)}", text)


def firstWithClass(node, className: str):
    """Return the first descendant of *node* carrying the CSS class *className*."""
    found = node.xpath(
        f".//*[contains(concat(' ', normalize-space(@class), ' '), ' {className} ')]"
    )
    return found[0] if found else None


def extractHero(root) -> str:
    """Return the hero of a page as HTML: its tagline, then the links it offers.

    A page that carries a hero has no content of its own (the home page): the hero is
    what the page is — the sentence under the title, and the links the reader is asked
    to go on with. A printed link is nothing to click, so every one of them is written
    out with the address it goes to.
    """

    hero = firstWithClass(root, "hero")
    if hero is None:
        return ""

    parts: list[str] = []
    if (tagline := firstWithClass(hero, "tagline")) is not None:
        parts.append(f"<p class='doc-tagline'>{html.escape(tagline.text_content().strip())}</p>")

    actions = firstWithClass(hero, "actions")
    links = actions.xpath(".//a[@href]") if actions is not None else []
    if links:
        items = "".join(
            "<li>"
            f"<a href='{html.escape(a.get('href', ''), quote=True)}'>"
            f"{html.escape(' '.join(a.itertext()).strip())}</a>"
            f"<span class='doc-link-address'>{html.escape(a.get('href', ''))}</span>"
            "</li>"
            for a in links
        )
        parts.append(f"<ul class='doc-links'>{items}</ul>")

    return "\n".join(parts)


def extract_page(doc):
    """Return (title, body_html) for a page, pulling the markdown content."""
    root = doc.getroot()
    h1s = root.xpath("//h1")
    title = " ".join(h1s[0].itertext()).strip() if h1s else ""
    hero_html = extractHero(root)
    content = firstWithClass(root, "sl-markdown-content")
    if content is None:
        # A page with no markdown content of its own — the home page — is its hero.
        body_html = hero_html
    else:
        body_html = hero_html + etree.tostring(content, method="html", encoding="unicode")
    return title, body_html


def process_content(slug: str, body_html: str):
    """Namespace ids/links per page and return (body_html, headings)."""
    if not body_html.strip():
        return "", []

    frag = lhtml.fromstring(body_html)

    for el in frag.xpath(".//style | .//script | .//link"):
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)

    idmap: dict[str, str] = {}
    used: set[str] = set()
    for el in frag.xpath("//*[@id]"):
        old = el.get("id")
        base = f"{slug}-{old}"
        new, n = base, 1
        while new in used:
            n += 1
            new = f"{base}-{n}"
        used.add(new)
        el.set("id", new)
        idmap[old] = new

    for a in frag.xpath("//a[@href]"):
        href = a.get("href") or ""
        if href.startswith("#"):
            anchor = href[1:]
            a.set("href", f"#{idmap.get(anchor, slug + '-' + anchor)}")
        elif href.startswith("/"):
            m = re.match(r"^/([^/#]+)/?(?:#(.+))?$", href)
            if m:
                target_slug, anchor = m.group(1), m.group(2)
                a.set("href", f"#{target_slug}-{anchor}" if anchor else f"#{target_slug}-top")

    for el in frag.xpath("//img[@src] | //source[@src]"):
        src = el.get("src") or ""
        if src.startswith("/"):
            el.set("src", (DIST / src.lstrip("/")).resolve().as_uri())

    headings = []
    for h in frag.xpath(".//h2 | .//h3 | .//h4 | .//h5 | .//h6"):
        text = " ".join(h.itertext()).strip()
        hid = h.get("id")
        if text and hid:
            headings.append((int(h.tag[1]), hid, text))

    return etree.tostring(frag, method="html", encoding="unicode"), headings


# --------------------------------------------------------------------------- #
# assembly + rendering
# --------------------------------------------------------------------------- #


def build_document(slugs: list[str], site_title: str) -> tuple[str, int]:
    seen_css: dict[str, str] = {}
    pages: list[tuple[str, str, str]] = []  # (slug, title, body_html)
    headings_by_slug: dict[str, list] = {}

    for slug in slugs:
        path = page_html_path(slug)
        if not path.is_file():
            raise SystemExit(f"missing built page: {path} — run `npm run build` first")
        doc = lhtml.parse(str(path))
        collect_css(doc, seen_css)
        title, body_html = extract_page(doc)
        body_html, headings = process_content(slug, body_html)
        pages.append((slug, title, body_html))
        headings_by_slug[slug] = headings

    all_levels = [lv for hs in headings_by_slug.values() for lv, _, _ in hs]
    min_level = min(all_levels) if all_levels else 2

    # --- table of contents -------------------------------------------------
    toc_items: list[str] = []
    for slug, title, _ in pages:
        toc_items.append(f'<li class="toc-l0"><a href="#{slug}-top">{html.escape(title)}</a></li>')
        for level, hid, text in headings_by_slug[slug]:
            depth = level - min_level + 1
            toc_items.append(
                f'<li class="toc-l{depth}"><a href="#{hid}">{html.escape(text)}</a></li>'
            )

    # --- page sections -----------------------------------------------------
    sections: list[str] = []
    for slug, title, body_html in pages:
        sections.append(
            f'<section class="print-page" id="{slug}">'
            f'<h1 class="page-title" id="{slug}-top">{html.escape(title)}</h1>'
            f'<div class="page-body">{body_html}</div>'
            f"</section>"
        )

    css_blocks = "\n".join(f"<style>{css}</style>" for css in seen_css.values())
    print_css = (Path(__file__).parent / "print.css").read_text(encoding="utf-8")

    doc_html = "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="en" data-theme="light">',
            "<head>",
            '<meta charset="utf-8"/>',
            f"<title>{html.escape(site_title)} — Documentation</title>",
            css_blocks,
            f"<style>{print_css}</style>",
            "</head>",
            "<body>",
            '<section class="doc-front">',
            '  <div class="doc-title">',
            f"    <h1>{html.escape(site_title)}</h1>",
            '    <p class="doc-subtitle">Documentation &amp; draft of the Mongolian UTN (UTN #57)</p>',
            "  </div>",
            '  <nav class="toc">',
            '    <h2 class="toc-title">Contents</h2>',
            f"    <ul>{''.join(toc_items)}</ul>",
            "  </nav>",
            "</section>",
            *sections,
            "</body>",
            "</html>",
        ]
    )

    page_count = len(pages)
    return doc_html, page_count


def main() -> None:
    ap = argparse.ArgumentParser(description="Render the docs site into a single PDF.")
    ap.add_argument("--build", action="store_true", help="run `npm run build` first")
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT, help="output PDF path")
    args = ap.parse_args()

    if args.build:
        npm = "npm.cmd" if os.name == "nt" else "npm"
        subprocess.run([npm, "run", "build"], cwd=ROOT, check=True)

    if not DIST.is_dir():
        raise SystemExit(f"{DIST} not found — run `npm run build` first")

    slugs = parse_sidebar_slugs()
    print("sidebar order:", " ".join(slugs))

    site_title = parse_site_title()
    doc_html, page_count = build_document(slugs, site_title)

    tmp = DIST / "print.html"
    tmp.write_text(doc_html, encoding="utf-8")
    print(f"merged HTML written to {tmp} ({page_count} pages)")

    document = HTML(filename=str(tmp)).render()
    print(f"rendered {len(document.pages)} PDF pages")
    document.write_pdf(str(args.out))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
