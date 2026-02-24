"""
pdf_exporter.py - Export messages to PDF using fpdf2.
"""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from .base import BaseExporter
from ..models import ExportedMessage


class _LogPDF(FPDF):
    """Custom FPDF subclass with header/footer."""

    source_label: str = ""
    total_messages: int = 0

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Discord Log Export", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, self.source_label, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(3)
        # Divider
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


class PdfExporter(BaseExporter):
    """Export messages as a styled PDF document."""

    @property
    def extension(self) -> str:
        return "pdf"

    def _safe_text(self, text: str) -> str:
        """Sanitize text for fpdf2 (replace unsupported chars)."""
        # fpdf2 with built-in fonts only supports latin-1ish.
        # Replace common special chars; the rest become '?'.
        replacements = {
            "\u2019": "'",
            "\u2018": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2014": "--",
            "\u2013": "-",
            "\u2026": "...",
            "\u00a0": " ",
            "\u200b": "",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Encode to latin-1 gracefully
        return text.encode("latin-1", errors="replace").decode("latin-1")

    def export(self, output_dir: Path) -> Path:
        path = self._output_path(output_dir)

        pdf = _LogPDF(orientation="P", unit="mm", format="A4")
        pdf.source_label = self._safe_text(self.metadata.source_label)
        pdf.total_messages = self.metadata.total_messages
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        # ── Metadata block ──────────────────────────────────────
        pdf.set_font("Helvetica", "", 9)
        for h in self._header_lines():
            pdf.cell(0, 5, self._safe_text(h), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        prev_date = None

        for msg in self.messages:
            # Day separator
            msg_date = msg.timestamp.strftime("%A, %B %d, %Y")
            if msg_date != prev_date:
                pdf.ln(3)
                pdf.set_fill_color(88, 101, 242)  # Discord blurple
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(
                    0, 7,
                    f"  {self._safe_text(msg_date)}",
                    new_x="LMARGIN", new_y="NEXT",
                    fill=True,
                )
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)
                prev_date = msg_date

            # Author & timestamp
            time_str = msg.timestamp.strftime("%H:%M:%S")
            pin_str = "  [pinned]" if msg.is_pinned else ""

            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(30, 30, 30)
            author_text = self._safe_text(f"{msg.author_display}{pin_str}")
            pdf.cell(0, 5, f"[{time_str}] {author_text}", new_x="LMARGIN", new_y="NEXT")

            # Reply indicator
            if msg.reply_to_id:
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 4, f"    -> Reply to {msg.reply_to_id}", new_x="LMARGIN", new_y="NEXT")

            # Content
            if msg.content:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(50, 50, 50)
                content = self._safe_text(msg.content)
                # multi_cell wraps long text automatically
                pdf.set_x(15)
                pdf.multi_cell(0, 4.5, content)

            # Edited
            if msg.edited_str:
                pdf.set_font("Helvetica", "I", 7)
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 4, f"    (edited {msg.edited_str})", new_x="LMARGIN", new_y="NEXT")

            # Attachments
            for att in msg.attachments:
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(0, 100, 200)
                size_kb = att.size / 1024
                pdf.cell(
                    0, 4,
                    self._safe_text(f"    Attachment: {att.filename} ({size_kb:.1f} KB) - {att.url}"),
                    new_x="LMARGIN", new_y="NEXT",
                )

            # Embeds (simplified)
            for emb in msg.embeds:
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(80, 80, 80)
                if emb.title:
                    pdf.cell(0, 4, self._safe_text(f"    [Embed] {emb.title}"), new_x="LMARGIN", new_y="NEXT")
                if emb.description:
                    desc = self._safe_text(emb.description[:200])
                    if len(emb.description) > 200:
                        desc += "..."
                    pdf.set_x(20)
                    pdf.multi_cell(0, 4, desc)

            # Reactions
            if msg.reactions:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(100, 100, 100)
                react_str = "  ".join(
                    f"{self._safe_text(r.emoji)} x{r.count}" for r in msg.reactions
                )
                pdf.cell(0, 4, f"    Reactions: {react_str}", new_x="LMARGIN", new_y="NEXT")

            pdf.ln(2)

        # Footer
        pdf.ln(5)
        pdf.set_draw_color(180, 180, 180)
        pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(
            0, 5,
            f"End of export - {self.metadata.total_messages} messages",
            new_x="LMARGIN", new_y="NEXT",
            align="C",
        )

        pdf.output(str(path))
        return path
