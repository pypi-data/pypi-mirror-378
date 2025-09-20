from typer.testing import CliRunner

from datahood.__main__ import app as datahood_app


runner = CliRunner()


def test_mongo_to_mongo_dry_run(monkeypatch):
    """Test the `mongo-to-mongo --dry-run` path uses the exporter to count documents."""

    class FakeSourceConnector:
        def __init__(self) -> None:
            self._data = [{"_id": 1}, {"_id": 2}]

        async def connect(self) -> None:
            return None

        async def disconnect(self) -> None:
            return None

        def extract_data(self, collection: str | None = None):
            async def _gen():
                for d in self._data:
                    yield d

            return _gen()

    class FakeExporter:
        def __init__(self, connection_uri: str, database: str | None = None) -> None:
            self.source_connector = FakeSourceConnector()

    # Patch the exporter class used in the CLI
    monkeypatch.setattr("datahood.cli.export.MongoDBExporter", FakeExporter)

    result = runner.invoke(
        datahood_app,
        [
            "export",
            "mongo-to-mongo",
            "--source-uri",
            "mongodb://localhost:27017/",
            "--source-collection",
            "coll",
            "--dest-uri",
            "mongodb://localhost:27017/",
            "--dest-collection",
            "coll2",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Dry run" in result.output
