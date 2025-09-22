from __future__ import annotations
import subprocess


def branch_commit() -> tuple[str, str]:
    """Get current git branch and commit hash."""
    try:
        b = (
            subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                text=True,
                capture_output=True,
            ).stdout.strip()
            or "unknown"
        )

        c = (
            subprocess.run(
                ["git", "rev-parse", "HEAD"], text=True, capture_output=True
            ).stdout.strip()
            or "unknown"
        )

        return b, c
    except Exception:
        return "unknown", "unknown"
