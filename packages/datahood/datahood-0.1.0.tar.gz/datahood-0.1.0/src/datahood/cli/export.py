"""Transfer commands for transferring data between MongoDB and BSON."""

import asyncio
from pathlib import Path

from rich.console import Console
import typer

from datahood.cli.help_text import CLICommands
from datahood.connectors.bson import BSONConnector
from datahood.connectors.mongodb import MongoDBConnector
from datahood.exporters.mongodb import MongoDBExporter


console = Console()


transfer_app = typer.Typer(
    name="transfer",
    help=f"""
    🚀 [bold blue]Transfer Hub[/bold blue] - transfer data with precision and speed

    [green]mongo-to-mongo[/green]   Copy collections between MongoDB instances
    [green]mongo-to-bson[/green]    Export MongoDB collections to BSON files
    [green]bson-to-mongo[/green]    Import BSON files into MongoDB collections

    [bold yellow]TRANSFER EXAMPLES[/bold yellow]
    [green]{CLICommands.TRANSFER_MONGO_TO_MONGO}[/green]
    [green]{CLICommands.TRANSFER_MONGO_TO_BSON_DETAILED}[/green]
    [green]{CLICommands.TRANSFER_BSON_TO_MONGO_DETAILED}[/green]

    [bold yellow]SAFETY FEATURES[/bold yellow]
    [magenta]--dry-run[/magenta]       Preview transfer without moving data
    [magenta]Streaming[/magenta]       Process large datasets without memory issues
    [magenta]Compression[/magenta]     Automatic .gz support for BSON files

    [bold yellow]PERFORMANCE TIPS[/bold yellow]
    • Use [cyan]--dry-run[/cyan] first to verify source data and estimate time
    • MongoDB URIs support connection options: [cyan]?authSource=admin[/cyan]
    • BSON exports preserve exact document structure and types
    """,
    rich_markup_mode="rich",
)

# Module-level Typer arguments to avoid calling functions in defaults (B008)


@transfer_app.command("mongo-to-mongo")
def export_mongo_to_mongo(
    source_uri: str = typer.Option(..., help="Source MongoDB connection URI."),
    source_collection: str = typer.Option(..., help="Source collection name."),
    dest_uri: str = typer.Option(..., help="Destination MongoDB connection URI."),
    dest_collection: str = typer.Option(..., help="Destination collection name."),
    source_database: str | None = typer.Option(
        None, help="Optional source database name."
    ),
    dest_database: str | None = typer.Option(
        None, help="Optional destination database name."
    ),
    dry_run: bool = typer.Option(
        False,
        help="If set, only count documents without transferring.",
    ),
) -> None:
    """Export a MongoDB collection to another MongoDB collection."""
    exporter = MongoDBExporter(source_uri, database=source_database)
    dest_conn = MongoDBConnector(dest_uri, database=dest_database)

    async def _run() -> None:
        if dry_run:
            await exporter.source_connector.connect()
            try:
                data = exporter.source_connector.extract_data(
                    collection=source_collection
                )
                count = 0
                async for _ in data:
                    count += 1
                console.print(
                    f"[yellow]Dry run: {count} documents would be transferred.[/yellow]"
                )
                return
            finally:
                await exporter.source_connector.disconnect()

        await exporter.to_mongodb(
            dest_conn, collection=source_collection, dest_collection=dest_collection
        )

    asyncio.run(_run())
    console.print(
        f"[green]Transferred {source_collection} -> {dest_collection}[/green]"
    )


@transfer_app.command("mongo-to-bson")
def export_mongo_to_bson(
    source_uri: str = typer.Option(..., help="Source MongoDB connection URI."),
    source_collection: str = typer.Option(..., help="Source collection name."),
    bson_path: Path = typer.Argument(..., help="Path to the output BSON file."),
    source_database: str | None = typer.Option(
        None, help="Optional source database name."
    ),
    dry_run: bool = typer.Option(
        False, help="If set, only count documents without exporting."
    ),
) -> None:
    """Export a MongoDB collection to a BSON file."""
    exporter = MongoDBExporter(source_uri, database=source_database)
    dest_conn = BSONConnector(str(bson_path))

    async def _run() -> None:
        if dry_run:
            await exporter.source_connector.connect()
            try:
                data = exporter.source_connector.extract_data(
                    collection=source_collection
                )
                count = 0
                async for _ in data:
                    count += 1
                console.print(
                    (
                        "[yellow]Dry run: {count} documents would be "
                        "exported to BSON.[/yellow]"
                    ).format(count=count)
                )
                return
            finally:
                await exporter.source_connector.disconnect()

        await exporter.to_bson(dest_conn, collection=source_collection)

    asyncio.run(_run())
    console.print(f"[green]Exported {source_collection} -> {bson_path}[/green]")


@transfer_app.command("bson-to-mongo")
def export_bson_to_mongo(
    bson_path: Path = typer.Argument(..., help="Path to the input BSON file."),
    dest_uri: str = typer.Option(..., help="Destination MongoDB connection URI."),
    dest_collection: str = typer.Option(..., help="Destination collection name."),
    dest_database: str | None = typer.Option(
        None,
        help=(
            "Optional destination database name. If not provided, "
            "the URI's default DB must be set."
        ),
    ),
    dry_run: bool = typer.Option(
        False, help="If set, only count documents without importing."
    ),
) -> None:
    """Import documents from a BSON file into a MongoDB collection."""
    source_conn = BSONConnector(str(bson_path))

    async def _run() -> None:
        # MongoDBExporter expects source connector to be a MongoDBConnector,
        # but its BaseExporter only relies on source_connector.extract_data(),
        # so we can create an exporter-like flow: call source_conn.extract_data
        # and load into MongoDB via MongoDBConnector directly.
        # Simpler: use MongoDBConnector directly as target and call its load_data.
        await source_conn.connect()
        dest_conn = MongoDBConnector(dest_uri, database=dest_database)
        if dry_run:
            try:
                data = source_conn.extract_data()
                count = 0
                async for _ in data:
                    count += 1
                console.print(
                    (
                        "[yellow]Dry run: {count} documents would be "
                        "imported to MongoDB.[/yellow]"
                    ).format(count=count)
                )
                return
            finally:
                await source_conn.disconnect()

        await dest_conn.connect()
        try:
            data = source_conn.extract_data()
            await dest_conn.load_data(data, collection=dest_collection)
        finally:
            await source_conn.disconnect()
            await dest_conn.disconnect()

    asyncio.run(_run())
    console.print(f"[green]Imported {bson_path} -> {dest_collection}[/green]")
