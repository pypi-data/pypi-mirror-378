# pr-doc-sync (prdoc)

> Keep your docs in lockstep with your code.

`prdoc` is a CLI + GitHub Action that detects **code→doc drift** in pull requests, proposes **Markdown patches** (via an LLM), and can **apply/commit** them automatically — so reviewers see doc updates alongside code changes.

- **Language-aware**: Python (`libcst`) + TypeScript/JavaScript (`ts-morph`) + plugin interface for more.
- **Docs-aware**: Locates & searches repo docs (`.md`, `.rst`, `.mdx`) to find the best spots to edit.
- **LLM-guarded**: Rate-limit + token-budget guard with clear, human-readable cost estimates.
- **Resilient**: Fallback heuristic patch when LLM is unavailable.
- **Pretty CLI**: Rich-styled output, progress bars, and a detailed `prdoc help`.

---

## Install

```bash
# Recommended
pipx install prdoc

# or
pip install prdoc
```

> Python **3.9+** required. For TypeScript symbol extraction, install **Node.js** and add `ts-morph` to your project:
>
> ```bash
> npm i -D ts-morph
> ```

---

## Quickstart

Show help:

```bash
prdoc help
```

Preview (read-only) suggested patches for a PR in CI:

```bash
# In GitHub Actions, with GITHUB_TOKEN available:
prdoc sync --pr 123 --dry-run --comment
```

Apply patches locally (non-interactive):

```bash
# Pipe the unified diff (from 'sync') into apply, or feed your own patch
prdoc apply --yes --commit-msg "docs: align with PR #123"
```

> If you’re testing locally without PR context, see **Local Dry Run** below.

---

## Configuration

You can configure via **CLI flags**, **env vars**, or **`.prdoc.yaml`**. Precedence (highest → lowest):

1. CLI flags
2. Real environment (shell/CI)
3. `.env` (auto-loaded)
4. `.prdoc.yaml`
5. Defaults

### Environment

```bash
# Required for GitHub API
export GITHUB_TOKEN=ghp_********************************

# Pick one LLM provider and key:
export OPENAI_API_KEY=sk-********************************
# or
export GROQ_API_KEY=gsk_********************************

# Optional: enable anonymous telemetry for this run
export PRDOC_TELEMETRY=1
```

### `.prdoc.yaml` (example)

```yaml
# Which LLM backend to use by default
provider: openai
model: gpt-5-thinking # or your preferred model id

# Glob patterns to find docs
docs:
  include:
    - "docs/**/*.md"
    - "README.md"
  exclude:
    - "docs/archive/**"

# Optional: vector index plugin (Chroma)
chroma:
  enabled: false
  persist_dir: .prdoc/chroma

# Logging
verbose: false
```

---

## Commands

### Global flags

```
--verbose / -v     Enable debug logging
--no-color         Disable ANSI colors
--telemetry/--no-telemetry  Opt in/out (for this run)
--version          Print version and exit
```

### `prdoc help [COMMAND]`

Pretty, sectioned help with examples.

```bash
prdoc help
prdoc help sync
prdoc help apply
prdoc help diagnose
prdoc help telemetry
```

### `prdoc sync`

Analyze a PR’s code changes, search docs, generate **unified diff** patches, and optionally post a summary comment (CI).

Common flags (some may be CI-only):

```
--pr <num>         Pull request number to analyze
--comment          Post a Markdown summary comment to the PR
--dry-run          Print patches to stdout (do not write)
--max-cost <USD>   Abort if estimated LLM spend exceeds this amount
```

**Local Dry Run (no PR context)**

If you just want to try the engine on a couple of doc files:

```bash
# Example: tell prdoc how to update specific docs (dry-run only)
prdoc sync -i "tighten intro and add usage example" -p README.md -p docs/guide.md -r openai -m gpt-5-thinking
```

> The local `-i/--instruction` + `-p/--path` flow is perfect for quick experiments. In CI you’ll typically use `--pr` so prdoc reads diff + doc candidates automatically.

