from __future__ import annotations
from pathlib import Path
from typing import Iterable
from contexter.utils.files import (
    read_text,
    write_text,
    sha256_file,
    sha256_text,
    fnmatch_any,
)

LANG_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".h": "c",
    ".cu": "cuda",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".rs": "rust",
    ".php": "php",
}


def lang_of(path: Path) -> str:
    """Determine language from file extension."""
    return LANG_MAP.get(path.suffix.lower(), "")


def discover_files(deny: list[str], allow: list[str]) -> list[Path]:
    """Discover files matching allow patterns, excluding deny patterns."""
    out = []
    for p in Path(".").rglob("*"):
        if not p.is_file():
            continue
        rp = str(p.relative_to(Path("."))).replace("\\", "/")
        if rp.startswith("contexter/") or rp in {"CONTEXTER.yaml", "PLAN.md", "ctx.py"}:
            continue
        if fnmatch_any(rp, deny):
            continue
        if any(fnmatch_any(rp, [pat]) for pat in allow):
            out.append(p)
    return out


def slice_ranges(n: int, max_lines=180, tail=40):
    """Return deterministic head/mid/tail ranges for file slicing."""
    if n <= 0:
        return []
    if n <= max_lines:
        return [("head", 1, n)]

    head_end = max(1, min(n, max_lines - tail))
    tail_start = max(1, n - tail + 1)
    mid_size = max(24, min(120, (max_lines - tail) // 2))
    mid_start = max(1, (n // 2) - (mid_size // 2))
    mid_end = min(n, mid_start + mid_size - 1)

    # Unique + sorted
    seen = set()
    out = []
    for kind, a, b in [
        ("head", 1, head_end),
        ("mid", mid_start, mid_end),
        ("tail", tail_start, n),
    ]:
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        out.append((kind, a, b))

    out.sort(key=lambda x: (x[1], x[2]))
    return out


def collect_slices(
    files: list[Path], per_file_max: int, per_file_tail: int, slice_dir: Path
):
    """Collect slices from files and write to slice directory."""
    slice_dir.mkdir(parents=True, exist_ok=True)
    slice_records = []
    files_meta = []
    total_chars = 0

    for fp in files:
        rp = str(fp.relative_to(Path("."))).replace("\\", "/")
        text = read_text(fp)
        total_chars += len(text)
        lines = text.splitlines()
        n = len(lines)
        file_sha = sha256_file(fp)
        lang = lang_of(fp)

        per = []
        for kind, start, end in slice_ranges(n, per_file_max, per_file_tail):
            data = "\n".join(lines[start - 1 : end])
            sid = sha256_text(f"{rp}:{start}-{end}:{file_sha}")[:16]
            write_text(
                slice_dir / f"{sid}.md",
                f"# path: {rp}\n# sha256: {file_sha}\n# lines: {start}-{end}\n{data}\n",
            )
            approx = max(1, len(data) // 4)
            slice_records.append(
                {
                    "id": sid,
                    "path": rp,
                    "lang": lang,
                    "file_sha": file_sha,
                    "start": start,
                    "end": end,
                    "kind": kind,
                    "slice_sha": sha256_text(data),
                    "approx_tokens": approx,
                }
            )
            per.append(
                {"id": sid, "start": start, "end": end, "sha256": sha256_text(data)}
            )

        files_meta.append(
            {
                "path": rp,
                "lang": lang,
                "sha256": file_sha,
                "size_bytes": fp.stat().st_size,
                "lines": n,
                "approx_tokens": max(1, len(text) // 4),
                "slices": per,
            }
        )

    return slice_records, files_meta, total_chars


def enforce_global_budget(slices: list[dict], token_limit: int, fraction: float):
    """Enforce global token budget by trimming slices."""
    budget = int(token_limit * max(0.05, min(0.95, fraction)))
    current = sum(s["approx_tokens"] for s in slices)
    if current <= budget:
        return slices, {"budget": budget, "trimmed": 0}

    def drop(kinds: set[str]):
        nonlocal slices, current
        kept = []
        removed = 0
        for s in slices:
            if current > budget and s["kind"] in kinds:
                current -= s["approx_tokens"]
                removed += s["approx_tokens"]
            else:
                kept.append(s)
        slices = kept
        return removed

    trimmed = 0
    trimmed += drop({"mid"})
    if current > budget:
        trimmed += drop({"tail"})
    if current > budget:
        trimmed += drop({"head"})

    return slices, {"budget": budget, "trimmed": trimmed}
