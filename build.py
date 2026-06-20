#!/usr/bin/env python3
"""Build script for the Façade-X specifications.

Editable prose lives in Markdown under ``content/``. The ReSpec scaffolding
(config script, MathJax/Turtle setup, styles, ``<head>``) lives in HTML
templates under ``templates/``. This script renders each Markdown file to an
HTML fragment and injects it into the matching template, writing the finished
documents into ``_site/``. Static assets referenced by the specs (e.g. images)
are copied across as-is.

Run with no arguments from the repository root:

    python build.py

The mapping between content, template and output is declared in ``PAGES``.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

try:
    import markdown
except ImportError:  # pragma: no cover - guidance for local runs
    sys.stderr.write(
        "The 'markdown' package is required. Install it with:\n"
        "    pip install markdown\n"
    )
    raise

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "_site"

# (markdown file, template file, output file)
PAGES = [
    ("index.md", "index.html", "index.html"),
    ("metamodel.md", "metamodel.html", "metamodel.html"),
    ("rdf.md", "rdf.html", "rdf.html"),
]

# Static files copied verbatim into _site.
STATIC_FILES = ["model.png"]

# Marker in each template that gets replaced by the rendered Markdown body.
BODY_MARKER = "<!-- BUILD:CONTENT -->"


def _restore_raw_blocks(html: str) -> str:
    """Turn fenced ``math`` / ``turtle`` code blocks back into bare markup.

    The page's own MathJax and Turtle scripts look for plain ``<pre>`` elements
    (math) and ``<pre class="turtle">`` / ``<pre class="example">`` blocks. The
    Markdown renderer emits ``<pre><code class="language-...">`` for fenced
    blocks, so we rewrite those specific languages into the shape the existing
    client-side scripts expect, leaving their contents untouched.
    """

    def replace(match: re.Match) -> str:
        lang = match.group("lang")
        body = match.group("body")
        # The markdown library HTML-escapes code block contents; that escaping
        # is exactly what the original hand-written HTML used for these blocks
        # (e.g. &lt; in Turtle/Manchester), so we keep it as-is.
        if lang == "math":
            return f"<pre>\n{body}\n    </pre>"
        if lang == "turtle":
            return f'<pre class="turtle">\n{body}\n    </pre>'
        if lang in ("manchester", "example"):
            return f'<pre data-nomath class="example">\n{body}\n    </pre>'
        # Any other language: leave the rendered <pre><code> intact.
        return match.group(0)

    pattern = re.compile(
        r'<pre><code class="language-(?P<lang>[^"]+)">(?P<body>.*?)</code></pre>',
        re.DOTALL,
    )
    return pattern.sub(replace, html)


def _enable_md_in_blocks(text: str) -> str:
    """Add ``markdown="1"`` to wrapper block tags so their Markdown is parsed.

    Authors write plain ``<section ...>`` / ``<div ...>`` wrappers in the
    content files; the ``md_in_html`` extension only descends into elements
    that carry a ``markdown`` attribute. Rather than make authors repeat that
    attribute everywhere, we add it automatically to opening ``<section>`` and
    ``<div>`` tags that don't already declare one. Tags that should stay opaque
    (e.g. ``<pre>``) are untouched.
    """

    def add_attr(match: re.Match) -> str:
        tag = match.group("tag")
        attrs = match.group("attrs") or ""
        if "markdown=" in attrs:
            return match.group(0)
        return f"<{tag}{attrs} markdown=\"1\">"

    pattern = re.compile(r"<(?P<tag>section|div)(?P<attrs>\s[^>]*?)?>")
    return pattern.sub(add_attr, text)


def render_markdown(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    text = _enable_md_in_blocks(text)
    md = markdown.Markdown(
        extensions=["extra", "attr_list", "fenced_code", "md_in_html"],
        output_format="html5",
    )
    html = md.convert(text)
    return _restore_raw_blocks(html)


def build_page(md_name: str, template_name: str, output_name: str) -> None:
    md_path = CONTENT_DIR / md_name
    template_path = TEMPLATE_DIR / template_name
    output_path = OUTPUT_DIR / output_name

    if not md_path.exists():
        raise FileNotFoundError(f"Missing content file: {md_path}")
    if not template_path.exists():
        raise FileNotFoundError(f"Missing template file: {template_path}")

    template = template_path.read_text(encoding="utf-8")
    if BODY_MARKER not in template:
        raise ValueError(
            f"Template {template_name} does not contain the body marker "
            f"{BODY_MARKER!r}"
        )

    body = render_markdown(md_path)
    result = template.replace(BODY_MARKER, body)
    output_path.write_text(result, encoding="utf-8")
    print(f"  built {output_name}  ({md_name} + {template_name})")


def copy_static() -> None:
    for name in STATIC_FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / name)
            print(f"  copied {name}")
        else:
            print(f"  (skipped missing static file {name})")


def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Building Façade-X specs into {OUTPUT_DIR.relative_to(ROOT)}/")
    for md_name, template_name, output_name in PAGES:
        build_page(md_name, template_name, output_name)
    copy_static()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
