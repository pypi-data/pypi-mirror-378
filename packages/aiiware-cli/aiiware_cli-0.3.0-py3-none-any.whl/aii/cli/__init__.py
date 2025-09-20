"""CLI package exports for entry points."""

from __future__ import annotations

__all__ = ["main", "main_translate"]


def main() -> int:
    """Lazy-load and invoke the primary CLI entry point."""
    from .application import main as _main

    return _main()


def main_translate() -> int:
    """Lazy-load and invoke the translation shortcut entry point."""
    from .application import main_translate as _main_translate

    return _main_translate()
