"""BSON file connector.

This connector treats a local `.bson` or `.bson.gz` file as a data source
or sink and implements the same `BaseConnector` contract as other
connectors so it can be used interchangeably by pipelines and exporters.
"""

from collections.abc import AsyncGenerator
import gzip
from typing import Any

from bson import BSON  # type: ignore

from datahood.connectors.base import BaseConnector


class BSONConnector(BaseConnector):
    """Connector for reading/writing BSON files.

    Parameters
    ----------
    path
        Path to a `.bson` or `.bson.gz` file.
    """

    def __init__(self, path: str) -> None:
        self.path = path

    async def connect(self) -> None:
        """No-op for file-based connector (kept for interface compatibility)."""
        return None

    async def disconnect(self) -> None:
        """No-op for file-based connector (kept for interface compatibility)."""
        return None

    def extract_data(
        self, *args: Any, **kwargs: Any
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Yield documents decoded from the BSON file as an async generator.

        This implementation streams the file and decodes documents one by
        one. It avoids loading the entire file into memory and supports
        plain and gzip-compressed BSON files.
        """

        async def _gen() -> AsyncGenerator[dict[str, Any], None]:
            # Open file (gzip or plain) in binary mode and read items
            if self.path.lower().endswith(".gz"):
                fh = gzip.open(self.path, "rb")
            else:
                fh = open(self.path, "rb")

            try:
                while True:
                    # Read the first 4 bytes which encode the document length
                    len_bytes = fh.read(4)
                    if not len_bytes or len(len_bytes) < 4:
                        break
                    length = int.from_bytes(len_bytes, "little")
                    # Read the remainder of the document
                    rest = fh.read(length - 4)
                    if not rest or len(rest) < (length - 4):
                        break
                    doc_bytes = len_bytes + rest
                    try:
                        doc = BSON(doc_bytes).decode()
                    except Exception:
                        # If decode fails, skip the document to avoid stopping
                        # the whole stream; downstream code may handle
                        # validation/logging as needed.
                        continue
                    yield doc
            finally:
                try:
                    fh.close()
                except Exception:
                    pass

        return _gen()

    async def load_data(
        self,
        data: AsyncGenerator[dict[str, Any], None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Write documents from an async generator into the BSON file.

        If the target path ends with ``.gz`` the written file will be gzip
        compressed. Existing content is overwritten.
        """
        write_path = kwargs.get("output_path", self.path)
        is_compressed = write_path.lower().endswith(".gz")

        mode = "wb"
        if is_compressed:
            with gzip.open(write_path, mode) as fh:
                async for doc in data:
                    fh.write(BSON.encode(doc))  # type: ignore[arg-type]
        else:
            with open(write_path, mode) as fh:
                async for doc in data:
                    fh.write(BSON.encode(doc))  # type: ignore[arg-type]