### `prdoc apply`

Read a unified diff from **STDIN**, apply via `git apply -p0`, **commit**, and **push**.

```
--yes              Non-interactive (no confirmation)
--commit-msg/-m    Commit message to use
--branch <name>    Target branch (optional, will push current HEAD if omitted)
```

Example:

```bash
# From a file:
cat patch.diff | prdoc apply --yes -m "docs: synchronize with PR #123"

# From sync output:
prdoc sync --pr 123 --dry-run | prdoc apply --yes
```

### `prdoc diagnose`

Pretty environment check: tokens, Node.js/ts-morph presence, versions, and quick tips.

```bash
prdoc diagnose
```

---

## Features (what happens under the hood)

- **Diff parsing**: Reads the PR’s diff to identify changed symbols and files.
- **Symbol extractors**:
  - **Python** via `libcst` (functions, classes, methods, signatures).
  - **TS/JS** via `ts-morph` (`node` child process; installed in your repo).
  - **Plugin interface** (entry points) for community extractors and indexers.
- **Doc discovery & search**:
  - Glob scans for docs; simple trigram index for fuzzy search.
  - Optional Chroma vector index plugin (for larger repos).
- **Patch generation**:
  - Prompt templates (Jinja) craft “diff → doc patch” instructions.
  - LLM client abstraction with retries and provider swapping (OpenAI/Groq).
- **Resilience**:
  - **LLM guard**: rate-limit + token-budget checks with cost estimation.
  - **Fallback heuristic**: returns a simple search-replace style diff when offline.
- **CI-friendly**:
  - Composite Action wrapper (comment-only mode).
  - Bot comment renderer (clean, non-intrusive PR summary).

---

## GitHub Actions (minimal)

```yaml
name: prdoc
on:
  pull_request:
    branches: [main]
jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pipx install prdoc
      - env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }} # or GROQ_API_KEY
        run: |
          prdoc sync --pr ${{ github.event.pull_request.number }} --comment --dry-run
```

> For full automation, run `prdoc apply --yes` in a separate job/PR after reviewers accept the patch.

---

## TypeScript/JavaScript support

- Requires **Node.js** and a **local dev dependency** on `ts-morph` (so your repo controls the exact version).
- prdoc will detect `node` and `ts-morph` automatically (`prdoc diagnose` to verify).
- Symbol extraction provides function/class/variable identifiers used to target doc snippets.

---

## Telemetry (opt-in)

Anonymous, minimal counts + timings only (no code, no docs, no repo names). Helps us prioritize performance and UX.

Enable for a run:

```bash
prdoc sync --telemetry --pr 123
```

Disable explicitly:

```bash
prdoc sync --no-telemetry --pr 123
```

Or set via env:

```bash
export PRDOC_TELEMETRY=1
```

---

## Troubleshooting

- **No patches suggested**  
  The change may not touch public symbols or documented sections. Try `--verbose` and confirm docs are matched by your `docs.include` globs.

- **Git apply failed**  
  Ensure the patch headers match repo paths. prdoc uses `git apply -p0` (no `a/` `b/` prefixes). If your patch has prefixes, re-generate without them.

- **TypeScript extractor not working**  
  Run `prdoc diagnose`. You need `node` on PATH and `ts-morph` in your project (`npm i -D ts-morph`).

- **Budget exceeded / rate limited**  
  Lower `--max-cost`, pick a cheaper model, or reduce the number of candidate docs (narrow `docs.include`).

---

## Versioning & Release

- Semantic Versioning.
- PyPI releases are built with Poetry and published via GitHub Actions (PyPI **Trusted Publisher** / OIDC).

---

## Contributing

- Issues & PRs welcome!
- Plugin authors: expose entry points under:
  - `prdoc.symbol_extractor`
  - `prdoc.doc_indexer`

---

## License

MIT © Bethvour
