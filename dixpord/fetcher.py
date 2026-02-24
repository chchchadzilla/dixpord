"""
fetcher.py - Core message fetching engine.
Connects to Discord and retrieves messages with filtering support.
"""

from __future__ import annotations

import asyncio
import datetime
import random
from typing import AsyncGenerator

import discord

from .config import Config
from .models import (
    Attachment,
    Embed,
    ExportedMessage,
    ExportMetadata,
    Reaction,
    UserFilter,
)


def _convert_message(msg: discord.Message) -> ExportedMessage:
    """Convert a discord.py Message into our ExportedMessage model."""
    attachments = [
        Attachment(filename=a.filename, url=a.url, size=a.size)
        for a in msg.attachments
    ]

    embeds = []
    for e in msg.embeds:
        fields = [
            {"name": f.name or "", "value": f.value or "", "inline": str(f.inline)}
            for f in (e.fields or [])
        ]
        embeds.append(
            Embed(
                title=e.title,
                description=e.description,
                url=e.url,
                color=e.color.value if e.color else None,
                fields=fields,
            )
        )

    reactions = []
    for r in msg.reactions:
        reactions.append(Reaction(emoji=str(r.emoji), count=r.count))

    reply_to = None
    if msg.reference and msg.reference.message_id:
        reply_to = msg.reference.message_id

    return ExportedMessage(
        id=msg.id,
        author_name=msg.author.display_name,
        author_id=msg.author.id,
        author_discriminator=msg.author.discriminator or "0",
        author_bot=msg.author.bot,
        content=msg.content or "",
        timestamp=msg.created_at,
        edited_at=msg.edited_at,
        attachments=attachments,
        embeds=embeds,
        reactions=reactions,
        reply_to_id=reply_to,
        is_pinned=msg.pinned,
    )


