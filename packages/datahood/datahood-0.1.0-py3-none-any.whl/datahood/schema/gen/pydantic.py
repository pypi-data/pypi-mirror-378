"""Pydantic schema generator."""

import keyword

from datahood.schema.gen.base import BaseSchemaGenerator
from datahood.schema.infer.base import Schema


class PydanticGenerator(BaseSchemaGenerator):
    """Generates Pydantic BaseModel classes from a schema."""

    def _get_valid_field_name(self, key: str, used_names: set[str]) -> str:
        """Generate a valid and unique Python identifier for a field name."""
        sanitized_key = key
        if keyword.iskeyword(sanitized_key):
            sanitized_key += "_"
        else:
            # Basic sanitization for invalid characters
            sanitized_key = "".join(c if c.isalnum() or c == "_" else "_" for c in key)
            if sanitized_key and sanitized_key[0].isdigit():
                sanitized_key = "_" + sanitized_key

        # Ensure the generated name is a valid identifier as a fallback
        if not sanitized_key or not sanitized_key.isidentifier():
            sanitized_key = "aliased_field"

        # Ensure uniqueness within the current model
        final_name = sanitized_key
        i = 1
        while final_name in used_names:
            final_name = f"{sanitized_key}_{i}"
            i += 1
        return final_name

    def _generate_model_code(self, name: str, schema: Schema) -> tuple[str, bool]:
        """Generate the code for a single Pydantic model.

        Return a tuple containing the model's code and a boolean indicating
        if any fields with aliases were generated.
        """
        lines = [f"\n\nclass {name}(BaseModel):"]
        has_aliased_fields = False

        if not schema:
            lines.append("    pass")
            return "\n".join(lines), False

        used_field_names: set[str] = set()
        for key, value_type in sorted(schema.items()):
            type_str = self.type_to_string(value_type)

            if key.isidentifier() and not keyword.iskeyword(key):
                lines.append(f"    {key}: {type_str}")
                used_field_names.add(key)
            else:
                has_aliased_fields = True
                field_name = self._get_valid_field_name(key, used_field_names)
                used_field_names.add(field_name)
                lines.append(f"    {field_name}: {type_str} = Field(alias='{key}')")

        return "\n".join(lines), has_aliased_fields

    def generate(
        self,
        root_schema: Schema,
        root_name: str,
        nested_schemas: dict[str, Schema],
    ) -> str:
        """Generate Python source containing Pydantic `BaseModel` classes."""
        all_schemas = {root_name: root_schema, **nested_schemas}
        sorted_schema_names = sorted(all_schemas.keys(), key=len, reverse=True)

        imports = {"from pydantic import BaseModel", "from typing import Any"}
        needs_datetime = False
        model_lines: list[str] = []
        rebuild_lines: list[str] = []
        any_aliased_fields = False

        for name in sorted_schema_names:
            model_code, has_aliased = self._generate_model_code(name, all_schemas[name])
            if "datetime" in model_code:
                needs_datetime = True
            model_lines.append(model_code)
            rebuild_lines.append(f"{name}.model_rebuild()")
            if has_aliased:
                any_aliased_fields = True

        if any_aliased_fields:
            imports.add("from pydantic import Field")
        if needs_datetime:
            imports.add("from datetime import datetime")

        return (
            "\n".join(sorted(list(imports)))
            + "".join(model_lines)
            + "\n\n"
            + "\n".join(rebuild_lines)
        )
