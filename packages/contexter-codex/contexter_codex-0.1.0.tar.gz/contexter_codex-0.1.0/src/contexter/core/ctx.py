from __future__ import annotations
from pathlib import Path
import time
from datetime import datetime
from contexter.core.config import load_config
from contexter.core.slicer import discover_files, collect_slices, enforce_global_budget
from contexter.core.manifest import build_manifest
from contexter.core.prompt import build_master_prompt
from contexter.utils.git import branch_commit
from contexter.utils.files import write_text
from contexter.utils.clipboard import copy as clip_copy


class ContexterCore:
    """Main orchestrator for Contexter operations."""

    def __init__(self, config_path: str | None, verbose: bool = False):
        self.config_path = config_path
        self.verbose = verbose
        self.root = Path(".")
        self.ctx = self.root / "contexter"
        self.slice_dir = self.ctx / ".slices"
        self.pack_dir = self.ctx / "pack"
        self.manifest = self.ctx / ".manifest.json"
        self.prompt = self.ctx / ".prompt.txt"
        self.plan = self.root / "PLAN.md"
        self.runlog = self.ctx / ".runlog.jsonl"

    def _ensure_plan(self):
        """Ensure PLAN.md exists with basic structure."""
        if not self.plan.exists():
            write_text(self.plan, "# PLAN\n\n## QUESTIONS\n\n## PROGRESS\n")

    def _progress(self, note: str):
        """Append progress note to PLAN.md."""
        with self.plan.open("a", encoding="utf-8") as f:
            f.write(f"\n## PROGRESS\n- {datetime.utcnow().isoformat()}Z: {note}\n")

    def run(self):
        """Main execution: load config, discover files, slice, budget, manifest, prompt."""
        t0 = time.time()
        cfg = load_config(self.config_path)
        cfg["_now"] = datetime.utcnow().isoformat() + "Z"
        self._ensure_plan()

        # File discovery
        deny = [
            "**/node_modules/**",
            "**/build/**",
            "**/.git/**",
            "**/.*/**",
            "**/*.png",
            "**/*.jpg",
            "**/*.jpeg",
            "**/*.gif",
            "**/*.mp4",
            "**/*.mov",
            "**/*.pt",
            "**/*.onnx",
            "**/*.ckpt",
            "**/*.bin",
            "**/*.pb",
            "**/*.so",
            "**/*.dylib",
            "**/*.a",
            "**/*.o",
        ]
        allow = ["**/*"]
        files = discover_files(deny, allow)

        # Slicing and budgeting
        per_file_max, per_file_tail = 180, 40
        slices, files_meta, _chars = collect_slices(
            files, per_file_max, per_file_tail, self.slice_dir
        )

        token_limit = int(cfg["budgets"]["token_limit"])
        fraction = float(cfg["budgets"]["slice_fraction"])
        slices, trim_info = enforce_global_budget(slices, token_limit, fraction)

        # Manifest and prompt
        b, c = branch_commit()
        mode = "chaptered" if cfg.get("domains") else "single"
        manifest = build_manifest(cfg, files_meta, slices, mode, b, c, self.manifest)

        prompt = build_master_prompt(cfg, manifest)
        write_text(self.prompt, prompt)
        clipped = clip_copy(prompt)

        # Progress logging
        note = (
            f"Prepared manifest ({len(files_meta)} files, {len(slices)} slices; "
            f"slice_budget={int(token_limit * fraction)} tok, trimmed≈{trim_info['trimmed']} tok). "
            f"Prompt saved to contexter/.prompt.txt"
        )
        if clipped:
            note += "; prompt copied to clipboard"
        self._progress(note)

        if self.verbose:
            print(prompt)

        print("\n=== Prompt written to contexter/.prompt.txt ===")
        if clipped:
            print(
                "Prompt also copied to clipboard. Paste into Codex and approve writes to contexter/pack/ and PLAN.md."
            )
        else:
            print(
                "Copy the prompt to Codex. Approve writes to contexter/pack/ and PLAN.md."
            )
        print(f"Run duration: {int((time.time() - t0) * 1000)} ms")
