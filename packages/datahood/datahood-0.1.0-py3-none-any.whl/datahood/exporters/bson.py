"""Exporters for BSON sources.

Helpers to export documents from `.bson` / `.bson.gz` files into other
storage backends via the project's connector interface.
"""

from datahood.connectors.bson import BSONConnector
from datahood.connectors.mongodb import MongoDBConnector
from datahood.exporters.base import BaseExporter


class BSONExporter(BaseExporter):
    """Exporter for BSON files."""

    def __init__(self, path: str):
        super().__init__(BSONConnector(path))

    async def to_mongodb(
        self, target_connector: MongoDBConnector, collection: str
    ) -> None:
        """Export data from the BSON file to a MongoDB collection."""
        await self.source_connector.connect()
        await target_connector.connect()

        try:
            data = self.source_connector.extract_data()
            await target_connector.load_data(data, collection=collection)
        finally:
            await self.source_connector.disconnect()
            await target_connector.disconnect()
