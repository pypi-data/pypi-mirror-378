"""
Main CLI module for datahood.

This module aggregates commands from submodules and configures the top-level
Typer application.
"""

import typer

from datahood import __version__
from datahood.cli.export import transfer_app
from datahood.cli.help_text import CLICommands
from datahood.cli.schema import schema_app


# from datahood.cli.import_ import import_app


def version_callback(version: bool) -> None:
    """Show version information and exit."""
    if version:
        typer.echo(f"datahood {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="datahood",
    help=f"""
    📊 [bold blue]DataHood[/bold blue] - your friendly neighborhood data transfer tool

    [green]transfer[/green] Transfer data between MongoDB instances and BSON files
    [green]import[/green] Import data from various sources
    [green]schema[/green] Infer and generate Python types from your data

    [bold yellow]QUICK EXAMPLES[/bold yellow]
    [green]{CLICommands.TRANSFER_MONGO_TO_BSON.replace("dh ", "datahood ")}[/green]
    [green]{CLICommands.TRANSFER_BSON_TO_MONGO.replace("dh ", "datahood ")}[/green]
    [green]{CLICommands.SCHEMA_FROM_MONGO.replace("dh ", "datahood ")}[/green]
    [green]{CLICommands.SCHEMA_FROM_BSON.replace("dh ", "datahood ")}[/green]
    """,
)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Handle version option."""
    pass


# app.add_typer(import_app)
app.add_typer(transfer_app, name="transfer")
app.add_typer(schema_app, name="schema")
