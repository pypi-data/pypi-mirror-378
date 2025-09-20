"""Schema inference commands for generating Python types from data."""

import asyncio
from pathlib import Path

from rich.console import Console
import typer

from datahood.cli.help_text import CLICommands
from datahood.schema.gen.pydantic import PydanticGenerator
from datahood.schema.gen.typeddict import TypedDictGenerator
from datahood.schema.infer.factory import infer_schema_from


console = Console()


schema_app = typer.Typer(
    name="schema",
    help=f"""
    🧬 [bold blue]Schema Oracle[/bold blue] - data structures from real documents

    [green]from-mongo[/green]   Analyze MongoDB collections and generate Python types
    [green]from-bson[/green]    Infer schema from BSON files and create models

    [bold yellow]TYPE GENERATION EXAMPLES[/bold yellow]
    [green]{CLICommands.SCHEMA_FROM_MONGO_PYDANTIC}[/green]  # Generate Pydantic models
    [green]{CLICommands.SCHEMA_FROM_MONGO_TYPEDDICT}[/green]  # TypedDict (default)
    [green]{CLICommands.SCHEMA_FROM_BSON_DETAILED}[/green]

    [bold yellow]OUTPUT FORMATS[/bold yellow]
    [magenta]TypedDict[/magenta]     Lightweight typing (default) - pure Python 3.8+
    [magenta]Pydantic[/magenta]      Rich validation models - data validation & more

    [bold yellow]ANALYSIS FEATURES[/bold yellow]
    • Scans [cyan]sample documents[/cyan] to infer comprehensive schemas
    • Handles [cyan]nested objects[/cyan] and arrays with proper typing
    • Detects [cyan]optional fields[/cyan] and union types automatically
    • Generates [cyan]clean, readable code[/cyan] ready for production use
    """,
    rich_markup_mode="rich",
)


def get_generator(to_pydantic: bool) -> PydanticGenerator | TypedDictGenerator:
    """Return the appropriate generator based on the output format requested.

    Args:
        to_pydantic: If True, returns PydanticGenerator,
                    else returns TypedDictGenerator.
    """
    if to_pydantic:
        return PydanticGenerator()
    return TypedDictGenerator()


# Common Typer options for schema commands
OUTPUT_OPT = typer.Option(None, "-o", "--output", help="Output Python file.")
ROOT_OPT = typer.Option(
    "RootDict", "--root-name", help="Name of the main generated type."
)
# Replace `--format` with two mutually-exclusive flags. Default is TypedDict when
# neither flag is provided.
TO_TYPEDDICT_OPT = typer.Option(
    False,
    "--to-typeddict",
    help="Generate TypedDict output (default if no flags provided).",
)
TO_PYDANTIC_OPT = typer.Option(
    False,
    "--to-pydantic",
    help="Generate Pydantic models output.",
)


@schema_app.command("from-bson")
def schema_from_bson(
    bson_path: Path = typer.Argument(..., help="BSON input file.", exists=True),
    output_file: Path | None = OUTPUT_OPT,
    root_name: str = ROOT_OPT,
    to_typeddict: bool = TO_TYPEDDICT_OPT,
    to_pydantic: bool = TO_PYDANTIC_OPT,
) -> None:
    """Generate data classes from a BSON input file."""
    if to_typeddict and to_pydantic:
        raise typer.BadParameter(
            "Options --to-typeddict and --to-pydantic are mutually exclusive"
        )

    # Default to TypedDict when neither flag is provided
    generator = get_generator(to_pydantic)

    async def _run() -> None:
        schema, nested_schemas = await infer_schema_from("bson", path=str(bson_path))
        code = generator.generate(schema, root_name, nested_schemas)

        if output_file:
            output_file.write_text(code, encoding="utf-8")
            fmt = "pydantic" if to_pydantic else "typeddict"
            typer.echo(f"Written {fmt} schema to: {output_file}")
        else:
            fmt = "pydantic" if to_pydantic else "typeddict"
            console.print(f"# --- Generated {fmt} schema ---")
            console.print(code)

    asyncio.run(_run())


@schema_app.command("from-mongo")
def schema_from_mongo(
    uri: str = typer.Option(..., help="MongoDB connection URI."),
    collection: str = typer.Option(..., help="Collection name."),
    output_file: Path | None = OUTPUT_OPT,
    root_name: str = ROOT_OPT,
    to_typeddict: bool = TO_TYPEDDICT_OPT,
    to_pydantic: bool = TO_PYDANTIC_OPT,
) -> None:
    """Infer schema from MongoDB and generate data classes."""
    if to_typeddict and to_pydantic:
        raise typer.BadParameter(
            "Options --to-typeddict and --to-pydantic are mutually exclusive"
        )

    # Default to TypedDict when neither flag is provided
    generator = get_generator(to_pydantic)

    async def _run() -> None:
        schema, nested_schemas = await infer_schema_from(
            "mongodb", uri=uri, collection=collection
        )
        code = generator.generate(schema, root_name, nested_schemas)

        if output_file:
            output_file.write_text(code, encoding="utf-8")
            fmt = "pydantic" if to_pydantic else "typeddict"
            typer.echo(f"Written {fmt} schema to: {output_file}")
        else:
            fmt = "pydantic" if to_pydantic else "typeddict"
            console.print(f"# --- Generated {fmt} schema ---")
            console.print(code)

    asyncio.run(_run())
