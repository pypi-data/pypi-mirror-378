from typing import AsyncGenerator

import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_mongo_connector(monkeypatch):
    """Provide a mock MongoDBConnector class to use in CLI tests."""

    class _MockMongo:
        def __init__(self, connection_uri: str, database: str | None = None):
            self.connection_uri = connection_uri
            self.database = database
            self._data = []

        async def connect(self) -> None:
            return None

        async def disconnect(self) -> None:
            return None

        def extract_data(
            self, collection: str | None = None
        ) -> AsyncGenerator[dict, None]:
            async def _gen():
                for d in self._data:
                    yield d

            return _gen()

        async def load_data(self, data, collection: str) -> None:
            async for d in data:
                self._data.append(d)

    monkeypatch.setattr("datahood.connectors.mongodb.MongoDBConnector", _MockMongo)
    return _MockMongo


@pytest.fixture
def mock_bson_file(tmp_path):
    """Create a small bson file with two documents for testing."""
    from bson import BSON

    docs = [
        {"_id": 1, "a": "first"},
        {"_id": 2, "a": "second"},
    ]

    path = tmp_path / "test.bson"
    with open(path, "wb") as fh:
        for d in docs:
            fh.write(BSON.encode(d))

    return path
