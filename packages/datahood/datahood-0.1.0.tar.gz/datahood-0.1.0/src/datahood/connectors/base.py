"""Connector abstractions for datahood.

This module defines a lightweight runtime `ConnectorProtocol` and an
`BaseConnector` abstract base class. Connectors should implement async
`connect`/`disconnect` as well as `extract_data` (async generator) and
`load_data` (async consumer).
"""

from abc import ABC
from abc import abstractmethod
from collections.abc import AsyncGenerator
from typing import Any
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class ConnectorProtocol(Protocol):
    """Protocol describing the async connector interface.

    Implementations must provide `connect`, `disconnect`, `extract_data` and
    `load_data` methods. Using a Protocol makes the expected surface area
    explicit for typing consumers.
    """

    async def connect(self) -> None:
        """Establish connection to the backend."""
        ...

    async def disconnect(self) -> None:
        """Close the connection and release resources."""
        ...

    def extract_data(self, *args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
        """Yield documents from the source as an async generator."""
        if False:
            yield None

    async def load_data(
        self, data: AsyncGenerator[Any, None], *args: Any, **kwargs: Any
    ) -> None:
        """Load documents from an async generator into the sink."""
        ...


class BaseConnector(ABC):
    """Abstract base class for connectors.

    Subclasses should follow the `ConnectorProtocol` contract. Methods are
    asynchronous where appropriate.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the backend."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection and release resources."""

    @abstractmethod
    def extract_data(self, *args: Any, **kwargs: Any) -> AsyncGenerator[Any, None]:
        """Return an async generator yielding documents from the source."""
        if False:
            yield None

    @abstractmethod
    async def load_data(
        self, data: AsyncGenerator[Any, None], *args: Any, **kwargs: Any
    ) -> None:
        """Load documents from an async generator into the sink."""
