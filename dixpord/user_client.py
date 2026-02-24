"""
user_client.py - Direct Discord HTTP API client using a user token.

This talks to Discord's API as YOU (not as a bot), giving access to
your DMs, servers, channels, and all your messages.
"""

from __future__ import annotations

import asyncio
import datetime
import random
from typing import Optional

import aiohttp

from .config import Config
from .models import (
    Attachment,
    Embed,
    ExportedMessage,
    ExportMetadata,
    Reaction,
    UserFilter,
)

API_BASE = "https://discord.com/api/v10"


class DiscordUserClient:
    """
    Lightweight async HTTP client that authenticates as a real Discord user.
    Provides methods to list DMs, servers, channels, and fetch messages.
    """

    def __init__(self, token: str):
        self.token = token
        self._session: Optional[aiohttp.ClientSession] = None
        self.user: dict | None = None  # populated by connect()

    @property
    def headers(self) -> dict:
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    async def _ensure_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _get(self, endpoint: str, params: dict | None = None) -> dict | list:
        """Make a GET request to the Discord API. Handles rate limits."""
        await self._ensure_session()
        url = f"{API_BASE}{endpoint}"

        for attempt in range(5):
            # Small per-request delay to stay well under rate limits
            # Adds slight jitter so requests aren't perfectly periodic
            await asyncio.sleep(0.05 + random.uniform(0, 0.05))

            async with self._session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 429:
                    # Rate limited — wait and retry
                    data = await resp.json()
                    wait = data.get("retry_after", 1.0)
                    await asyncio.sleep(wait + 0.1)
                    continue
                elif resp.status == 401:
                    raise RuntimeError(
                        "Authentication failed. Your DISCORD_USER_TOKEN may be invalid or expired.\n"
                        "See the README for how to get a fresh token from your browser."
                    )
                elif resp.status == 403:
                    raise PermissionError(
                        f"Access denied for {endpoint}. You may not have permission."
                    )
                else:
                    text = await resp.text()
                    raise RuntimeError(
                        f"Discord API error {resp.status} on {endpoint}: {text}"
                    )

        raise RuntimeError(f"Too many retries for {endpoint}")

    # ── Identity ─────────────────────────────────────────────────────

    async def connect(self) -> dict:
        """Verify the token and fetch the current user info."""
        self.user = await self._get("/users/@me")
        return self.user

    @property
    def display_name(self) -> str:
        if not self.user:
            return "Unknown"
        name = self.user.get("global_name") or self.user.get("username", "Unknown")
        disc = self.user.get("discriminator", "0")
        if disc and disc != "0":
            return f"{name}#{disc}"
        return name

    @property
    def user_id(self) -> int:
        return int(self.user["id"]) if self.user else 0

    # ── DMs ──────────────────────────────────────────────────────────

    async def get_dm_channels(self) -> list[dict]:
        """Get all DM / group DM channels for the user."""
        channels = await self._get("/users/@me/channels")
        return channels

    # ── Servers (guilds) ─────────────────────────────────────────────

    async def get_guilds(self) -> list[dict]:
        """Get all guilds the user is in."""
        guilds = await self._get("/users/@me/guilds")
        return guilds

    async def get_guild_channels(self, guild_id: int) -> list[dict]:
        """Get all channels for a guild."""
        channels = await self._get(f"/guilds/{guild_id}/channels")
        return channels

    # ── Messages ─────────────────────────────────────────────────────

    async def fetch_messages(
        self,
        channel_id: int,
        *,
        date_from: datetime.datetime | None = None,
        date_to: datetime.datetime | None = None,
        user_filters: list[UserFilter] | None = None,
        keyword_filter: str | None = None,
        include_bots: bool = True,
        include_pinned_only: bool = False,
        limit: int | None = None,
        progress_callback=None,
    ) -> list[ExportedMessage]:
        """
        Fetch messages from a channel using the user token.
        Applies all the same filters as the bot-mode fetcher.

        user_filters: list of UserFilter objects. If non-empty, only messages
        from authors matching at least one filter are included. Each filter
        can carry its own date_from / date_to override.

        Returns messages sorted oldest-first.
        """
        if include_pinned_only:
            return await self._fetch_pinned(
                channel_id, date_from=date_from, date_to=date_to,
                user_filters=user_filters, keyword_filter=keyword_filter,
                include_bots=include_bots, limit=limit,
            )

        messages: list[ExportedMessage] = []
        fetched = 0
        before_id: int | None = None
        uf_list = user_filters or []
        keyword_lower = keyword_filter.lower() if keyword_filter else None

        # If we have a date_to, convert to snowflake for efficient fetching
        if date_to:
            before_id = _datetime_to_snowflake(date_to)

        while True:
            params: dict = {"limit": 100}
            if before_id:
                params["before"] = str(before_id)

            batch = await self._get(f"/channels/{channel_id}/messages", params=params)

            if not batch:
                break

            for raw in batch:
                fetched += 1
                msg = _parse_raw_message(raw)

                # Date filter (after) — global
                if date_from and msg.timestamp < date_from:
                    # Messages are newest-first, so once we go past date_from
                    # we're done
                    if progress_callback:
                        progress_callback(fetched, len(messages))
                    messages.sort(key=lambda m: m.timestamp)
                    return messages

                # Date filter (before) - shouldn't be needed if we used snowflake
                if date_to and msg.timestamp > date_to:
                    continue

                # Bot filter
                if not include_bots and msg.author_bot:
                    continue

                # Multi-user filter (with per-user date overrides)
                if uf_list:
                    if not _msg_matches_user_filters(msg, uf_list):
                        continue

                # Keyword filter
                if keyword_lower:
                    if keyword_lower not in msg.content.lower():
                        continue

                messages.append(msg)

                if limit and len(messages) >= limit:
                    if progress_callback:
                        progress_callback(fetched, len(messages))
                    messages.sort(key=lambda m: m.timestamp)
                    return messages

            if progress_callback and fetched % 100 == 0:
                progress_callback(fetched, len(messages))

            # Set the cursor for the next page (oldest message in this batch)
            before_id = int(batch[-1]["id"])

            # Breathing room every 300 messages to avoid rate-limit spikes
            if fetched % 300 == 0:
                await asyncio.sleep(Config.RATE_LIMIT_DELAY + random.uniform(0, 0.3))

            # If we got fewer than 100, we've hit the end
            if len(batch) < 100:
                break

        if progress_callback:
            progress_callback(fetched, len(messages))

        messages.sort(key=lambda m: m.timestamp)
        return messages

    async def _fetch_pinned(
        self, channel_id: int, **filter_kwargs
    ) -> list[ExportedMessage]:
        """Fetch only pinned messages from a channel."""
        raw_pins = await self._get(f"/channels/{channel_id}/pins")
        messages = []
        uf_list = filter_kwargs.get("user_filters") or []
        keyword_lower = (filter_kwargs.get("keyword_filter") or "").lower() or None
        date_from = filter_kwargs.get("date_from")
        date_to = filter_kwargs.get("date_to")
        include_bots = filter_kwargs.get("include_bots", True)
        limit = filter_kwargs.get("limit")

        for raw in raw_pins:
            msg = _parse_raw_message(raw)
            msg.is_pinned = True

            if date_from and msg.timestamp < date_from:
                continue
            if date_to and msg.timestamp > date_to:
                continue
            if not include_bots and msg.author_bot:
                continue
            if uf_list and not _msg_matches_user_filters(msg, uf_list):
                continue
            if keyword_lower and keyword_lower not in msg.content.lower():
                continue

            messages.append(msg)
            if limit and len(messages) >= limit:
                break

        messages.sort(key=lambda m: m.timestamp)
        return messages


