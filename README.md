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

## Releases

The site publishes three kinds of pages:

| URL                      | Content                               | Source                                            |
| ------------------------ | ------------------------------------- | ------------------------------------------------- |
| `/<page>.html`           | Latest release (default landing page) | copy of `releases/<latest>/`                      |
| `/<version>/<page>.html` | Frozen release snapshot               | `releases/<version>/`                             |
| `/dev/<page>.html`       | Editor's draft                        | `content/`, rebuilt by CI on every push to `main` |

Each page links to its own version, the latest release and the editor's draft.
Before the first release, the root serves the editor's draft.

Snapshots under `releases/` are static HTML, exported once with ReSpec at
release time. Never edit them: corrections go into a new release.

### Making a release

Requirements: Python with `requirements.txt`, Node.js (`npx`), and the
[GitHub CLI](https://cli.github.com/), logged in with `gh auth login`.

1. Assign the issues of the release to the milestone `Version <version>`
   (e.g. `Version 0.1`), and close those that are resolved.
2. Prepare the draft (the date is the one printed in the documents; default today):

```bash
   ./release.sh draft 0.1 2026-10-19
```

   The script builds the pages, exports them to `releases/0.1/`, pushes them
   on the branch `release/0.1`, opens the pull request "Release 0.1", and
   creates a draft GitHub release `v0.1` whose notes list the closed and open
   issues of the milestone. ReSpec errors stop the export.
3. Review: CG participants comment on the pull request (a preview link is in
   its description). Complete the `<!-- … -->` placeholders in the draft
   release notes.
4. After the CG decision, merge the pull request. CI publishes the release at
   `/0.1/` and at the root.
5. Publish the release, which creates the tag `v0.1` on the merge commit:

```bash
   ./release.sh publish 0.1
```

6. Close the milestone and move any open issues to the next one.

To redo a draft, delete its pull request, branch and draft release, then run
`draft` again.