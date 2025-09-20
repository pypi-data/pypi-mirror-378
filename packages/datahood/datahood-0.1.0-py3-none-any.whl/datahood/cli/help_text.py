"""
CLI command examples and constants for help text.

This module centralizes CLI command examples used in help text to ensure
consistency and enable easy testing and maintenance.
"""

from enum import Enum
from typing import Dict


class CLICommands:
    """CLI command examples used in help text."""

    # Main application examples
    TRANSFER_MONGO_TO_BSON = (
        "dh transfer mongo-to-bson --source-uri mongodb://host "
        "--source-collection users"
    )
    TRANSFER_BSON_TO_MONGO = (
        "dh transfer bson-to-mongo data.bson --dest-uri mongodb://host "
        "--dest-collection users"
    )
    SCHEMA_FROM_MONGO = (
        "dh schema from-mongo --uri mongodb://host --collection users --to-pydantic"
    )
    SCHEMA_FROM_BSON = "dh schema from-bson data.bson --to-typeddict"

    # Transfer command examples
    TRANSFER_MONGO_TO_MONGO = (
        "dh transfer mongo-to-mongo --source-uri mongodb://src:27017 "
        "--source-collection users --dest-uri mongodb://dest:27017 "
        "--dest-collection users_backup"
    )
    TRANSFER_MONGO_TO_BSON_DETAILED = (
        "dh transfer mongo-to-bson --source-uri mongodb://localhost "
        "--source-collection products users_export.bson"
    )
    TRANSFER_BSON_TO_MONGO_DETAILED = (
        "dh transfer bson-to-mongo data.bson.gz --dest-uri mongodb://localhost "
        "--dest-collection imported_data"
    )

    # Schema command examples
    SCHEMA_FROM_MONGO_PYDANTIC = (
        "dh schema from-mongo --uri mongodb://localhost "
        "--collection users --to-pydantic"
    )
    SCHEMA_FROM_MONGO_TYPEDDICT = (
        "dh schema from-mongo --uri mongodb://localhost "
        "--collection products --to-typeddict"
    )
    SCHEMA_FROM_BSON_DETAILED = (
        "dh schema from-bson large_dataset.bson.gz --to-pydantic"
    )


class ExampleCategories(Enum):
    """Categories of CLI examples for organized access."""

    MAIN = "main"
    TRANSFER = "transfer"  # formerly EXPORT
    SCHEMA = "schema"


# Dictionary for easy programmatic access to commands
CLI_EXAMPLES: Dict[str, str] = {
    # Main examples
    "main_transfer_mongo_to_bson": CLICommands.TRANSFER_MONGO_TO_BSON,
    "main_transfer_bson_to_mongo": CLICommands.TRANSFER_BSON_TO_MONGO,
    "main_schema_from_mongo": CLICommands.SCHEMA_FROM_MONGO,
    "main_schema_from_bson": CLICommands.SCHEMA_FROM_BSON,
    # Transfer examples (formerly export)
    "transfer_mongo_to_mongo": CLICommands.TRANSFER_MONGO_TO_MONGO,
    "transfer_mongo_to_bson": CLICommands.TRANSFER_MONGO_TO_BSON_DETAILED,
    "transfer_bson_to_mongo": CLICommands.TRANSFER_BSON_TO_MONGO_DETAILED,
    # Schema examples
    "schema_from_mongo_pydantic": CLICommands.SCHEMA_FROM_MONGO_PYDANTIC,
    "schema_from_mongo_typeddict": CLICommands.SCHEMA_FROM_MONGO_TYPEDDICT,
    "schema_from_bson": CLICommands.SCHEMA_FROM_BSON_DETAILED,
}


def get_examples_by_category(category: ExampleCategories) -> Dict[str, str]:
    """Get CLI examples filtered by category."""
    prefix = category.value
    return {key: value for key, value in CLI_EXAMPLES.items() if key.startswith(prefix)}


def get_all_commands() -> list[str]:
    """Get all CLI command examples as a list."""
    return list(CLI_EXAMPLES.values())


def validate_command_format(command: str) -> bool:
    """Validate that a command follows expected format."""
    return command.startswith("dh ") and len(command.split()) >= 3
