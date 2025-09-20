from pathlib import Path

import pytest

from datahood.connectors.bson import BSONConnector


@pytest.mark.asyncio
async def test_bson_streaming_reads_two_docs(tmp_path: Path) -> None:
    from bson import BSON

    docs = [{"_id": 1, "a": "first"}, {"_id": 2, "a": "second"}]
    path = tmp_path / "small.bson"
    with open(path, "wb") as fh:
        for d in docs:
            fh.write(BSON.encode(d))

    connector = BSONConnector(str(path))
    gen = connector.extract_data()

    collected = []
    async for doc in gen:
        collected.append(doc)

    assert len(collected) == 2
    assert collected[0]["_id"] == 1
    assert collected[1]["a"] == "second"
