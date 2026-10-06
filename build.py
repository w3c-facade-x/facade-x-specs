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

The optional ``parent`` field names another page (by file name, without
``.md``) that lists this one, e.g. ``parent: mappings`` for a format mapping.
Such pages are left out of the Set of Documents list; their own Status section
points to the parent instead.

Versions
--------
The site holds three kinds of pages (see README, "Releases"):

* ``/dev/<n>.html``: the editor's draft, built from ``content/`` on every run;
* ``/<version>/<n>.html``: frozen release snapshots, copied verbatim from
  ``releases/<version>/`` (they are produced once by ``release.sh``);
* ``/<n>.html``: a copy of the latest release (or of the draft, before the
  first release), so that "latest version" URLs never change.

Run with no arguments from the repository root to assemble the whole site in
``_site/``::

    python build.py

``release.sh`` builds the pages of a new release with::

    python build.py --version 0.1 --date 2026-10-19 --out build/0.1
"""

from __future__ import annotations

import argparse
import datetime
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
RELEASES_DIR = ROOT / "releases"

GITHUB_REPO = "w3c-facade-x/facade-x-specs"
# Public location of the site. Version links are absolute, so they work the
# same from the root, from a snapshot directory and from /dev/.
BASE_URL = "https://w3c-facade-x.github.io/facade-x-specs/"
RELEASE_NOTES_URL = f"https://github.com/{GITHUB_REPO}/releases/tag/v{{version}}"
SPEC_STATUS = "CG-DRAFT"
DEV = "dev"
VERSION_PATTERN = re.compile(r"^\d+(\.\d+)*$")
ISSUES_MARKER = re.compile(r'<!--\s*BUILD:ISSUES\s+label="(?P<label>[^"]+)"\s*-->')

# Static files copied verbatim into _site.
STATIC_FILES = ["model.png"]

# Placeholders in the shared template.
BODY_MARKER = "<!-- BUILD:CONTENT -->"
VERSION_CONFIG_MARKER = "{{VERSION_CONFIG}}"
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


def page_link(md_path: Path, fields: dict[str, str]) -> str:
    return f'<a href="{md_path.stem}.html">{htmllib.escape(plain(fields["title"]))}</a>'


def set_of_documents(pages, current: Path, current_fields: dict[str, str]) -> str:
    """HTML for the Set of Documents subsection of the current page.

    The list holds the pages without a ``parent``; the pages that name one of
    them as ``parent`` are listed under it. The current page is marked
    "(this document)"; a page with a ``parent`` also gets a sentence pointing
    to it.
    """
    members = [(p, f) for p, f, _ in pages if "parent" not in f]
    count = len(members)
    count_text = NUMBER_WORDS[count] if count < len(NUMBER_WORDS) else str(count)

    def item(md_path, fields):
        link = page_link(md_path, fields)
        return link + " (this document)" if md_path == current else link

    items = []
    for md_path, fields in members:
        children = [item(p, f) for p, f, _ in pages if f.get("parent") == md_path.stem]
        nested = ""
        if children:
            nested = ("\n      <ul>\n"
                      + "\n".join(f"        <li>{c}</li>" for c in children)
                      + "\n      </ul>\n    ")
        items.append(f"    <li>{item(md_path, fields)}{nested}</li>")
    if "parent" in current_fields:
        parent = next(((p, f) for p, f in members if p.stem == current_fields["parent"]), None)
        if parent is None:
            raise ValueError(f"{current.name}: parent {current_fields['parent']!r} "
                             "is not a page in the Set of Documents")
        intro = (f"This document is listed in {page_link(*parent)}, one of the "
                 f"{count_text} Fa&ccedil;ade-X specification documents produced by the "
                 "Data Fa&ccedil;ades Community Group:")
    else:
        intro = (f"This document is one of {count_text} Fa&ccedil;ade-X specification "
                 "documents produced by the Data Fa&ccedil;ades Community Group:")
    return (
        '\n<section id="set-of-documents">\n'
        "  <h3>Set of Documents</h3>\n"
        f"  <p>{intro}</p>\n"
        "  <ol>\n" + "\n".join(items) + "\n  </ol>\n"
        "</section>\n"
    )

def add_to_sotd(text: str, first: str, last: str) -> str:
    """Put ``first`` at the start and ``last`` at the end of the Status of This
    Document section, creating the section if absent."""
    match = SOTD_OPEN.search(text)
    if not match:
        return f'<section id="sotd">\n{first}\n{last}\n</section>\n\n' + text
    close = text.index("</section>", match.end())
    return (text[:match.end()] + "\n" + first + "\n" + text[match.end():close]
            + last + "\n" + text[close:])


# --------------------------------------------------------------------------
# Versions
# --------------------------------------------------------------------------

def version_key(version: str) -> tuple[int, ...]:
    """Sort key for version numbers: "0.10" comes after "0.9"."""
    return tuple(int(part) for part in version.split("."))


def released_versions() -> list[str]:
    """Versions with a snapshot under releases/, oldest first."""
    if not RELEASES_DIR.is_dir():
        return []
    found = [d.name for d in RELEASES_DIR.iterdir()
             if d.is_dir() and VERSION_PATTERN.match(d.name)]
    return sorted(found, key=version_key)


def in_release(version: str, stem: str) -> bool:
    return (RELEASES_DIR / version / f"{stem}.html").exists()


def version_links(stem: str, version: str) -> dict:
    """URLs of the other versions of page ``stem``, seen from ``version``.

    * latest: the stable root URL. From the draft, only if the latest release
      has the page; a release always links it, as it is (or was) the latest.
    * draft: the editor's draft.
    * previous: the newest older release that has the page (releases only).
    """
    released = [v for v in released_versions() if v != version]
    latest = None
    if version != DEV or (released and in_release(released[-1], stem)):
        latest = f"{BASE_URL}{stem}.html"
    previous = None
    if version != DEV:
        older = [v for v in released
                 if version_key(v) < version_key(version) and in_release(v, stem)]
        if older:
            previous = f"{BASE_URL}{older[-1]}/{stem}.html"
    return {
        "latest": latest,
        "latest_version": released[-1] if released else None,
        "draft": f"{BASE_URL}{DEV}/{stem}.html",
        "previous": previous,
    }


def respec_version_config(stem: str, version: str, date: str | None) -> str:
    """ReSpec configuration entries that depend on the version being built."""
    links = version_links(stem, version)
    config = {
        "specStatus": SPEC_STATUS,
        "isPreview": version == DEV,
        "edDraftURI": links["draft"],
    }
    if links["latest"]:
        config["latestVersion"] = links["latest"]
    if links["previous"]:
        config["prevVersion"] = links["previous"]
    if version != DEV:
        config["publishDate"] = date
    return "\n      ".join(f"{k}: {json.dumps(v)}," for k, v in config.items())


def versions_paragraph(stem: str, version: str, date: str | None) -> str:
    """Opening paragraph of the Status section: which version this is and
    where the other versions are."""
    links = version_links(stem, version)

    def a(url: str, text: str | None = None) -> str:
        return f'<a href="{url}">{text or url}</a>'

    if version == DEV:
        parts = ["This is the editor's draft of this document. It changes with "
                 "every update to the specification sources and is not a stable "
                 "release."]
        if links["latest"]:
            parts.append(f"The latest release, version {links['latest_version']}, "
                         f"is at {a(links['latest'])}.")
    else:
        this = f"{BASE_URL}{version}/{stem}.html"
        parts = [f"This is version {version} of this document, released on {date}, "
                 f"at {a(this)}. This version will not change.",
                 f"The latest release is always at {a(links['latest'])}.",
                 "The editor's draft, which may include changes made after this "
                 f"release, is at {a(links['draft'])}."]
        if links["previous"]:
            parts.append(f"The previous release is at {a(links['previous'])}.")
        parts.append("The issues addressed in this release, and those still open, "
                     "are listed in the "
                     + a(RELEASE_NOTES_URL.format(version=version), "release notes")
                     + ".")
    return '<p id="versions">' + " ".join(parts) + "</p>"


# --------------------------------------------------------------------------
# Building
# --------------------------------------------------------------------------

def build_page(md_path: Path, fields: dict[str, str], text: str, template: str,
               pages, out_dir: Path, version: str, date: str | None) -> None:
    stem = md_path.stem
    text = add_to_sotd(text, versions_paragraph(stem, version, date),
                       set_of_documents(pages, md_path, fields))
    plain_title = plain(fields["title"])
    result = (
        template.replace("{{PLAIN_TITLE}}", htmllib.escape(plain_title))
        .replace("{{TITLE}}", fields["title"])
        .replace("{{SUBTITLE}}", fields["subtitle"])
        .replace("{{VERSION}}", version)
        .replace(VERSION_CONFIG_MARKER, respec_version_config(stem, version, date))
        .replace(BODY_MARKER, render_markdown(text))
    )
    (out_dir / f"{stem}.html").write_text(result, encoding="utf-8")
    print(f"  built {out_dir.name}/{stem}.html")


def copy_static(out_dir: Path) -> None:
    for name in STATIC_FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, out_dir / name)
            print(f"  copied {name}")
        else:
            print(f"  (skipped missing static file {name})")


def build_docs(out_dir: Path, version: str, date: str | None) -> None:
    """Render every content page for ``version`` into ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    if VERSION_CONFIG_MARKER not in template:
        raise ValueError(f"{TEMPLATE_PATH.name} lacks {VERSION_CONFIG_MARKER}")
    pages = collect_pages()
    for md_path, fields, text in pages:
        build_page(md_path, fields, text, template, pages, out_dir, version, date)
    copy_static(out_dir)


