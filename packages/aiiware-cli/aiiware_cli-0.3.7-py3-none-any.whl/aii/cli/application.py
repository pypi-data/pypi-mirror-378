"""Main CLI application for aii."""

import sys

from ..application import AiiApplication


def main() -> int:
    """Application entry point."""
    try:
        app = AiiApplication()
        return app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 130
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


def main_translate() -> int:
    """Entry point for aiit command (translation shortcut)."""
    try:
        # Insert -t at the beginning of arguments
        sys.argv.insert(1, "-t")
        app = AiiApplication()
        return app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 130
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1
