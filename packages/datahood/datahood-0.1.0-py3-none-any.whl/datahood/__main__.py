"""Entrypoint module for the datahoodpackage.

This module exposes a `main()` function used by the console script and
by `dh`. It intentionally keeps logic minimal and delegates
to the Typer application in :mod:`datahood.cli`.
"""

from datahood.cli import app


def main() -> None:
    """Invoke the command-line application.

    Typical use:

    ```bash
    dh transfer --source-uri ... --dest-uri ...
    ```
    """
    app()


if __name__ == "__main__":
    main()
