# Contexter — Prompt-First, Codex-Only Context Packs

**Author:** Gudjon Mar Gudjonsson  
**License:** MIT

## Overview

Contexter is a **prompt-first** toolkit that lets **GPT-5 Codex** build and maintain compact, navigable **Markdown context packs** for your repository. Python does deterministic prep (globs, SHA, exact slices, manifest, prompt); **Codex** does judgment (chapters, AST snippets, diagrams, metadata, freshness, tasks). No source edits, ever.

## Quick Start

```bash
# Install
pip install contexter-codex

# Initialize repository
contexter init

# Generate context pack
contexter run
# Paste prompt into Codex and approve writes
```

## How It Works

### One command → master prompt → Codex builds packs

```
+-----------+        contexter run        +------------------+
| CONTEXTER |  ========================>  |   Codex (GPT-5)   |
|  .yaml    |      (master prompt)        |  plan→exec→sync   |
+-----------+                             +------------------+
         |                                        |
         | writes                                 | writes
         | PLAN.md (PROGRESS/QUESTIONS)          | contexter/pack/*.md
         v                                        v
   +----+-----------------------------------------------+
   |                 Documentation output               |
   |   CONTEXTPACK.md  |  INDEX.md  |  domain-*.md      |
   +----------------------------------------------------+
```

- **Single-pack mode**: `CONTEXTPACK.md` with overview, deps, platform metadata, files with anchors + AST-selected snippets, metrics & freshness, plus ASCII/Mermaid diagrams.
- **Chaptered mode** (if `domains:` provided): `INDEX.md` + `domain-*.md` packs with internal deps & cross-domain notes.

## Features

- **Domain chapters** via `domains:` → `INDEX.md` + `domain-*.md` (reduce truncation, improve navigation)
- **AST-aware snippets** → function/class excerpts with Lx–Ly anchors
- **Deps graph** (import/http/db/queue) with low noise
- **Platform metadata** → env keys, package versions, compose services, SQL DDL paths
- **ASCII & Mermaid diagrams** for human scan without leaving Markdown
- **Abstention > guessing** → QUESTIONS in `PLAN.md` when unsure
- **Guardrails by design** → never touch source; only `/contexter/pack/` + `PLAN.md`

## Installation

```bash
pip install contexter-codex
```

## Usage

### Initialize Repository

```bash
contexter init
```

This creates:
- `CONTEXTER.yaml` - Configuration file
- `PLAN.md` - Progress tracking
- `.gitignore` - Ignores generated files
- `.github/workflows/contexter.yml` - CI integration

### Generate Context Pack

```bash
contexter run
```

This:
1. Discovers files in your repository
2. Creates deterministic slices with SHA-256 hashes
3. Enforces global token budget
4. Generates manifest and master prompt
5. Copies prompt to clipboard (if supported)

### CLI Commands

- `contexter run` - Generate context pack
- `contexter init` - Initialize repository
- `contexter version` - Show version
- `contexter config` - Show configuration

## Configuration

Edit `CONTEXTER.yaml` to customize:

```yaml
policy:
  no_code_edits: true
  abstention: "Correct > Abstain >> Confidently wrong"
  secret_scrub: true

budgets:
  token_limit: 200000
  slice_fraction: 0.5

prompt:
  base: |
    You are Codex in plan mode. Build and maintain a Markdown "context pack" for this repository.
    Never edit source code; write only to contexter/pack/ and PLAN.md.

domains:
  core:
    - "src/core/**"
  api:
    - "src/api/**"

dependency_kinds: ["import", "http", "db", "queue"]
languages: ["python", "javascript", "typescript", "cpp", "cuda", "go", "java", "rust"]
```

## Development

```bash
# Clone and setup
git clone https://github.com/org/contexter-dev.git
cd contexter-dev
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
flake8 .
mypy .
```

## License

MIT © Gudjon Mar Gudjonsson
