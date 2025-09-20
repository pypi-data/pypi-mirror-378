import os
import time

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
    # Use authenticated URI with admin credentials and authSource
    return f"mongodb://admin:password@localhost:{port}/?authSource=admin"


def test_mongo_to_mongo_roundtrip():
    """
    Test mongo-to-mongo end-to-end.

    Insert docs into source Mongo, run mongo-to-mongo CLI, and assert docs copied
    to dest DB.
    """
    src_uri = _mongo_uri_for(27017)
    dest_uri = _mongo_uri_for(27018)

    src_client = MongoClient(src_uri)
    dest_client = MongoClient(dest_uri)

    src_db = src_client.get_database("integration_src")
    src_coll = src_db.get_collection("coll_src")

    dest_db = dest_client.get_database("integration_dest")
    dest_coll = dest_db.get_collection("coll_dest")

    # ensure collections are empty
    src_coll.drop()
    dest_coll.drop()
    # prepare source data
    docs = [{"_id": 301, "v": "a"}, {"_id": 302, "v": "b"}]
    src_coll.insert_many(docs)

    result = runner.invoke(
        datahood_app,
        [
            "export",
            "mongo-to-mongo",
            "--source-uri",
            src_uri,
            "--source-collection",
            "coll_src",
            "--source-database",
            "integration_src",
            "--dest-uri",
            dest_uri,
            "--dest-collection",
            "coll_dest",
            "--dest-database",
            "integration_dest",
        ],
    )

    assert result.exit_code == 0, result.output

    # allow some propagation
    time.sleep(0.2)

    got = list(dest_coll.find({}))
    ids = {d["_id"] for d in got}
    assert ids == {301, 302}

    # cleanup
    src_coll.drop()
    dest_coll.drop()
    src_client.close()
    dest_client.close()
