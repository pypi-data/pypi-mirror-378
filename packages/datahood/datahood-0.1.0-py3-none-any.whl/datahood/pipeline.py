"""
Provides a programmatic interface for creating and running data pipelines.

This module allows users to define pipelines composed of various steps,
such as data transfer and schema generation, and run them asynchronously.

Example:
    # Define a pipeline to transfer data and generate a schema
    p1 = Pipeline(name="Mongo-to-BSON-and-Schema")
    p1.add_step(TransferStep(
        source=MongoDBConnector("mongodb://localhost:27017/db1"),
        sink=BSONConnector("output.bson.gz"),
        source_options={"collection": "products"}
    ))
    p1.add_step(SchemaGenStep(
        source_type="mongodb",
        source_args={"uri": "mongodb://localhost:27017/db1", "collection": "products"},
        generator=PydanticGenerator(),
        output_path="products_schema.py"
    ))

    # Run the pipeline
    asyncio.run(p1.run())

    # To run multiple pipelines concurrently:
    # await run_pipelines(p1, p2)
"""

from abc import ABC
from abc import abstractmethod
import asyncio
from pathlib import Path
from typing import Any
from typing import Self

from datahood.connectors.base import BaseConnector
from datahood.schema.gen.base import BaseSchemaGenerator
from datahood.schema.infer.factory import SourceType
from datahood.schema.infer.factory import infer_schema_from


class Step(ABC):
    """Abstract base class for a single step in a pipeline."""

    @abstractmethod
    async def execute(self) -> None:
        """Execute the logic for this step."""
        pass


class TransferStep(Step):
    """A pipeline step that transfers data from a source to a sink."""

    def __init__(
        self,
        source: BaseConnector,
        sink: BaseConnector,
        source_options: dict[str, Any] | None = None,
        sink_options: dict[str, Any] | None = None,
    ):
        self.source = source
        self.sink = sink
        self.source_options: dict[str, Any] = source_options or {}
        self.sink_options: dict[str, Any] = sink_options or {}

    async def execute(self) -> None:
        """Connect to source and sink, extract data from source, and load it.

        This method manages connection lifecycle and streams data from the
        source to the sink.
        """
        print(
            (
                "  Executing TransferStep: "
                f"{self.source.__class__.__name__} -> {self.sink.__class__.__name__}..."
            )
        )
        await self.source.connect()
        await self.sink.connect()
        try:
            data_generator = self.source.extract_data(**self.source_options)
            await self.sink.load_data(data_generator, **self.sink_options)
        finally:
            await self.source.disconnect()
            await self.sink.disconnect()
        print("  TransferStep finished.")


class SchemaGenStep(Step):
    """A pipeline step that infers a schema and generates a data class file."""

    def __init__(
        self,
        source_type: SourceType,
        source_args: dict[str, Any],
        generator: BaseSchemaGenerator,
        output_path: str | Path,
        root_name: str = "RootDict",
    ):
        self.source_type: SourceType = source_type
        self.source_args: dict[str, Any] = source_args
        self.generator = generator
        self.output_path = Path(output_path)
        self.root_name = root_name

    async def execute(self) -> None:
        """Infer the schema from the source, generate code, and write it.

        The generated code is written to `self.output_path` using UTF-8
        encoding.
        """
        print(f"  Executing SchemaGenStep for source '{self.source_type}'...")
        schema, nested_schemas = await infer_schema_from(
            self.source_type, **self.source_args
        )
        code = self.generator.generate(schema, self.root_name, nested_schemas)

        self.output_path.write_text(code, encoding="utf-8")
        print(f"  SchemaGenStep finished. Schema written to {self.output_path}")


class Pipeline:
    """Represent a data pipeline composed of executable steps."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.steps: list[Step] = []

    def add_step(self, step: Step) -> Self:
        """Add a step to the pipeline and return self for chaining."""
        self.steps.append(step)
        return self

    async def run(self) -> None:
        """Run all steps in the pipeline sequentially."""
        print(f"Running pipeline: '{self.name}'...")
        for i, step in enumerate(self.steps):
            print(f" Step {i + 1}/{len(self.steps)}:")
            await step.execute()
        print(f"Finished pipeline: '{self.name}'.")


async def run_pipelines(*pipelines: Pipeline) -> None:
    """Run multiple pipelines concurrently."""
    print(f"Executing {len(pipelines)} pipelines concurrently...")
    tasks = [asyncio.create_task(p.run()) for p in pipelines]
    await asyncio.gather(*tasks)
    print("All pipelines finished.")
