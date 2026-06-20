# facade-x-specs

Repository for the specification of the Façade-X metamodel.

## Editing workflow

Editable content lives in Markdown under [`content/`](content/). The ReSpec
scaffolding (configuration, MathJax/Turtle setup, styles, `<head>`) lives in
HTML templates under [`templates/`](templates/). A build step renders the
Markdown into the templates and writes the finished documents into `_site/`,
which is what gets published.

`_site/` is **generated output** — it is git-ignored and produced by the build,
either locally or by CI. Don't edit it by hand.

| Page                     | Edit this                | Template                  | Output (generated)     |
| ------------------------ | ------------------------ | ------------------------- | ---------------------- |
| Specifications overview  | `content/index.md`       | `templates/index.html`    | `_site/index.html`     |
| Concepts and metamodel   | `content/metamodel.md`   | `templates/metamodel.html`| `_site/metamodel.html` |
| RDF vocabulary           | `content/rdf.md`         | `templates/rdf.html`      | `_site/rdf.html`       |

To change the **substance** of a spec, edit the Markdown in `content/`.
To change the **ReSpec configuration, styles, or scripts**, edit the matching
template in `templates/`.

### Authoring notes

- Prose is ordinary Markdown. You can freely mix in raw HTML (tables, term
  blocks, figures) where the structure calls for it — Markdown inside
  `<section>` and `<div>` wrappers is parsed automatically.
- First-order-logic axioms (metamodel) go in fenced ` ```math ` blocks. Each is
  emitted as a bare `<pre>` so the page's MathJax script renders it.
- The Manchester-syntax block is kept as a raw `<pre data-nomath class="example">`
  so MathJax leaves it alone.
- Static assets (e.g. `model.png`) referenced by the specs are copied into
  `_site/` by the build; add new ones to `STATIC_FILES` in `build.py`.

## Building locally

```bash
pip install -r requirements.txt
python build.py
```

Then open the files in `_site/` (e.g. with a local web server) to preview.

## Continuous deployment

The [`Build and deploy specs`](.github/workflows/build.yml) GitHub Action runs
`build.py` on every push to `main` and publishes the generated `_site/` to
GitHub Pages — the build output is never committed back to the repository.
Pull requests build the site as a check but do not deploy.

To enable this, set the repository's **Settings → Pages → Build and deployment
→ Source** to **GitHub Actions** (one-time setup).
