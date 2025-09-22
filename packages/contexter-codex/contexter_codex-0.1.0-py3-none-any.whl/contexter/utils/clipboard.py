from __future__ import annotations
import subprocess
import shutil


def copy(text: str) -> bool:
    """Copy text to clipboard using platform-specific tools."""
    try:
        if shutil.which("pbcopy"):  # macOS
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
            return True
        if shutil.which("xclip"):  # Linux
            p = subprocess.Popen(
                ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE
            )
            p.communicate(input=text.encode("utf-8"))
            return True
        if shutil.which("wl-copy"):  # Wayland
            p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
            return True
        return False
    except Exception:
        return False