def copy_files(src: Path, dst: Path) -> None:
    """Copy the files directly inside ``src`` (not subdirectories) into ``dst``."""
    for f in src.iterdir():
        if f.is_file():
            shutil.copy2(f, dst / f.name)


def build_site() -> None:
    """Assemble _site/: the draft, the snapshots, the root and versions.json."""
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    print(f"Building Façade-X specs into {OUTPUT_DIR.relative_to(ROOT)}/")

    # Editor's draft, from content/.
    build_docs(OUTPUT_DIR / DEV, DEV, None)

    # Release snapshots, verbatim.
    released = released_versions()
    for version in released:
        shutil.copytree(RELEASES_DIR / version, OUTPUT_DIR / version)
        print(f"  copied release {version}")

    # Root: the latest release, or the draft until there is one.
    latest = released[-1] if released else None
    copy_files(RELEASES_DIR / latest if latest else OUTPUT_DIR / DEV, OUTPUT_DIR)
    print(f"  root serves {'release ' + latest if latest else 'the editor’s draft'}")

    # Read by the banner that older snapshots show when a newer release exists.
    (OUTPUT_DIR / "versions.json").write_text(
        json.dumps({"latest": latest, "versions": released}, indent=2) + "\n",
        encoding="utf-8")


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

def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Façade-X specifications (see the module docstring).")
    parser.add_argument("--version", default=DEV,
                        help="build the pages of this release (e.g. 0.1); omit to "
                             "assemble the whole site in _site/")
    parser.add_argument("--date", default=datetime.date.today().isoformat(),
                        help="release date, YYYY-MM-DD (default: today)")
    parser.add_argument("--out", type=Path,
                        help="output directory of a release (default: build/<version>)")
    args = parser.parse_args(argv)
    if args.version == DEV:
        if args.out:
            parser.error("--out is only used with --version")
    else:
        if not VERSION_PATTERN.match(args.version):
            parser.error(f"invalid version {args.version!r}: use numbers like 0.1")
        try:
            datetime.date.fromisoformat(args.date)
        except ValueError:
            parser.error(f"invalid date {args.date!r}: use YYYY-MM-DD")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.version == DEV:
        build_site()
    else:
        out_dir = (args.out or ROOT / "build" / args.version).resolve()
        print(f"Building release {args.version} into {out_dir}")
        build_docs(out_dir, args.version, args.date)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())