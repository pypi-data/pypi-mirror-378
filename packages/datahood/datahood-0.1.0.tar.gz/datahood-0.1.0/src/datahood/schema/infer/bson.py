"""Schema inferer for BSON sources."""

from typing import Any

from datahood.connectors.bson import BSONConnector
from datahood.schema.infer.base import BaseSchemaInferer
from datahood.schema.infer.base import Schema


class BSONSchemaInferer(BaseSchemaInferer):
    """Schema inferer for BSON files."""

    def __init__(self, path: str) -> None:
        super().__init__()
        self.connector = BSONConnector(path)

    async def infer_schema(self, **kwargs: Any) -> Schema:
        """Infer schema from a BSON file."""
        await self.connector.connect()
        try:
            docs: list[dict[str, Any]] = []
            async for doc in self.connector.extract_data():
                docs.append(doc)

            return self.infer_schema_from_list(docs, "RootDict")
        finally:
            await self.connector.disconnect()