class MessageFetcher:
    """
    Fetches messages from a Discord channel/DM with rich filtering.

    Parameters
    ----------
    channel : discord.abc.Messageable
        The channel or DM to fetch from.
    date_from : datetime or None
        Only include messages after this date.
    date_to : datetime or None
        Only include messages before this date.
    user_filters : list[UserFilter] or None
        If provided, only include messages from users matching at least one
        filter. Each filter has a name_pattern (partial match) and optional
        per-user date_from / date_to overrides.
    keyword_filter : str or None
        Only include messages whose content contains this string (case-insensitive).
    include_bots : bool
        Whether to include bot messages.
    include_pinned_only : bool
        If True, only fetch pinned messages.
    limit : int or None
        Max number of messages to return. None = no limit.
    """

    def __init__(
        self,
        channel: discord.abc.Messageable,
        *,
        date_from: datetime.datetime | None = None,
        date_to: datetime.datetime | None = None,
        user_filters: list[UserFilter] | None = None,
        keyword_filter: str | None = None,
        include_bots: bool = True,
        include_pinned_only: bool = False,
        limit: int | None = None,
    ):
        self.channel = channel
        self.date_from = date_from
        self.date_to = date_to
        self.user_filters = user_filters or []
        self.keyword_filter = keyword_filter.lower() if keyword_filter else None
        self.include_bots = include_bots
        self.include_pinned_only = include_pinned_only
        self.limit = limit

    def _passes_filters(self, msg: discord.Message) -> bool:
        """Check if a message passes all active filters."""
        # Bot filter
        if not self.include_bots and msg.author.bot:
            return False

        # Multi-user filter (with per-user date overrides)
        if self.user_filters:
            name_lower = msg.author.display_name.lower()
            username_lower = msg.author.name.lower()
            matched = False
            for uf in self.user_filters:
                pattern = uf.name_pattern.lower()
                if pattern not in name_lower and pattern not in username_lower:
                    continue
                # Name matched — check per-user date overrides
                if uf.date_from and msg.created_at < uf.date_from:
                    continue
                if uf.date_to and msg.created_at > uf.date_to:
                    continue
                matched = True
                break
            if not matched:
                return False

        # Keyword filter
        if self.keyword_filter:
            if self.keyword_filter not in (msg.content or "").lower():
                return False

        return True

    async def fetch_all(
        self, progress_callback=None
    ) -> list[ExportedMessage]:
        """
        Fetch all messages matching the filters.

        Parameters
        ----------
        progress_callback : callable or None
            Called with (fetched_count, accepted_count) periodically.

        Returns
        -------
        list[ExportedMessage]
            Messages sorted oldest-first.
        """
        messages: list[ExportedMessage] = []
        fetched = 0

        if self.include_pinned_only:
            # discord.py has a dedicated pins() method
            pinned = await self.channel.pins()
            for msg in pinned:
                fetched += 1
                if self.date_from and msg.created_at < self.date_from:
                    continue
                if self.date_to and msg.created_at > self.date_to:
                    continue
                if self._passes_filters(msg):
                    messages.append(_convert_message(msg))
                    if self.limit and len(messages) >= self.limit:
                        break
            messages.sort(key=lambda m: m.timestamp)
            return messages

        # Use history() with date bounds for efficient fetching
        kwargs = {"limit": None, "oldest_first": True}
        if self.date_from:
            kwargs["after"] = self.date_from
        if self.date_to:
            kwargs["before"] = self.date_to

        async for msg in self.channel.history(**kwargs):
            fetched += 1

            if self._passes_filters(msg):
                messages.append(_convert_message(msg))

            if progress_callback and fetched % 100 == 0:
                progress_callback(fetched, len(messages))

            if self.limit and len(messages) >= self.limit:
                break

            # Breathing room every 300 messages to avoid rate-limit spikes
            if fetched % 300 == 0:
                await asyncio.sleep(Config.RATE_LIMIT_DELAY + random.uniform(0, 0.3))

        if progress_callback:
            progress_callback(fetched, len(messages))

        return messages

    def build_metadata(
        self, channel: discord.abc.Messageable, message_count: int
    ) -> ExportMetadata:
        """Build export metadata from the channel context."""
        guild_name = None
        guild_id = None
        channel_type = "text"

        if isinstance(channel, discord.TextChannel):
            guild_name = channel.guild.name
            guild_id = channel.guild.id
            channel_name = channel.name
            channel_id = channel.id
            channel_type = "text"
        elif isinstance(channel, discord.VoiceChannel):
            guild_name = channel.guild.name
            guild_id = channel.guild.id
            channel_name = channel.name
            channel_id = channel.id
            channel_type = "voice"
        elif isinstance(channel, discord.Thread):
            guild_name = channel.guild.name
            guild_id = channel.guild.id
            channel_name = channel.name
            channel_id = channel.id
            channel_type = "thread"
        elif isinstance(channel, discord.ForumChannel):
            guild_name = channel.guild.name
            guild_id = channel.guild.id
            channel_name = channel.name
            channel_id = channel.id
            channel_type = "forum"
        elif isinstance(channel, discord.StageChannel):
            guild_name = channel.guild.name
            guild_id = channel.guild.id
            channel_name = channel.name
            channel_id = channel.id
            channel_type = "stage"
        elif isinstance(channel, discord.DMChannel):
            channel_name = (
                channel.recipient.display_name if channel.recipient else "Unknown DM"
            )
            channel_id = channel.id
            channel_type = "dm"
        elif isinstance(channel, discord.GroupChannel):
            channel_name = channel.name or "Unnamed Group DM"
            channel_id = channel.id
            channel_type = "group_dm"
        else:
            channel_name = getattr(channel, "name", "unknown")
            channel_id = getattr(channel, "id", 0)

        return ExportMetadata(
            guild_name=guild_name,
            guild_id=guild_id,
            channel_name=channel_name,
            channel_id=channel_id,
            channel_type=channel_type,
            total_messages=message_count,
            date_from=self.date_from,
            date_to=self.date_to,
            filter_usernames=self.user_filters,
            filter_keyword=self.keyword_filter,
        )
