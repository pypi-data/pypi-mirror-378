from __future__ import annotations
from pathlib import Path
import yaml

DEFAULTS = {
    "policy": {
        "no_code_edits": True,
        "secret_scrub": True,
        "abstention": "Correct > Abstain >> Confidently wrong",
    },
    "budgets": {"token_limit": 200000, "slice_fraction": 0.5},
    "prompt": {"base": "", "addons": {}},
    "dependency_kinds": ["import", "http", "db", "queue"],
    "languages": [
        "python",
        "javascript",
        "typescript",
        "cpp",
        "cuda",
        "go",
        "java",
        "rust",
    ],
    "domains": {},
}


def load_config(path: str | None) -> dict:
    """Load and validate CONTEXTER.yaml configuration with defaults."""
    p = Path(path) if path else Path("CONTEXTER.yaml")
    if not p.exists():
        raise FileNotFoundError(
            "CONTEXTER.yaml missing (use `contexter init` to scaffold)"
        )

    try:
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as e:
        raise ValueError(f"Invalid YAML in {p}: {e}") from e

    # Merge defaults shallowly
    out = DEFAULTS | cfg
    out["policy"] = DEFAULTS["policy"] | cfg.get("policy", {})
    out["budgets"] = DEFAULTS["budgets"] | cfg.get("budgets", {})

    pr = cfg.get("prompt", {})
    out["prompt"] = {"base": pr.get("base", ""), "addons": pr.get("addons", {})}

    if not isinstance(out.get("domains", {}), dict):
        out["domains"] = {}

    # Sanity checks
    tl = int(out["budgets"]["token_limit"])
    sf = float(out["budgets"]["slice_fraction"])
    if not (0.05 <= sf <= 0.95):
        out["budgets"]["slice_fraction"] = 0.5

    return out
