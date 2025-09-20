"""MongoDB connector implementation using Motor (async).

This module provides :class:`MongoDBConnector`, a small connector that
implements the `BaseConnector` contract using `motor.motor_asyncio`.
"""

from collections.abc import AsyncGenerator
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from datahood.connectors.base import BaseConnector


class MongoDBConnector(BaseConnector):
    """Asynchronous MongoDB connector using Motor.

    Parameters
    ----------
    connection_uri
        Full MongoDB connection URI.
    database
        Optional database name to use. If not provided, the driver's default
        database selection will be used.
    """

    def __init__(self, connection_uri: str, database: str | None = None) -> None:
        self.connection_uri: str = connection_uri
        self.database: str | None = database
        # Motor's client is a generic type which pyright may require type
        # arguments for; annotate as Any to avoid spurious errors in a small
        # project while still capturing runtime behavior.
        self.client: Any | None = None
        # Motor database object has dynamic attributes; annotate as Any to
        # avoid overly strict type checks in a small project.
        self.db: Any = None

    async def connect(self) -> None:
        """Create Motor client and select database if provided.

        The function assigns `self.client` and `self.db` attributes used by
        `extract_data` and `load_data`. An `assert` ensures static type checkers
        understand `self.client` is not None after creation.
        """
        self.client = AsyncIOMotorClient(self.connection_uri)
        assert self.client is not None
        if self.database:
            # type: ignore[attr-defined]
            self.db = self.client.get_database(self.database)
        else:
            # type: ignore[attr-defined]
            self.db = self.client.get_default_database()

    async def disconnect(self) -> None:
        """Close the Motor client connection."""
        if self.client is not None:
            self.client.close()

    def extract_data(self, collection: str) -> AsyncGenerator[Any, None]:
        """Yield documents from the given collection as an async generator.

        Parameters
        ----------
        collection
            Name of the collection to read from.
        """
        cursor = self.db[collection].find().batch_size(1000)

        async def _gen() -> AsyncGenerator[Any, None]:
            async for document in cursor:
                yield document

        return _gen()

    async def load_data(self, data: AsyncGenerator[Any, None], collection: str) -> None:
        """Insert documents from an async generator into `collection` in batches.

        Parameters
        ----------
        data
            An async generator that yields documents to insert.
        collection
            Collection name where documents will be inserted.
        """
        documents: list[Any] = []
        async for doc in data:
            documents.append(doc)
            if len(documents) >= 1000:
                await self.db[collection].insert_many(documents)
                documents = []
        if documents:
            await self.db[collection].insert_many(documents)
