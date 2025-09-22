from contexter.core.slicer import slice_ranges


def test_slice_ranges_small():
    """Test slicing for small files."""
    assert slice_ranges(10) == [("head", 1, 10)]


def test_slice_ranges_large():
    """Test slicing for large files."""
    out = slice_ranges(1000, max_lines=180, tail=40)
    kinds = [k for k, _, _ in out]
    assert set(kinds) == {"head", "mid", "tail"}


def test_slice_ranges_empty():
    """Test slicing for empty files."""
    assert slice_ranges(0) == []
