#!/bin/bash
# Release workflow for the Façade-X specifications (see README, "Releases").
#
#   ./release.sh draft 0.1 [YYYY-MM-DD]   prepare release 0.1 for CG review
#   ./release.sh publish 0.1              publish it, once the CG has approved
#
# draft:   builds the pages of the release, freezes them as static HTML in
#          releases/<version>/, commits them on a branch release/<version>,
#          opens a pull request for review and creates a *draft* GitHub release
#          whose notes list the issues of milestone "Version <version>".
#          The date is the one printed in the documents (default: today).
# publish: after the pull request is merged, publishes the draft release, which
#          creates the tag v<version> on the merge commit.
#
# Needs: git, python (pip install -r requirements.txt), node/npx (ReSpec
# export; the first run downloads ReSpec and a headless Chromium) and the
# GitHub CLI `gh`, logged in with `gh auth login`.

set -euo pipefail

REPO="w3c-facade-x/facade-x-specs"
SITE="https://w3c-facade-x.github.io/facade-x-specs"

STEP="${1:-}"
VERSION="${2:-}"
DATE="${3:-$(date +%F)}"

MILESTONE="Version $VERSION"   # GitHub milestone holding the release's issues
BRANCH="release/$VERSION"      # branch carrying the snapshot until approval
TAG="v$VERSION"                # created when the draft release is published
NOTES="build/RELEASE_NOTES-$VERSION.md"

die() { echo "error: $*" >&2; exit 1; }
usage() { sed -n '4,5p' "$0" | sed 's/^# *//' >&2; exit 1; }

[[ "$STEP" == draft || "$STEP" == publish ]] || usage
[[ "$VERSION" =~ ^[0-9]+(\.[0-9]+)*$ ]] || die "invalid version '$VERSION' (use e.g. 0.1)"
cd "$(dirname "$0")"

# List the issues of the milestone in one state, one Markdown line each.
milestone_issues() {
  gh issue list -R "$REPO" --milestone "$MILESTONE" --state "$1" --limit 500 \
    --json number,title --jq 'sort_by(.number)[] | "- #\(.number) \(.title)"'
}

draft() {
  for tool in git python npx gh; do
    command -v "$tool" >/dev/null || die "$tool not found"
  done
  [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || die "invalid date '$DATE'"
  [ -z "$(git status --porcelain)" ] || die "uncommitted changes; commit or stash them first"
  [ ! -e "releases/$VERSION" ] || die "releases/$VERSION already exists"
  if gh release view "$TAG" -R "$REPO" >/dev/null 2>&1; then
    die "a GitHub release $TAG already exists"
  fi

  # Start from the current main branch.
  git checkout -q main
  git pull -q --ff-only

  # 1. Issues of the milestone. Open ones do not block the draft, but are
  #    reported so that they can be closed, or moved to a later milestone.
  echo "Collecting issues of milestone \"$MILESTONE\"..."
  local closed open
  closed="$(milestone_issues closed)"
  open="$(milestone_issues open)"
  [ -n "$closed$open" ] || die "no issues found in milestone \"$MILESTONE\""
  if [ -n "$open" ]; then
    echo "warning: open issues in \"$MILESTONE\":" >&2
    echo "$open" >&2
  fi

  # 2. Release notes. The HTML comments are placeholders to complete in the
  #    draft release on GitHub before publishing it.
  mkdir -p build
  {
    echo "Version $VERSION of the Façade-X specifications, released on $DATE by the"
    echo "W3C Data Façades Community Group."
    echo
    echo "<!-- Summary of the release: what it contains, what changed. -->"
    echo "<!-- Link to the minutes of the CG decision. -->"
    echo
    echo "Documents: $SITE/$VERSION/"
    echo
    echo "## Issues addressed"
    echo
    echo "${closed:-None.}"
    echo
    echo "## Open issues"
    echo
    echo "<!-- Say whether these are deferred to a later release. -->"
    echo
    echo "${open:-None.}"
  } > "$NOTES"

  # 3. Build the pages of the release (versioned links, fixed date).
  rm -rf "build/$VERSION"
  python build.py --version "$VERSION" --date "$DATE" --out "build/$VERSION"

  # 4. Freeze each page as static HTML with the ReSpec command line tool: the
  #    snapshot no longer depends on the ReSpec version or on live GitHub data.
  #    --localhost serves build/<version>/ so that relative links and images
  #    resolve; --haltonerror stops on ReSpec errors.
  mkdir -p "releases/$VERSION"
  (
    cd "build/$VERSION"
    for page in *.html; do
      echo "  exporting $page"
      npx --yes respec --localhost --timeout 60 --haltonerror \
        "$page" "../../releases/$VERSION/$page"
    done
  ) || { rm -rf "releases/$VERSION"; die "ReSpec export failed"; }
  # Static assets (images etc.) go along unchanged.
  find "build/$VERSION" -maxdepth 1 -type f ! -name '*.html' \
    -exec cp {} "releases/$VERSION/" \;

  # 5. Commit the snapshot on its own branch: main, and so the published
  #    site, only gets it when the pull request is merged.
  git checkout -q -b "$BRANCH"
  git add "releases/$VERSION"
  git commit -q -m "Release $VERSION: snapshot of the specifications"
  git push -q -u origin "$BRANCH"

  # 6. Pull request, where the CG reviews and comments on the release.
  local preview="https://htmlpreview.github.io/?https://github.com/$REPO/blob/$BRANCH/releases/$VERSION/index.html"
  gh pr create -R "$REPO" --base main --head "$BRANCH" --title "Release $VERSION" \
    --body "Snapshot of the specifications for release $VERSION, dated $DATE.

Preview: $preview

Merging this pull request publishes the release on the site (root and /$VERSION/).
Merge only after the CG decision, then run \`./release.sh publish $VERSION\`.

Draft release notes: see the draft release $TAG."

  # 7. Draft GitHub release. Drafts are visible to maintainers only and
  #    create no tag until they are published.
  gh release create "$TAG" -R "$REPO" --draft --title "Version $VERSION" \
    --notes-file "$NOTES" --target "$BRANCH"

  git checkout -q main
  echo
  echo "Draft of release $VERSION ready:"
  echo "  - complete the notes of the draft release $TAG on GitHub (see the <!-- --> comments);"
  echo "  - after the CG decision, merge the pull request \"Release $VERSION\";"
  echo "  - then run: ./release.sh publish $VERSION"
}

publish() {
  command -v gh >/dev/null || die "gh not found"

  # The snapshot must be on main, through the merged pull request.
  local state merge
  state="$(gh pr view "$BRANCH" -R "$REPO" --json state --jq .state)"
  [ "$state" = MERGED ] || die "pull request for $BRANCH is $state; merge it first"
  merge="$(gh pr view "$BRANCH" -R "$REPO" --json mergeCommit --jq .mergeCommit.oid)"

  git checkout -q main
  git pull -q --ff-only
  [ -d "releases/$VERSION" ] || die "releases/$VERSION is not on main"

  # Publishing the draft creates tag v<version> on the merge commit.
  gh release edit "$TAG" -R "$REPO" --target "$merge" --draft=false
  # Separate call: GitHub refuses to mark a release as latest while it is a draft.
  gh release edit "$TAG" -R "$REPO" --latest
  git fetch -q --tags

  # The release branch is no longer needed.
  git push -q origin --delete "$BRANCH" 2>/dev/null || true
  git branch -q -D "$BRANCH" 2>/dev/null || true

  echo "Release $VERSION published: $SITE/$VERSION/ (tag $TAG)."
  echo "Remember to close the milestone \"$MILESTONE\" and to move any open issues."
}

"$STEP"