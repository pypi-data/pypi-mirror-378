from __future__ import annotations
from contexter.utils.files import write_text


def build_master_prompt(cfg: dict, manifest: dict) -> str:
    """Build master prompt for Codex from configuration and manifest."""
    lines = []
    lines.append(
        "Plan mode. Read contexter/.manifest.json and the slice files in contexter/.slices/."
    )
    lines.append("Never edit source code; only write to contexter/pack/ and PLAN.md.")

    if manifest["run"]["mode"] == "chaptered":
        lines.append(
            "Since domains exist, produce: INDEX.md + one domain-<slug>.md per domain with internal deps and cross-domain notes."
        )
    else:
        lines.append("Produce a single CONTEXTPACK.md.")

    base = cfg.get("prompt", {}).get("base", "").strip()
    addons = cfg.get("prompt", {}).get("addons", {})

    if base:
        lines.append(base)

    if cfg.get("domains"):
        ad = addons.get("domains", "").strip()
        if ad:
            lines.append(ad)

    for key in ("ast_snippets", "diagrams"):
        ad = addons.get(key, "").strip()
        if ad:
            lines.append(ad)

    lines.append(f"Kinds: {', '.join(cfg.get('dependency_kinds', []))}")
    lines.append(f"Languages: {', '.join(cfg.get('languages', []))}")
    lines.append(f"Budget: {manifest['run']['token_budget']} tokens.")
    lines.append(f"Manifest hash: {manifest['run']['manifest_hash']}")
    lines.append(
        "Freshness: ensure packs reflect the latest commit; if stale, rewrite packs."
    )
    lines.append(
        "Abstention: prepend QUESTIONS to PLAN.md and stop on uncertainty (e.g., invalid slice hash)."
    )
    lines.append("Scrub secrets (keys/tokens) in outputs.")
    lines.append(
        "Output:\n  - contexter/pack/CONTEXTPACK.md (single) OR\n  - contexter/pack/INDEX.md + contexter/pack/domain-<slug>.md (chaptered)\n  - PLAN.md (append PROGRESS; prepend QUESTIONS when needed)"
    )

    return "\n".join(lines)
