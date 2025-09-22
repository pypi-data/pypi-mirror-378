from __future__ import annotations
from pathlib import Path
import json
from contexter.utils.files import write_text, sha256_text


def build_manifest(
    cfg: dict,
    files_meta: list[dict],
    slices: list[dict],
    mode: str,
    branch: str,
    commit: str,
    out_path: Path,
) -> dict:
    """Build and write manifest.json with run metadata and file/slice information."""
    domains = cfg.get("domains", {})
    manifest = {
        "run": {
            "ts": cfg.get("_now"),
            "commit": commit,
            "branch": branch,
            "token_budget": int(cfg["budgets"]["token_limit"]),
            "mode": mode,
            "domains": domains,
        },
        "files": files_meta,
        "slices": [
            {
                k: s[k]
                for k in (
                    "id",
                    "path",
                    "lang",
                    "file_sha",
                    "start",
                    "end",
                    "kind",
                    "slice_sha",
                    "approx_tokens",
                )
            }
            for s in slices
        ],
        "packs": {
            "output": (
                ["contexter/pack/INDEX.md"]
                + [f"contexter/pack/domain-{name}.md" for name in domains.keys()]
                if domains
                else ["contexter/pack/CONTEXTPACK.md"]
            )
        },
    }

    # Compute manifest hash for reproducibility
    stable = json.dumps(
        {
            "run": manifest["run"],
            "files": [
                {"path": f["path"], "sha256": f["sha256"], "lines": f["lines"]}
                for f in files_meta
            ],
            "slices": [
                {"id": s["id"], "slice_sha": s["slice_sha"]} for s in manifest["slices"]
            ],
        },
        separators=(",", ":"),
        sort_keys=True,
    )

    manifest["run"]["manifest_hash"] = sha256_text(stable)
    write_text(out_path, json.dumps(manifest, indent=2))
    return manifest
