# Python Basic Example

This is a simple Python project to demonstrate Contexter functionality.

## Files

- `hello.py` - Simple greeting functions
- `math.py` - Basic math utilities
- `README.md` - This file

## Testing Contexter

1. Initialize Contexter:
   ```bash
   contexter init
   ```

2. Generate context pack:
   ```bash
   contexter run
   ```

3. Paste the prompt into Codex and approve writes

## Expected Output

Contexter should generate:
- `contexter/.manifest.json` - File metadata
- `contexter/.slices/` - Code slices
- `contexter/.prompt.txt` - Master prompt
- `contexter/pack/CONTEXTPACK.md` - Context pack (after Codex processing)
