"""
exporters/__init__.py - Exporter registry.
"""

from .txt_exporter import TxtExporter
from .md_exporter import MarkdownExporter
from .pdf_exporter import PdfExporter

EXPORTERS = {
    "txt": TxtExporter,
    "md": MarkdownExporter,
    "pdf": PdfExporter,
}


def get_exporter(fmt: str):
    """Return the exporter class for the given format string."""
    fmt = fmt.lower().strip()
    if fmt not in EXPORTERS:
        raise ValueError(
            f"Unknown format '{fmt}'. Supported: {', '.join(EXPORTERS.keys())}"
        )
    return EXPORTERS[fmt]
