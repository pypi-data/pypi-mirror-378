import os
from pathlib import Path

from bson import BSON
from pymongo import MongoClient
import pytest
from typer.testing import CliRunner

from datahood.__main__ import app as datahood_app


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION", "0") != "1",
    reason="Integration tests are skipped by default. Set RUN_INTEGRATION=1 to enable.",
)

runner = CliRunner()


def _mongo_uri_for(port: int) -> str:
    # Use authenticated connection URI (admin:password) with authSource
    return f"mongodb://admin:password@localhost:{port}/?authSource=admin"


def test_mongo_to_bson_roundtrip(tmp_path: Path) -> None:
    """Insert docs into Mongo, export to BSON via CLI, and read BSON to assert docs."""
    dest_uri = _mongo_uri_for(27017)
    client = MongoClient(dest_uri)
    db = client.get_database("integration_test_db")
    coll = db.get_collection("coll_export")
    # ensure empty collection
    coll.drop()

    # prepare data
    docs = [{"_id": 200, "x": "foo"}, {"_id": 201, "x": "bar"}]
    coll.insert_many(docs)

    out_path = tmp_path / "out_export.bson"

    result = runner.invoke(
        datahood_app,
        [
            "export",
            "mongo-to-bson",
            str(out_path),
            "--source-uri",
            dest_uri,
            "--source-collection",
            "coll_export",
            "--source-database",
            "integration_test_db",
        ],
    )

    assert result.exit_code == 0

    # read bson
    read_docs = []
    with open(out_path, "rb") as fh:
        while True:
            length_bytes = fh.read(4)
            if not length_bytes:
                break
            length = int.from_bytes(length_bytes, "little")
            payload = fh.read(length - 4)
            # Decode via instance method
            doc = BSON(length_bytes + payload).decode()
            read_docs.append(doc)

    ids = {d["_id"] for d in read_docs}
    assert ids == {200, 201}

    # cleanup
    coll.drop()
    client.close()
