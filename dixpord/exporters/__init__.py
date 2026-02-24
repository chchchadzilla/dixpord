"""
exporters/__init__.py - Exporter registry.

PDF exporter is loaded lazily so that the ``fpdf2`` package is only
required when the user actually chooses PDF output.
"""

from .txt_exporter import TxtExporter
from .md_exporter import MarkdownExporter

EXPORTERS = {
    "txt": TxtExporter,
    "md": MarkdownExporter,
    "pdf": None,  # lazy – loaded on first use
}


def get_exporter(fmt: str):
    """Return the exporter class for the given format string."""
    fmt = fmt.lower().strip()
    if fmt not in EXPORTERS:
        raise ValueError(
            f"Unknown format '{fmt}'. Supported: {', '.join(EXPORTERS.keys())}"
        )

    if fmt == "pdf" and EXPORTERS["pdf"] is None:
        try:
            from .pdf_exporter import PdfExporter
        except ImportError:
            raise ImportError(
                "PDF export requires the 'fpdf2' package.\n"
                "Install it with:  pip install fpdf2"
            ) from None
        EXPORTERS["pdf"] = PdfExporter

    return EXPORTERS[fmt]
