from contexter.core.config import load_config
import pytest
from pathlib import Path


def test_load_defaults(tmp_path: Path):
    """Test loading configuration with defaults."""
    p = tmp_path / "CONTEXTER.yaml"
    p.write_text("{}", encoding="utf-8")
    cfg = load_config(str(p))
    assert cfg["budgets"]["token_limit"] == 200000
    assert "prompt" in cfg


def test_load_missing_file():
    """Test error when CONTEXTER.yaml is missing."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")


def test_invalid_yaml(tmp_path: Path):
    """Test error with invalid YAML."""
    p = tmp_path / "CONTEXTER.yaml"
    p.write_text("invalid: yaml: [", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(str(p))