# ── Multi-user filter logic ──────────────────────────────────────────────


def _msg_matches_user_filters(msg: ExportedMessage, filters: list[UserFilter]) -> bool:
    """
    Check if a message matches at least ONE of the user filters.

    Each UserFilter has:
    - name_pattern: partial match on author name (case-insensitive)
    - date_from / date_to: optional per-user date overrides

    Logic: the message passes if ANY filter matches (OR logic across users).
    A filter matches when:
    1. The author name contains name_pattern, AND
    2. The message timestamp is within the filter's date range (if set)
    """
    name_lower = msg.author_name.lower()
    for uf in filters:
        if uf.name_pattern.lower() not in name_lower:
            continue
        # Name matched — now check this filter's date overrides
        if uf.date_from and msg.timestamp < uf.date_from:
            continue
        if uf.date_to and msg.timestamp > uf.date_to:
            continue
        return True
    return False


# ── JSON → Model converters ─────────────────────────────────────────────


def _parse_raw_message(raw: dict) -> ExportedMessage:
    """Convert a raw Discord API message JSON object to our ExportedMessage model."""
    author = raw.get("author", {})

    attachments = [
        Attachment(
            filename=a.get("filename", "unknown"),
            url=a.get("url", ""),
            size=a.get("size", 0),
        )
        for a in raw.get("attachments", [])
    ]

    embeds = []
    for e in raw.get("embeds", []):
        fields = [
            {
                "name": f.get("name", ""),
                "value": f.get("value", ""),
                "inline": str(f.get("inline", False)),
            }
            for f in e.get("fields", [])
        ]
        embeds.append(
            Embed(
                title=e.get("title"),
                description=e.get("description"),
                url=e.get("url"),
                color=e.get("color"),
                fields=fields,
            )
        )

    reactions = []
    for r in raw.get("reactions", []):
        emoji = r.get("emoji", {})
        emoji_str = emoji.get("name", "?")
        if emoji.get("id"):
            emoji_str = f":{emoji.get('name', 'emoji')}:"
        reactions.append(Reaction(emoji=emoji_str, count=r.get("count", 0)))

    reply_to = None
    ref = raw.get("message_reference")
    if ref:
        reply_to = ref.get("message_id")
        if reply_to:
            reply_to = int(reply_to)

    timestamp = _parse_timestamp(raw.get("timestamp", ""))
    edited_at = None
    if raw.get("edited_timestamp"):
        edited_at = _parse_timestamp(raw["edited_timestamp"])

    return ExportedMessage(
        id=int(raw["id"]),
        author_name=author.get("global_name") or author.get("username", "Unknown"),
        author_id=int(author.get("id", 0)),
        author_discriminator=author.get("discriminator", "0"),
        author_bot=author.get("bot", False),
        content=raw.get("content", ""),
        timestamp=timestamp,
        edited_at=edited_at,
        attachments=attachments,
        embeds=embeds,
        reactions=reactions,
        reply_to_id=reply_to,
        is_pinned=raw.get("pinned", False),
    )


