"""Factory function for creating schema inference results."""

from typing import Any
from typing import Literal
from typing import TypedDict
from typing import cast
from typing import overload

from datahood.connectors.mongodb import MongoDBConnector
from datahood.schema.infer.base import Schema
from datahood.schema.infer.bson import BSONSchemaInferer
from datahood.schema.infer.mongodb import MongoDBSchemaInferer


# Restrict allowed source types for better static checking
SourceType = Literal["bson", "mongodb"]


class BsonParams(TypedDict):
    """Parameters expected when inferring schema from a BSON file."""

    path: str


class MongoParams(TypedDict):
    """Parameters expected when inferring schema from MongoDB."""

    uri: str
    collection: str


@overload
async def infer_schema_from(
    source_type: Literal["bson"], *, path: str
) -> tuple[Schema, dict[str, Schema]]: ...


@overload
async def infer_schema_from(
    source_type: Literal["mongodb"], *, uri: str, collection: str
) -> tuple[Schema, dict[str, Schema]]: ...


@overload
async def infer_schema_from(
    source_type: SourceType, **kwargs: Any
) -> tuple[Schema, dict[str, Schema]]: ...


async def infer_schema_from(
    source_type: SourceType, **kwargs: Any
) -> tuple[Schema, dict[str, Schema]]:
    """
    Infers a schema from a given data source type and its arguments.

    This acts as a factory for schema inference, hiding the details of
    which Inferer or Connector classes to instantiate.

    Args:
        source_type: The type of the data source (e.g., 'bson', 'mongodb').
        **kwargs: Arguments specific to the data source.
            - for 'bson': path (str)
            - for 'mongodb': uri (str), collection (str)

    Returns
    -------
        A tuple containing the root schema and a dictionary of nested schemas.
    """
    if source_type == "bson":
        params = cast(BsonParams, kwargs)
        path = params.get("path")
        if not path:
            raise ValueError("Missing 'path' for bson source type.")
        inferer = BSONSchemaInferer(path)
        root_schema = await inferer.infer_schema()
        return root_schema, inferer.nested_schemas

    if source_type == "mongodb":
        params = cast(MongoParams, kwargs)
        uri = params.get("uri")
        collection = params.get("collection")
        if not uri or not collection:
            raise ValueError("Missing 'uri' or 'collection' for mongodb source type.")
        connector = MongoDBConnector(uri)
        inferer = MongoDBSchemaInferer(connector)
        root_schema = await inferer.infer_schema(collection=collection)
        return root_schema, inferer.nested_schemas

    raise ValueError(f"Unknown source type for schema inference: '{source_type}'")
