from __future__ import annotations
from pathlib import Path
import hashlib
from fnmatch import fnmatch as _fn


def read_text(p: Path) -> str:
    """Read text file with UTF-8 encoding, ignoring errors."""
    return p.read_text(encoding="utf-8", errors="ignore")


def write_text(p: Path, data: str) -> None:
    """Write text to file, creating parent directories if needed."""
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")


def sha256_file(p: Path) -> str:
    """Compute SHA-256 hash of file content."""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s: str) -> str:
    """Compute SHA-256 hash of text string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def fnmatch_any(path: str, patterns) -> bool:
    """Check if path matches any of the given patterns."""
    if not patterns:
        return False
    if isinstance(patterns, str):
        patterns = [patterns]
    return any(_fn(path, pat) for pat in patterns)
