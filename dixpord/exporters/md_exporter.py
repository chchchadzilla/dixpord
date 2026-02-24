"""
md_exporter.py - Export messages to Markdown.
"""

from __future__ import annotations

from pathlib import Path

from .base import BaseExporter
from ..models import ExportedMessage


class MarkdownExporter(BaseExporter):
    """Export messages as a rich Markdown document."""

    @property
    def extension(self) -> str:
        return "md"

    def export(self, output_dir: Path) -> Path:
        path = self._output_path(output_dir)
        lines: list[str] = []

        # Header
        lines.append(f"# 📋 Discord Log Export")
        lines.append("")
        lines.append(f"**Source:** {self.metadata.source_label}  ")
        lines.append(
            f"**Exported:** {self.metadata.export_date.strftime('%Y-%m-%d %H:%M:%S UTC')}  "
        )
        lines.append(f"**Total messages:** {self.metadata.total_messages}  ")

        if self.metadata.date_from:
            lines.append(
                f"**From:** {self.metadata.date_from.strftime('%Y-%m-%d %H:%M:%S UTC')}  "
            )
        if self.metadata.date_to:
            lines.append(
                f"**To:** {self.metadata.date_to.strftime('%Y-%m-%d %H:%M:%S UTC')}  "
            )
        if self.metadata.filter_usernames:
            labels = [uf.label for uf in self.metadata.filter_usernames]
            lines.append(f"**Username filter:** `{', '.join(labels)}`  ")
        elif self.metadata.filter_username:
            lines.append(f"**Username filter:** `{self.metadata.filter_username}`  ")
        if self.metadata.filter_keyword:
            lines.append(f"**Keyword filter:** `{self.metadata.filter_keyword}`  ")

        lines.append("")
        lines.append("---")
        lines.append("")

        prev_date = None

        for msg in self.messages:
            # Day header
            msg_date = msg.timestamp.strftime("%A, %B %d, %Y")
            if msg_date != prev_date:
                lines.append(f"## 📅 {msg_date}")
                lines.append("")
                prev_date = msg_date

            # Message
            pin = " 📌" if msg.is_pinned else ""
            time_str = msg.timestamp.strftime("%H:%M:%S")

            lines.append(f"### `{time_str}` **{msg.author_display}**{pin}")

            if msg.reply_to_id:
                lines.append(f"> *↪ Reply to message ID {msg.reply_to_id}*")
                lines.append("")

            # Content
            if msg.content:
                lines.append("")
                lines.append(msg.content)
                lines.append("")

            # Edited
            if msg.edited_str:
                lines.append(f"*✏️ Edited: {msg.edited_str}*")
                lines.append("")

            # Attachments
            if msg.attachments:
                lines.append("**Attachments:**")
                for att in msg.attachments:
                    size_kb = att.size / 1024
                    lines.append(f"- 📎 [{att.filename}]({att.url}) ({size_kb:.1f} KB)")
                lines.append("")

            # Embeds
            for emb in msg.embeds:
                lines.append("> **Embed**")
                if emb.title:
                    if emb.url:
                        lines.append(f"> ### [{emb.title}]({emb.url})")
                    else:
                        lines.append(f"> ### {emb.title}")
                if emb.description:
                    for desc_line in emb.description.split("\n"):
                        lines.append(f"> {desc_line}")
                for fld in emb.fields:
                    lines.append(f"> **{fld.get('name', '')}:** {fld.get('value', '')}")
                lines.append("")

            # Reactions
            if msg.reactions:
                react_parts = [f"{r.emoji} ×{r.count}" for r in msg.reactions]
                lines.append(f"*Reactions: {' &nbsp; '.join(react_parts)}*")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Footer
        lines.append(f"*End of export — {self.metadata.total_messages} messages*")

        path.write_text("\n".join(lines), encoding="utf-8")
        return path
