"""Schema inferer for MongoDB sources."""

from collections.abc import AsyncGenerator
from typing import Any

from datahood.connectors.mongodb import MongoDBConnector
from datahood.schema.infer.base import BaseSchemaInferer
from datahood.schema.infer.base import Schema


class MongoDBSchemaInferer(BaseSchemaInferer):
    """Schema inferer for MongoDB collections."""

    def __init__(self, connector: MongoDBConnector):
        super().__init__()
        self.connector = connector

    async def infer_schema(self, **kwargs: Any) -> Schema:
        """Infer schema from a MongoDB collection."""
        collection = kwargs.get("collection")
        if not collection or not isinstance(collection, str):
            raise TypeError(
                "infer_schema() missing 1 required keyword-only argument: 'collection'"
            )

        sample_size = kwargs.get("sample_size", 100)
        if not isinstance(sample_size, int):
            raise TypeError("infer_schema() 'sample_size' must be an integer")

        await self.connector.connect()
        try:
            gen: AsyncGenerator[Any, None] = self.connector.extract_data(collection)
            docs: list[dict[str, Any]] = []
            async for doc in gen:
                if len(docs) >= sample_size:
                    break
                if hasattr(doc, "to_dict"):
                    docs.append(doc.to_dict())
                else:
                    docs.append(doc)

            return self.infer_schema_from_list(docs, "RootDict")
        finally:
            await self.connector.disconnect()