def _parse_timestamp(ts: str) -> datetime.datetime:
    """Parse a Discord ISO-8601 timestamp string."""
    if not ts:
        return datetime.datetime.now(datetime.timezone.utc)
    # Discord timestamps look like: 2024-01-15T12:34:56.789000+00:00
    ts = ts.replace("+00:00", "+0000").replace("Z", "+0000")
    try:
        return datetime.datetime.fromisoformat(ts)
    except ValueError:
        from dateutil import parser as dateparser
        return dateparser.parse(ts)


def _datetime_to_snowflake(dt: datetime.datetime) -> int:
    """Convert a datetime to a Discord snowflake for use in API pagination."""
    # Discord epoch is 2015-01-01T00:00:00Z = 1420070400000 ms
    DISCORD_EPOCH = 1420070400000
    ms = int(dt.timestamp() * 1000)
    return (ms - DISCORD_EPOCH) << 22


def build_metadata_from_raw(
    *,
    channel_info: dict,
    guild_info: dict | None,
    message_count: int,
    date_from: datetime.datetime | None = None,
    date_to: datetime.datetime | None = None,
    user_filters: list[UserFilter] | None = None,
    keyword_filter: str | None = None,
) -> ExportMetadata:
    """Build ExportMetadata from raw API data (not discord.py objects)."""
    channel_type_map = {
        0: "text",
        1: "dm",
        2: "voice",
        3: "group_dm",
        4: "category",
        5: "text",       # announcement
        10: "thread",
        11: "thread",
        12: "thread",
        13: "stage",
        15: "forum",
        16: "forum",      # media
    }

    raw_type = channel_info.get("type", 0)
    channel_type = channel_type_map.get(raw_type, "text")

    guild_name = None
    guild_id = None

    if guild_info:
        guild_name = guild_info.get("name")
        guild_id = int(guild_info["id"]) if guild_info.get("id") else None

    # Determine channel name
    if channel_type == "dm":
        recipients = channel_info.get("recipients", [])
        if recipients:
            r = recipients[0]
            channel_name = r.get("global_name") or r.get("username", "Unknown DM")
        else:
            channel_name = "Unknown DM"
    elif channel_type == "group_dm":
        channel_name = channel_info.get("name") or "Unnamed Group DM"
    else:
        channel_name = channel_info.get("name", "unknown")

    return ExportMetadata(
        guild_name=guild_name,
        guild_id=guild_id,
        channel_name=channel_name,
        channel_id=int(channel_info.get("id", 0)),
        channel_type=channel_type,
        total_messages=message_count,
        date_from=date_from,
        date_to=date_to,
        filter_usernames=user_filters or [],
        filter_keyword=keyword_filter,
    )
