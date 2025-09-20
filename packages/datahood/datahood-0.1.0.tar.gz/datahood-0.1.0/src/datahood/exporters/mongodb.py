"""Exporters for MongoDB sources."""

from datahood.connectors.bson import BSONConnector
from datahood.connectors.mongodb import MongoDBConnector
from datahood.exporters.base import BaseExporter


class MongoDBExporter(BaseExporter):
    """Exporter for MongoDB collections."""

    def __init__(self, connection_uri: str, database: str | None = None):
        super().__init__(MongoDBConnector(connection_uri, database))

    async def to_bson(self, target_connector: BSONConnector, collection: str) -> None:
        """Export data from a MongoDB collection to a BSON file."""
        await self.source_connector.connect()
        await target_connector.connect()

        try:
            data = self.source_connector.extract_data(collection=collection)
            await target_connector.load_data(data)
        finally:
            await self.source_connector.disconnect()
            await target_connector.disconnect()

    async def to_mongodb(
        self, target_connector: MongoDBConnector, collection: str, dest_collection: str
    ) -> None:
        """Export data from a MongoDB collection to another MongoDB collection."""
        await self.source_connector.connect()
        await target_connector.connect()

        try:
            data = self.source_connector.extract_data(collection=collection)
            await target_connector.load_data(data, collection=dest_collection)
        finally:
            await self.source_connector.disconnect()
            await target_connector.disconnect()
