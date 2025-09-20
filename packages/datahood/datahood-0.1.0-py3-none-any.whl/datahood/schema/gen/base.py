"""Base classes for schema generation."""

from abc import ABC
from abc import abstractmethod
import types
from typing import Any
from typing import get_args
from typing import get_origin

from datahood.schema.infer.base import Schema


class BaseSchemaGenerator(ABC):
    """Abstract base class for schema generators."""

    def type_to_string(self, t: Any) -> str:
        """Convert an inferred type into Python source text."""
        if t is type(None):
            return "None"
        if isinstance(t, str) and t.endswith("Dict"):
            return t
        if isinstance(t, type):
            return t.__name__
        origin = get_origin(t)
        if origin:
            args = get_args(t)
            args_str = [self.type_to_string(arg) for arg in args]
            if origin is types.UnionType:
                if "None" in args_str:
                    args_str.remove("None")
                    if not args_str:
                        return "None"
                    return " | ".join(sorted(args_str)) + " | None"
                return " | ".join(sorted(args_str))
            return f"{origin.__name__}[{', '.join(args_str)}]"
        return str(t)

    @abstractmethod
    def generate(
        self,
        root_schema: Schema,
        root_name: str,
        nested_schemas: dict[str, Schema],
    ) -> str:
        """Generate Python source code from a schema."""
        raise NotImplementedError
