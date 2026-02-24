"""
models.py - Data models for exported messages and metadata.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field


@dataclass
class Attachment:
    """Represents a message attachment."""
    filename: str
    url: str
    size: int  # bytes


@dataclass
class Embed:
    """Simplified representation of a Discord embed."""
    title: str | None = None
    description: str | None = None
    url: str | None = None
    color: int | None = None
    fields: list[dict[str, str]] = field(default_factory=list)


@dataclass
class Reaction:
    """A reaction on a message."""
    emoji: str
    count: int


@dataclass
class UserFilter:
    """
    A per-user filter rule.

    Matches messages where the author name contains `name_pattern` (case-insensitive).
    Optionally restricts to a date range that overrides the global date range.
    """
    name_pattern: str
    date_from: datetime.datetime | None = None
    date_to: datetime.datetime | None = None

    @property
    def label(self) -> str:
        parts = [f'"{self.name_pattern}"']
        if self.date_from:
            parts.append(f"from {self.date_from.strftime('%Y-%m-%d')}")
        if self.date_to:
            parts.append(f"to {self.date_to.strftime('%Y-%m-%d')}")
        return " ".join(parts)


@dataclass
class ExportedMessage:
    """A single exported message."""
    id: int
    author_name: str
    author_id: int
    author_discriminator: str
    author_bot: bool
    content: str
    timestamp: datetime.datetime
    edited_at: datetime.datetime | None
    attachments: list[Attachment] = field(default_factory=list)
    embeds: list[Embed] = field(default_factory=list)
    reactions: list[Reaction] = field(default_factory=list)
    reply_to_id: int | None = None
    is_pinned: bool = False

    @property
    def author_display(self) -> str:
        """Return a display-friendly author string."""
        tag = f"{self.author_name}#{self.author_discriminator}"
        if self.author_discriminator == "0":
            tag = self.author_name
        if self.author_bot:
            tag += " [BOT]"
        return tag

    @property
    def timestamp_str(self) -> str:
        """Return a human-readable timestamp."""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

    @property
    def edited_str(self) -> str | None:
        if self.edited_at:
            return self.edited_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        return None


@dataclass
class ExportMetadata:
    """Metadata about an export operation."""
    guild_name: str | None
    guild_id: int | None
    channel_name: str
    channel_id: int
    channel_type: str  # "text", "dm", "group_dm", "voice", "thread", etc.
    export_date: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    total_messages: int = 0
    date_from: datetime.datetime | None = None
    date_to: datetime.datetime | None = None
    filter_username: str | None = None
    filter_keyword: str | None = None
    filter_usernames: list[UserFilter] = field(default_factory=list)

    @property
    def source_label(self) -> str:
        """Friendly label for where these messages came from."""
        if self.guild_name:
            return f"{self.guild_name} › #{self.channel_name}"
        if self.channel_type == "dm":
            return f"DM with {self.channel_name}"
        if self.channel_type == "group_dm":
            return f"Group DM: {self.channel_name}"
        return f"#{self.channel_name}"

    @property
    def safe_filename(self) -> str:
        """Generate a filesystem-safe filename base."""
        import re
        base = self.source_label.replace("›", "-").replace("#", "")
        base = re.sub(r'[<>:"/\\|?*]', "_", base).strip()
        ts = self.export_date.strftime("%Y%m%d_%H%M%S")
        return f"{base}_{ts}"
