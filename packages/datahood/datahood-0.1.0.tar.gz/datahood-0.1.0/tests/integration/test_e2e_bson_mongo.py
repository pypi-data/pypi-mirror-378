import os
import time

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
    # Use authenticated URI with admin user and authSource
    return f"mongodb://admin:password@localhost:{port}/?authSource=admin"


def _ensure_indexes_absent(db, coll_name):
    # noop for now; placeholder if cleaning needed
    pass


def test_bson_to_mongo_roundtrip(tmp_path):
    """Write a BSON file, import it into Mongo via CLI then assert documents present."""
    # Create sample docs
    docs = [{"_id": 100, "a": "one"}, {"_id": 101, "a": "two"}]
    path = tmp_path / "sample.bson"
    with open(path, "wb") as fh:
        for d in docs:
            fh.write(BSON.encode(d))

    # Import into test Mongo (container exposes 27017 and 27018 in compose.test.yaml)
    dest_uri = _mongo_uri_for(27017)
    # ensure empty target collection
    pre_client = MongoClient(dest_uri)
    pre_db = pre_client.get_database("integration_test_db")
    pre_coll = pre_db.get_collection("coll_e2e")
    pre_coll.drop()
    result = runner.invoke(
        datahood_app,
        [
            "export",
            "bson-to-mongo",
            str(path),
            "--dest-uri",
            dest_uri,
            "--dest-database",
            "integration_test_db",
            "--dest-collection",
            "coll_e2e",
        ],
    )

    assert result.exit_code == 0, result.output

    # Wait a bit for writes to propagate
    time.sleep(0.2)

    client = MongoClient(dest_uri)
    db = client.get_database("integration_test_db")
    coll = db.get_collection("coll_e2e")

    found = list(coll.find({}))
    assert len(found) == 2
    ids = {d["_id"] for d in found}
    assert ids == {100, 101}

    # cleanup
    coll.drop()
    client.close()
