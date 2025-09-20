from pathlib import Path
from typing import Any

from typer.testing import CliRunner

# Import the Typer app entrypoint used by the project's console script
from datahood.__main__ import app as datahood_app


runner = CliRunner()


def test_dry_run_bson_to_mongo(mock_bson_file: Path, mock_mongo_connector: Any) -> None:
    """Test `bson-to-mongo --dry-run`.

    Invoke the CLI `bson-to-mongo` with `--dry-run` and assert it returns
    a dry-run message.

    The fixtures `mock_bson_file` and `mock_mongo_connector` are provided by
    tests.conftest.
    """
    result = runner.invoke(
        datahood_app,
        [
            "export",
            "bson-to-mongo",
            str(mock_bson_file),
            "--dest-uri",
            "mongodb://localhost:27017/",
            "--dest-database",
            "testdb",
            "--dest-collection",
            "coll",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Dry run" in result.output


def test_dry_run_mongo_to_bson(monkeypatch: Any, tmp_path: Path) -> None:
    """Test `mongo-to-bson --dry-run` by monkeypatching the
    MongoDBConnector to yield two docs. This avoids nested loops.

    This test is synchronous to avoid creating a nested asyncio event loop when the
    Typer CLI uses `asyncio.run()` internally. The fake connector still provides
    async methods/async generator for compatibility with the application code.
    """

    class FakeSource:
        def __init__(self, connection_uri: str, database: str | None = None) -> None:
            self._data = [{"_id": 1}, {"_id": 2}]

        async def connect(self) -> None:
            return None

        async def disconnect(self) -> None:
            return None

        def extract_data(self, collection: str):
            async def _gen():
                for d in self._data:
                    yield d

            return _gen()

    # Patch only the MongoDBConnector class used by the CLI export command
    monkeypatch.setattr("datahood.connectors.mongodb.MongoDBConnector", FakeSource)

    result = runner.invoke(
        datahood_app,
        [
            "export",
            "mongo-to-bson",
            "--source-uri",
            "mongodb://localhost:27017/",
            "--source-collection",
            "coll",
            str(tmp_path / "out.bson"),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Dry run" in result.output
