"""TypedDict schema generator."""

import keyword

from datahood.schema.gen.base import BaseSchemaGenerator
from datahood.schema.infer.base import Schema


class TypedDictGenerator(BaseSchemaGenerator):
    """Generates TypedDict classes from a schema."""

    def generate(
        self,
        root_schema: Schema,
        root_name: str,
        nested_schemas: dict[str, Schema],
    ) -> str:
        """Generate Python source containing `TypedDict` classes."""
        all_schemas = {root_name: root_schema, **nested_schemas}
        sorted_schema_names = sorted(all_schemas.keys(), key=len, reverse=True)
        code_lines: list[str] = ["from typing import TypedDict, Any\n"]
        needs_datetime = False
        for name in sorted_schema_names:
            schema = all_schemas[name]
            code_lines.append(f"\n\nclass {name}(TypedDict):")
            if not schema:
                code_lines.append("    pass")
                continue

            for key, value_type in sorted(schema.items()):
                type_str = self.type_to_string(value_type)
                if "datetime" in type_str:
                    needs_datetime = True
                if key.isidentifier() and not keyword.iskeyword(key):
                    code_lines.append(f"    {key}: {type_str}")
                else:
                    code_lines.append(f'    "{key}": {type_str}')
        if needs_datetime:
            code_lines.insert(0, "from datetime import datetime\n")
        return "\n".join(code_lines)
