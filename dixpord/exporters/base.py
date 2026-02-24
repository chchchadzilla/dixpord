"""
base.py - Abstract base class for all exporters.
"""

from __future__ import annotations

import abc
from pathlib import Path

from ..models import ExportedMessage, ExportMetadata


class BaseExporter(abc.ABC):
    """
    Base class for message exporters.

    Subclasses must implement `export()`.
    """

    def __init__(self, metadata: ExportMetadata, messages: list[ExportedMessage]):
        self.metadata = metadata
        self.messages = messages

    @property
    @abc.abstractmethod
    def extension(self) -> str:
        """File extension (without dot)."""
        ...

    @abc.abstractmethod
    def export(self, output_dir: Path) -> Path:
        """
        Export messages to a file in the given directory.

        Returns the path to the created file.
        """
        ...

    def _output_path(self, output_dir: Path) -> Path:
        """Build the output file path."""
        filename = f"{self.metadata.safe_filename}.{self.extension}"
        return output_dir / filename

    def _header_lines(self) -> list[str]:
        """Common header information."""
        lines = [
            f"Source: {self.metadata.source_label}",
            f"Exported: {self.metadata.export_date.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Total messages: {self.metadata.total_messages}",
        ]
        if self.metadata.date_from:
            lines.append(f"From: {self.metadata.date_from.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        if self.metadata.date_to:
            lines.append(f"To: {self.metadata.date_to.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        if self.metadata.filter_usernames:
            labels = [uf.label for uf in self.metadata.filter_usernames]
            lines.append(f"Username filter: {', '.join(labels)}")
        elif self.metadata.filter_username:
            lines.append(f"Username filter: {self.metadata.filter_username}")
        if self.metadata.filter_keyword:
            lines.append(f"Keyword filter: {self.metadata.filter_keyword}")
        return lines
