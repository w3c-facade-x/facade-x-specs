#!/usr/bin/env python3
"""Build script for the Façade-X specifications.

Editable prose lives in Markdown under ``content/``. The ReSpec scaffolding
(config script, MathJax/Turtle setup, styles, ``<head>``) lives in a single
HTML template. This script renders each Markdown file to an HTML fragment and
injects it into the template, writing the finished documents into ``_site/``. Static assets referenced by the specs (e.g. images)
are copied across as-is.

Every ``content/<name>.md`` is rendered with the shared template
``templates/spec.html`` into ``_site/<name>.html``. Each Markdown file starts
with a front matter block giving the page title and subtitle::

    ---
    title: <code>Façade-X</code> mapping for JSON
    subtitle: Representing JSON in Façade-X.
    order: 9
    ---

The optional ``order`` field sets the position of the page in the "Set of
Documents" list that the build adds to the Status of This Document section of
every page (pages without it come last, by file name).

Run with no arguments from the repository root:

    python build.py
"""

from __future__ import annotations

import html as htmllib
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
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
TEMPLATE_PATH = ROOT / "templates" / "spec.html"
OUTPUT_DIR = ROOT / "_site"

GITHUB_REPO = "w3c-facade-x/facade-x-specs"
ISSUES_MARKER = re.compile(r'<!--\s*BUILD:ISSUES\s+label="(?P<label>[^"]+)"\s*-->')

# Static files copied verbatim into _site.
STATIC_FILES = ["model.png"]

# Placeholders in the shared template.
BODY_MARKER = "<!-- BUILD:CONTENT -->"
FRONT_MATTER = re.compile(r"\A---\n(?P<head>.*?)\n---\n", re.DOTALL)
FRONT_MATTER_KEYS = ("title", "subtitle")
DEFAULT_ORDER = 1000
SOTD_OPEN = re.compile(r'<section\s+id="sotd"[^>]*>')
NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
                "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]


def _restore_raw_blocks(html: str) -> str:
    """Turn fenced ``math`` / ``turtle`` code blocks back into bare markup.

    The page's own MathJax and Turtle scripts look for ``<pre class="math">``
    elements and ``<pre class="turtle">`` / ``<pre class="example">`` blocks. The
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
            return f'<pre class="math">\n{body}\n    </pre>'
        if lang == "turtle":
            return f'<pre class="turtle">\n{body}\n    </pre>'
        if lang in ("manchester", "example"):
            return f'<pre class="example">\n{body}\n    </pre>'
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


def split_front_matter(md_path: Path) -> tuple[dict[str, str], str]:
    """Return the front matter fields and the Markdown body of a content file."""
    text = md_path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        raise ValueError(f"{md_path.name}: missing front matter (--- title/subtitle ---)")
    fields = {}
    for line in match.group("head").splitlines():
        if line.strip():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    missing = [k for k in FRONT_MATTER_KEYS if k not in fields]
    if missing:
        raise ValueError(f"{md_path.name}: front matter lacks {', '.join(missing)}")
    return fields, text[match.end():]


def render_markdown(text: str) -> str:
    text = _expand_issue_markers(text)
    text = _enable_md_in_blocks(text)
    md = markdown.Markdown(
        extensions=["extra", "attr_list", "fenced_code", "md_in_html"],
        output_format="html5",
    )
    html = md.convert(text)
    # Markdown tables get the same styling as hand-written <table class="model">.
    html = html.replace("<table>", '<table class="model">')
    return _restore_raw_blocks(html)


def plain(title: str) -> str:
    """The title without markup or character references."""
    return htmllib.unescape(re.sub(r"<[^>]+>", "", title))


def collect_pages() -> list[tuple[Path, dict[str, str], str]]:
    """All content pages, in the order of the Set of Documents list."""
    pages = []
    for md_path in CONTENT_DIR.glob("*.md"):
        fields, text = split_front_matter(md_path)
        pages.append((md_path, fields, text))

    def key(page):
        md_path, fields, _ = page
        try:
            order = int(fields.get("order", DEFAULT_ORDER))
        except ValueError:
            raise ValueError(f"{md_path.name}: order must be an integer")
        return (order, md_path.stem)

    return sorted(pages, key=key)


def set_of_documents(pages, current: Path) -> str:
    """HTML for the Set of Documents subsection, marking the current page."""
    count = len(pages)
    count_text = NUMBER_WORDS[count] if count < len(NUMBER_WORDS) else str(count)
    items = []
    for md_path, fields, _ in pages:
        link = f'<a href="{md_path.stem}.html">{htmllib.escape(plain(fields["title"]))}</a>'
        if md_path == current:
            link += " (this document)"
        items.append(f"    <li>{link}</li>")
    return (
        '\n<section id="set-of-documents">\n'
        "  <h3>Set of Documents</h3>\n"
        f"  <p>This document is one of {count_text} Fa&ccedil;ade-X specification documents "
        "produced by the Data Fa&ccedil;ades Community Group:</p>\n"
        "  <ol>\n" + "\n".join(items) + "\n  </ol>\n"
        "</section>\n"
    )


def add_set_of_documents(text: str, block: str) -> str:
    """Append the block to the Status of This Document section, creating it if absent."""
    match = SOTD_OPEN.search(text)
    if not match:
        return f'<section id="sotd">\n{block}\n</section>\n\n' + text
    close = text.index("</section>", match.end())
    return text[:close] + block + "\n" + text[close:]


def build_page(md_path: Path, fields: dict[str, str], text: str, template: str,
               pages) -> None:
    output_path = OUTPUT_DIR / f"{md_path.stem}.html"
    text = add_set_of_documents(text, set_of_documents(pages, md_path))
    plain_title = plain(fields["title"])
    result = (
        template.replace("{{PLAIN_TITLE}}", htmllib.escape(plain_title))
        .replace("{{TITLE}}", fields["title"])
        .replace("{{SUBTITLE}}", fields["subtitle"])
        .replace(BODY_MARKER, render_markdown(text))
    )
    output_path.write_text(result, encoding="utf-8")
    print(f"  built {output_path.name}")


def copy_static() -> None:
    for name in STATIC_FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / name)
            print(f"  copied {name}")
        else:
            print(f"  (skipped missing static file {name})")


def _open_issue_numbers(label: str) -> list[int]:
    """Numbers of open issues carrying `label` (PRs excluded). [] on failure."""
    numbers, page = [], 1
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "facade-x-build"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    try:
        while True:
            q = urllib.parse.urlencode(
                {"state": "open", "labels": label, "per_page": 100, "page": page})
            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/issues?{q}", headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                batch = json.load(resp)
            numbers += [i["number"] for i in batch if "pull_request" not in i]
            if len(batch) < 100:
                break
            page += 1
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        sys.stderr.write(f"  warning: could not fetch issues for label {label!r}: {exc}\n")
        return []
    return numbers

def _expand_issue_markers(text: str) -> str:
    def replace(m):
        nums = _open_issue_numbers(m.group("label"))
        if not nums:
            return f'No open issues with label {m.group("label")}.'
        return "\n".join(f'<p class="issue" data-number="{n}"></p>' for n in nums)
    return ISSUES_MARKER.sub(replace, text)

def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Building Façade-X specs into {OUTPUT_DIR.relative_to(ROOT)}/")
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    pages = collect_pages()
    for md_path, fields, text in pages:
        build_page(md_path, fields, text, template, pages)
    copy_static()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())