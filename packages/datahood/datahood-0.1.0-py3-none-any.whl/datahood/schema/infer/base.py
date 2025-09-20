"""Base classes for schema inference."""

from abc import ABC
from abc import abstractmethod
import datetime
import types
from typing import Any
from typing import cast
from typing import get_args
from typing import get_origin


# Representation types
InferredType = Any
Schema = dict[str, InferredType]


class BaseSchemaInferer(ABC):
    """Abstract base class for schema inferers."""

    def __init__(self) -> None:
        self.nested_schemas: dict[str, Schema] = {}

    def to_pascal_case(self, text: str) -> str:
        """Convert a snake_case identifier to PascalCase."""
        if "_" in text:
            return "".join(word.capitalize() for word in text.split("_"))
        return text[0].upper() + text[1:]

    def infer_type(self, value: Any, key_name: str, parent_name: str) -> InferredType:
        """Infer a representation for ``value``."""
        if value is None:
            return type(None)
        # Recognize datetime objects produced by BSON/MongoDB drivers
        if isinstance(value, datetime.datetime):
            return datetime.datetime
        if isinstance(value, (str, bool, int, float)):
            return type(value)
        if isinstance(value, list):
            if not value:
                return list[Any]
            element_types: set[InferredType] = set()
            for item in cast(list[Any], value):
                element_types.add(self.infer_type(item, key_name, parent_name))
            if len(element_types) == 1:
                inner_type = next(iter(element_types))
                return list[inner_type]
            return list[Any]
        if isinstance(value, dict):
            nested_dict_name = f"{parent_name}{self.to_pascal_case(key_name)}Dict"
            value_dict = cast(dict[str, Any], value)
            nested_schema = self.infer_schema_from_obj(value_dict, nested_dict_name)
            self.nested_schemas[nested_dict_name] = nested_schema
            return nested_dict_name
        return Any

    def merge_types(self, type1: InferredType, type2: InferredType) -> InferredType:
        """Merge two inferred types, attempting to keep specificity."""
        if type1 == type2:
            return type1
        if type1 == Any or type2 == Any:
            return Any
        existing: set[InferredType] = set()
        for t in (type1, type2):
            origin = get_origin(t)
            if origin is types.UnionType:
                for arg in get_args(t):
                    existing.add(arg)
            else:
                existing.add(t)
        if len(existing) == 1:
            return next(iter(existing))
        return Any

    def infer_schema_from_obj(self, data: dict[str, Any], dict_name: str) -> Schema:
        """Infer a schema from a mapping."""
        return {
            key: self.infer_type(value, key, dict_name) for key, value in data.items()
        }

    def infer_schema_from_list(
        self,
        data_list: list[dict[str, Any]],
        dict_name: str,
    ) -> Schema:
        """Infer a merged schema from a sequence of mapping objects."""
        if not data_list:
            return {}
        master_schema: Schema = {}
        schemas: list[Schema] = [
            self.infer_schema_from_obj(obj, dict_name) for obj in data_list
        ]
        all_keys: set[str] = set()
        for s in schemas:
            all_keys.update(s.keys())
        for key in all_keys:
            types_for_key: list[InferredType | None] = [s.get(key) for s in schemas]
            is_optional = any(key not in s for s in schemas)
            has_none = any(t is type(None) for t in types_for_key if t is not None)
            non_none_types: list[InferredType] = [
                t for t in types_for_key if t is not None and t is not type(None)
            ]
            final_type: InferredType = Any
            if non_none_types:
                acc = non_none_types[0]
                for t in non_none_types[1:]:
                    acc = self.merge_types(acc, t)
                final_type = acc
            if is_optional or has_none:
                master_schema[key] = final_type | type(None)
            else:
                master_schema[key] = final_type
        return master_schema

    @abstractmethod
    async def infer_schema(self, **kwargs: Any) -> Schema:
        """Infer schema from a data source."""
