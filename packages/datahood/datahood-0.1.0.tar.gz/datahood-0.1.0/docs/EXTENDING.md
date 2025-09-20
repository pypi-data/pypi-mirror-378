# Extending datahood 🧩

This document describes how to add new connectors, exporters, or schema generators.

## Connector Contract
Every connector must implement:
```python
async def connect(self) -> None
async def disconnect(self) -> None
def extract_data(...) -> AsyncGenerator[dict[str, Any], None]
async def load_data(self, data: AsyncGenerator[dict[str, Any], None], collection: str | None = None) -> None
```

Pattern to return an async generator:
```python
def extract_data(self, ...) -> AsyncGenerator[dict[str, Any], None]:
    async def _gen():
        # fetch and yield one document at a time
        yield {"_id": 1}
    return _gen()
```

## Minimal New Connector Example
```python
from collections.abc import AsyncGenerator
from datahood.connectors.base import BaseConnector

class MySourceConnector(BaseConnector):
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    async def connect(self) -> None:
        ...  # open session

    async def disconnect(self) -> None:
        ...  # close session

    def extract_data(self) -> AsyncGenerator[dict, None]:
        async def _gen():
            # stream items
            yield {"example": True}
        return _gen()

    async def load_data(self, data: AsyncGenerator[dict, None], collection: str | None = None) -> None:
        async for doc in data:
            ...  # write somewhere
```

## Exporters
Exporters orchestrate a source connector → target sink. See `src/datahood/exporters/mongodb.py` for a simple pattern.

## Schema Generation
Schema inference currently supports BSON and MongoDB and can emit:
* TypedDict types
* Pydantic `BaseModel` classes

See CLI module `datahood/cli/schema.py` and generator classes under `datahood/schema/gen/*`.

## Testing New Components
* Add unit tests under `tests/unit/`
* Use integration tests (guarded by `RUN_INTEGRATION=1`) if network or DB needed
* Run: `make test`, `make type-check`, `make lint`

## Dry-Run Notes
Dry-run modes iterate only the source generator counting docs. Keep operations side‑effect free in extractors.

## Contributing Checklist
1. Fork & branch
2. Implement feature with tests
3. Run quality commands
4. Open PR with clear description

Happy hacking! 🚀
