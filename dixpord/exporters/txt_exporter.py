"""
txt_exporter.py - Export messages to plain text.
"""

from __future__ import annotations

from pathlib import Path

from .base import BaseExporter
from ..models import ExportedMessage


class TxtExporter(BaseExporter):
    """Export messages as a clean plain-text log file."""

    @property
    def extension(self) -> str:
        return "txt"

    def export(self, output_dir: Path) -> Path:
        path = self._output_path(output_dir)
        lines: list[str] = []

        # Header
        lines.append("=" * 72)
        lines.append("  DISCORD LOG EXPORT")
        lines.append("=" * 72)
        for h in self._header_lines():
            lines.append(f"  {h}")
        lines.append("=" * 72)
        lines.append("")

        prev_date = None

        for msg in self.messages:
            # Day separator
            msg_date = msg.timestamp.strftime("%A, %B %d, %Y")
            if msg_date != prev_date:
                lines.append(f"--- {msg_date} {'─' * (50 - len(msg_date))}---")
                lines.append("")
                prev_date = msg_date

            # Message header
            pin_marker = " 📌" if msg.is_pinned else ""
            reply_marker = ""
            if msg.reply_to_id:
                reply_marker = f" (replying to {msg.reply_to_id})"

            lines.append(
                f"[{msg.timestamp.strftime('%H:%M:%S')}] "
                f"{msg.author_display}{pin_marker}{reply_marker}"
            )

            # Content
            if msg.content:
                for content_line in msg.content.split("\n"):
                    lines.append(f"    {content_line}")

            # Edited
            if msg.edited_str:
                lines.append(f"    (edited {msg.edited_str})")

            # Attachments
            for att in msg.attachments:
                size_kb = att.size / 1024
                lines.append(f"    📎 {att.filename} ({size_kb:.1f} KB)")
                lines.append(f"       {att.url}")

            # Embeds
            for emb in msg.embeds:
                lines.append("    ┌─ Embed ─────────────────────────")
                if emb.title:
                    lines.append(f"    │ Title: {emb.title}")
                if emb.description:
                    for desc_line in emb.description.split("\n"):
                        lines.append(f"    │ {desc_line}")
                if emb.url:
                    lines.append(f"    │ URL: {emb.url}")
                for fld in emb.fields:
                    lines.append(f"    │ {fld.get('name', '')}: {fld.get('value', '')}")
                lines.append("    └──────────────────────────────────")

            # Reactions
            if msg.reactions:
                react_str = "  ".join(
                    f"{r.emoji} ×{r.count}" for r in msg.reactions
                )
                lines.append(f"    Reactions: {react_str}")

            lines.append("")

        # Footer
        lines.append("=" * 72)
        lines.append(f"  End of export — {self.metadata.total_messages} messages")
        lines.append("=" * 72)

        path.write_text("\n".join(lines), encoding="utf-8")
        return path
