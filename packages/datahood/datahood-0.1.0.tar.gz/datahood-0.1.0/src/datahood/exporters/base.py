"""Exporter abstractions for datahood.

This module defines a lightweight `BaseExporter` abstract base class.
"""

from datahood.connectors.base import BaseConnector


class BaseExporter:
    """Base class for exporters.

    Keep this lightweight: concrete exporters should accept a connector and
    implement `to_mongodb` / `to_bson` or other methods as needed.
    """

    def __init__(self, source_connector: BaseConnector):
        self.source_connector = source_connector
