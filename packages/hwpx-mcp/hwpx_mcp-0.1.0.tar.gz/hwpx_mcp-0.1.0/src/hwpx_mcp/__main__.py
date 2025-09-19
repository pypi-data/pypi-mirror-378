"""Allow running the CLI via ``python -m hwpx_mcp`` or bundled zipapps."""

from __future__ import annotations

from .cli import app


def main() -> None:
    """Entry point that defers to the Typer application."""

    app()


if __name__ == "__main__":
    main()
