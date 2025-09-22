#!/usr/bin/env python3
"""
Simple hello world example for Contexter testing.
"""


def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"


def main():
    """Main entry point."""
    print(greet("World"))


if __name__ == "__main__":
    main()
