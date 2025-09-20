"""Utility functions for the aii package."""

import os


def debug_print(message: str) -> None:
    """Print debug message only if AII_DEBUG=true is set."""
    if os.environ.get("AII_DEBUG", "").lower() == "true":
        print(f"DEBUG: {message}")
