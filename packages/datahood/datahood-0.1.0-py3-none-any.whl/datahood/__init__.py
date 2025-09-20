"""datahood package root."""

__version__ = "0.1.0"

# Import subpackages lazily after version to avoid circular imports
from datahood import cli
from datahood import connectors
from datahood import exporters
from datahood import pipeline
from datahood import schema


__all__ = ["cli", "pipeline", "connectors", "exporters", "schema", "__version__"]
