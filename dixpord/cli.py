"""
cli.py - Interactive Rich CLI for the Discord Log Exporter.
Supports two modes:
  • User mode — uses your personal Discord token (full access to DMs & servers)
  • Bot mode  — uses a Discord bot token (limited to bot-accessible channels)
"""

from __future__ import annotations

import asyncio
import datetime
import sys
import time
from typing import Optional

import discord
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
from dateutil import parser as dateparser

from .config import Config
from .fetcher import MessageFetcher
from .exporters import get_exporter
from .user_client import DiscordUserClient, build_metadata_from_raw
from .models import UserFilter

console = Console()


# ── Helpers ──────────────────────────────────────────────────────────────

def _banner():
    """Print the startup splash — Darrel the DixporD Duck."""
    from rich.text import Text

    # ── Cybernetic Duck ASCII Art ────────────────────────────────────────
    # Built with Rich Text objects to avoid markup nesting issues.
    C = "bright_cyan"
    R = "bright_red"
    Y = "bright_yellow"
    G = "bright_green"

    def _duck_line(*segments):
        """Build a single line from (text, style) pairs."""
        t = Text()
        for text, style in segments:
            t.append(text, style=style)
        return t

    duck_lines = [
        _duck_line(("              ", ""), ("██████████████", C)),
        _duck_line(("          ", ""), ("████", C), ("░░░░░░", R), ("██████████", C)),
        _duck_line(("        ", ""), ("██", C), ("░░░░░░░░░░", R), ("██", C), ("▓▓", Y), ("████", C)),
        _duck_line(("      ", ""), ("██", C), ("░░░░", R), ("████", C), ("░░░░", R), ("██", C), ("▓▓▓▓", Y), ("██", C)),
        _duck_line(("      ", ""), ("██", C), ("░░", R), ("██    ██", C), ("░░░░", R), ("██", C), ("▓▓", Y), ("██", C)),
        _duck_line(("      ", ""), ("██", C), ("░░", R), ("██", C), ("●", G), ("   ██", C), ("░░░░", R), ("████████", C)),
        _duck_line(("      ", ""), ("██", C), ("░░", R), ("██    ██", C), ("░░░░░░░░", R), ("████", C)),
        _duck_line(("      ", ""), ("██", C), ("░░░░", R), ("████", C), ("░░░░░░", R), ("████", C), ("▓▓", Y), ("████████████", C)),
        _duck_line(("        ", ""), ("██", C), ("░░░░░░░░░░", R), ("██", C), ("▓▓▓▓▓▓▓▓▓▓▓▓▓▓", Y), ("████", C)),
        _duck_line(("    ", ""), ("██████", C), ("░░░░░░", R), ("████", C), ("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓", Y), ("██", C)),
        _duck_line(("  ", ""), ("██", C), ("▓▓▓▓", Y), ("██████████", C), ("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓", Y), ("██", C)),
        _duck_line(("  ", ""), ("██", C), ("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓", Y), ("██", C)),
        _duck_line(("    ", ""), ("██", C), ("▓▓▓▓▓▓", Y), ("████", C), ("▓▓▓▓▓▓▓▓▓▓▓▓", Y), ("████", C), ("▓▓▓▓", Y), ("██", C)),
        _duck_line(("    ", ""), ("██", C), ("▓▓▓▓", Y), ("██", C), ("░░░░", R), ("██", C), ("▓▓▓▓▓▓▓▓", Y), ("██", C), ("░░░░", R), ("██", C), ("▓▓", Y), ("██", C)),
        _duck_line(("      ", ""), ("████", C), ("░░░░░░", R), ("██", C), ("▓▓▓▓▓▓▓▓", Y), ("██", C), ("░░░░░░", R), ("████", C)),
        _duck_line(("          ", ""), ("████████  ████████  ████████", C)),
    ]

    console.print()
    for dl in duck_lines:
        console.print(dl)

    # ── Block Letters ────────────────────────────────────────────────────
    title_lines = [
        "",
        " ██████╗  ██╗██╗  ██╗██████╗  ██████╗ ██████╗ ██████╗ ",
        " ██╔══██╗ ██║╚██╗██╔╝██╔══██╗██╔═══██╗██╔══██╗██╔══██╗",
        " ██║  ██║ ██║ ╚███╔╝ ██████╔╝██║   ██║██████╔╝██║  ██║",
        " ██║  ██║ ██║ ██╔██╗ ██╔═══╝ ██║   ██║██╔══██╗██║  ██║",
        " ██████╔╝ ██║██╔╝ ██╗██║     ╚██████╔╝██║  ██║██████╔╝",
        " ╚═════╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═════╝ ",
        "",
    ]
    for tl in title_lines:
        console.print(tl, style="bold bright_blue")

    console.print(
        '  "Quack Quack, motherfeathers!"  ',
        style="bold bright_yellow",
        justify="center",
    )
    console.print()

    # ── Darrel's Story ───────────────────────────────────────────────────
    # Each tuple is (text, style). Plain strings use default style.
    lore: list[tuple[str, str] | str] = [
        ("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "dim bright_cyan"),
        "",
        ("         THE LEGEND OF DARREL THE DIXPORD DUCK", "bold bright_yellow"),
        "",
        ("  In the year 2094, the world was about to end.", "bright_white"),
        ("  Some crazy ass nuke type stuff.", "bright_white"),
        "",
        ("  See, Pete Hegseth had started storing ALL the nuclear", "bright_white"),
        ("  launch codes in Discord instead of Signal. And when", "bright_white"),
        ("  the time came to stop the launch... they couldn't.", "bright_white"),
        ("  There was no chat log export feature.", "bright_white"),
        "",
        ("  The missiles flew. The world burned.", "bright_red"),
        "",
        ("  But in the ashes, they built one last thing:", "bright_white"),
        ("  a time machine.", "bright_cyan"),
        "",
        ("  And they sent back their best operative -- their only", "bright_white"),
        ("  hope -- a cybernetic duck named Darrel.", "bright_white"),
        "",
        ("  His mission: travel back to this very moment and create", "bright_white"),
        ("  DixporD -- the Discord chat exporter that does it all:", "bold bright_blue"),
        "",
        ("    + Export from servers, DMs, and group chats", "green"),
        ("    + Bulk-export every DM conversation at once", "green"),
        ("    + Cross-server keyword search", "green"),
        ("    + Multi-user filtering with per-user date ranges", "green"),
        ("    + Date range, keyword, and bot message filters", "green"),
        ("    + Export as .txt, .md, or styled .pdf", "green"),
        ("    + Attachments, embeds, reactions, replies, pins", "green"),
        ("    + Built-in rate-limit protection", "green"),
        "",
        ("  The world was saved. But there was a catch.", "bright_white"),
        "",
        ("  If the apocalypse never happens... the time machine", "bright_white"),
        ("  is never built. And if the time machine is never built...", "bright_white"),
        ("  Darrel can never go home.", "bright_yellow"),
        "",
        ("  So he found a way to digitize himself -- to live within", "bright_white"),
        ("  the internet, among the 1s and 0s, the only semblance", "bright_white"),
        ("  of familiarity he could find in this cold, analogue world.", "bright_white"),
        "",
        ("  And now he lives there. Helping people export their", "bright_white"),
        ("  Discord files. Making sure the world is saved. For a", "bright_white"),
        ("  species he's not part of. For a timeline he doesn't", "bright_white"),
        ("  belong in.", "bright_white"),
        "",
        ("  Because he has integrity, god damn it.", "bold bright_white"),
        "",
        ("  And today? Integrity is spelled", "bright_white"),
        ("  D -- U -- C -- K", "bold bright_yellow"),
        "",
        ("  Thank you, Darrel.", "dim italic bright_white"),
        "",
        ("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "dim bright_cyan"),
    ]

    for entry in lore:
        if isinstance(entry, str):
            console.print(entry)
        else:
            text, style = entry
            console.print(text, style=style)
        time.sleep(0.04)

    console.print()


def _parse_date(raw: str) -> Optional[datetime.datetime]:
    """Parse a user-supplied date string, or return None."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        dt = dateparser.parse(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except (ValueError, OverflowError):
        console.print(f"[red]Could not parse date:[/] {raw}")
        return None


def _pick_from_table(
    title: str, items: list, columns: list[tuple[str, callable]], *, allow_cancel: bool = True
):
    """
    Display a numbered table and let the user pick one item.
    `columns` is a list of (header, accessor_fn) tuples.
    Returns the chosen item or None if cancelled.
    """
    if not items:
        console.print(f"[yellow]No items found for: {title}[/]")
        return None

    table = Table(title=title, box=box.ROUNDED, show_lines=False, highlight=True)
    table.add_column("#", style="bold cyan", justify="right", width=5)
    for header, _ in columns:
        table.add_column(header)

    for idx, item in enumerate(items, 1):
        row = [str(idx)]
        for _, accessor in columns:
            row.append(str(accessor(item)))
        table.add_row(*row)

    console.print(table)

    cancel_hint = " (0 to cancel)" if allow_cancel else ""
    while True:
        choice = IntPrompt.ask(
            f"Select an item{cancel_hint}",
            default=0 if allow_cancel else 1,
        )
        if allow_cancel and choice == 0:
            return None
        if 1 <= choice <= len(items):
            return items[choice - 1]
        console.print(f"[red]Please enter a number between 1 and {len(items)}[/]")


# ── Main menu choices ────────────────────────────────────────────────────

MAIN_CHOICES = {
    "1": "Export from a server channel",
    "2": "Export from a DM",
    "3": "Search messages across all servers",
    "4": "Export all DMs",
    "5": "List your servers",
    "6": "List your DMs",
    "0": "Quit",
}


def _show_main_menu() -> str:
    console.print()
    table = Table(
        title="[bold]Main Menu[/]",
        box=box.SIMPLE_HEAVY,
        show_header=False,
        title_style="bold bright_blue",
    )
    table.add_column("Option", style="bold cyan", width=5)
    table.add_column("Description")
    for key, desc in MAIN_CHOICES.items():
        table.add_row(key, desc)
    console.print(table)
    return Prompt.ask("Choose", choices=list(MAIN_CHOICES.keys()), default="0")


# ── Filters ──────────────────────────────────────────────────────────────

def _ask_filters() -> dict:
    """Prompt the user for message filters. Returns a dict of kwargs for the fetch engine."""
    console.print("\n[bold]Filter Options[/] (press Enter to skip any)")

    date_from_raw = Prompt.ask("  Start date (e.g. 2024-01-01)", default="")
    date_to_raw = Prompt.ask("  End date   (e.g. 2025-12-31)", default="")

    # ── Multi-user filter ──────────────────────────────────────
    user_filters: list[UserFilter] = []
    username = Prompt.ask(
        "  Filter by username (partial match, or 'multi' for multiple users)",
        default="",
    )

    if username.strip().lower() == "multi":
        console.print(
            "\n  [bold cyan]Multi-user filter mode[/]\n"
            "  [dim]Add one or more usernames. Each can have its own date range.[/]\n"
            "  [dim]Press Enter with an empty name when you're done.[/]"
        )
        while True:
            name = Prompt.ask("    Username pattern (empty = done)", default="")
            if not name.strip():
                break
            uf_from_raw = Prompt.ask(
                f"    Date override: start date for '{name}' (empty = use global)", default=""
            )
            uf_to_raw = Prompt.ask(
                f"    Date override: end date for '{name}' (empty = use global)", default=""
            )
            user_filters.append(
                UserFilter(
                    name_pattern=name.strip(),
                    date_from=_parse_date(uf_from_raw),
                    date_to=_parse_date(uf_to_raw),
                )
            )
            console.print(f"    [green]✓ Added filter:[/] {user_filters[-1].label}")

        if user_filters:
            console.print(f"  [bold]{len(user_filters)} user filter(s) active[/]")
        username = ""  # clear single username since we're using multi
    elif username.strip():
        # Single username — wrap it in a UserFilter for consistency downstream
        user_filters.append(UserFilter(name_pattern=username.strip()))

    keyword = Prompt.ask("  Filter by keyword in message", default="")
    include_bots = Confirm.ask("  Include bot messages?", default=True)
    pinned_only = Confirm.ask("  Pinned messages only?", default=False)
    limit_raw = Prompt.ask("  Max messages (empty = unlimited)", default="")

    limit = None
    if limit_raw.strip():
        try:
            limit = int(limit_raw)
        except ValueError:
            console.print("[yellow]Invalid limit, using unlimited.[/]")

    return {
        "date_from": _parse_date(date_from_raw),
        "date_to": _parse_date(date_to_raw),
        "user_filters": user_filters,
        "keyword_filter": keyword or None,
        "include_bots": include_bots,
        "include_pinned_only": pinned_only,
        "limit": limit,
    }


def _ask_format() -> str:
    """Ask which export format to use."""
    fmt = Prompt.ask(
        "Export format",
        choices=["txt", "md", "pdf"],
        default=Config.DEFAULT_FORMAT,
    )
    return fmt


# ── Export execution ─────────────────────────────────────────────────────

# ════════════════════════════════════════════════════════════════════════
#  USER MODE — uses your personal Discord token via HTTP API
# ════════════════════════════════════════════════════════════════════════

async def _user_do_export(client: DiscordUserClient, channel_info: dict, guild_info: dict | None):
    """Run the full fetch → export pipeline in user mode."""
    filters = _ask_filters()
    fmt = _ask_format()

    channel_id = int(channel_info["id"])

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("{task.completed} accepted"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Fetching messages...", total=None)

        def on_progress(fetched, accepted):
            progress.update(task, completed=accepted, description=f"Scanned {fetched} messages...")

        messages = await client.fetch_messages(
            channel_id,
            progress_callback=on_progress,
            **filters,
        )

    if not messages:
        console.print("[yellow]No messages matched your filters.[/]")
        return

    metadata = build_metadata_from_raw(
        channel_info=channel_info,
        guild_info=guild_info,
        message_count=len(messages),
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
        user_filters=filters.get("user_filters", []),
        keyword_filter=filters.get("keyword_filter"),
    )

    console.print(
        f"\n[green]✓ Fetched {len(messages)} messages from {metadata.source_label}[/]"
    )

    output_dir = Config.ensure_export_dir()
    exporter_cls = get_exporter(fmt)
    exporter = exporter_cls(metadata, messages)

    with console.status("Writing export file..."):
        filepath = exporter.export(output_dir)

    console.print(f"[bold green]✓ Exported to:[/] {filepath.resolve()}")


async def _user_pick_server_channel(client: DiscordUserClient):
    """User mode: pick a server → channel → export."""
    with console.status("Loading your servers..."):
        guilds = await client.get_guilds()

    guilds = sorted(guilds, key=lambda g: g.get("name", "").lower())
    guild = _pick_from_table(
        "Your Servers",
        guilds,
        [
            ("Server", lambda g: g.get("name", "?")),
            ("Server ID", lambda g: g.get("id", "?")),
        ],
    )
    if guild is None:
        return

    with console.status(f"Loading channels for {guild['name']}..."):
        channels = await client.get_guild_channels(int(guild["id"]))

    # Filter to text-like channels (type 0=text, 5=announcement, 15=forum)
    text_channels = [c for c in channels if c.get("type", 99) in (0, 5)]
    text_channels = sorted(text_channels, key=lambda c: c.get("name", "").lower())

    channel = _pick_from_table(
        f"Text Channels in {guild['name']}",
        text_channels,
        [
            ("Channel", lambda c: f"#{c.get('name', '?')}"),
            ("Topic", lambda c: (c.get("topic") or "")[:50]),
        ],
    )
    if channel is None:
        return

    await _user_do_export(client, channel, guild)


async def _user_pick_dm(client: DiscordUserClient):
    """User mode: pick a DM conversation to export."""
    with console.status("Loading your DMs..."):
        dm_channels = await client.get_dm_channels()

    # Separate 1-on-1 DMs (type 1) from group DMs (type 3)
    dms = [ch for ch in dm_channels if ch.get("type") == 1]
    group_dms = [ch for ch in dm_channels if ch.get("type") == 3]

    # Combine with a label
    all_dms = []
    for ch in dms:
        all_dms.append(("DM", _recipient_name(ch), ch))
    for ch in group_dms:
        all_dms.append(("Group", _group_dm_name(ch), ch))

    all_dms.sort(key=lambda x: x[1].lower())

    if not all_dms:
        console.print("[yellow]No DM conversations found.[/]")
        return

    chosen = _pick_from_table(
        f"Your DMs ({len(dms)} direct, {len(group_dms)} group)",
        all_dms,
        [
            ("Type", lambda x: x[0]),
            ("Name", lambda x: x[1]),
            ("Channel ID", lambda x: x[2].get("id", "?")),
        ],
    )
    if chosen is None:
        return

    _, _, channel_info = chosen
    await _user_do_export(client, channel_info, guild_info=None)


async def _user_export_all_dms(client: DiscordUserClient):
    """User mode: export all DM conversations."""
    with console.status("Loading your DMs..."):
        dm_channels = await client.get_dm_channels()

    dms = [ch for ch in dm_channels if ch.get("type") in (1, 3)]
    if not dms:
        console.print("[yellow]No DM conversations found.[/]")
        return

    fmt = _ask_format()
    filters = _ask_filters()
    output_dir = Config.ensure_export_dir()

    console.print(f"\n[bold]Exporting {len(dms)} DM conversations...[/]")

    for ch in dms:
        recipients = ch.get("recipients", [])
        if ch.get("type") == 1 and recipients:
            name = recipients[0].get("global_name") or recipients[0].get("username", "Unknown")
        elif ch.get("name"):
            name = ch["name"]
        else:
            names = [r.get("username", "?") for r in recipients]
            name = ", ".join(names[:3])

        try:
            messages = await client.fetch_messages(int(ch["id"]), **filters)
            if not messages:
                console.print(f"  [dim]Skipped {name} (no messages match)[/]")
                continue

            metadata = build_metadata_from_raw(
                channel_info=ch,
                guild_info=None,
                message_count=len(messages),
                date_from=filters.get("date_from"),
                date_to=filters.get("date_to"),
                user_filters=filters.get("user_filters", []),
                keyword_filter=filters.get("keyword_filter"),
            )

            exporter_cls = get_exporter(fmt)
            exporter = exporter_cls(metadata, messages)
            filepath = exporter.export(output_dir)
            console.print(f"  [green]✓[/] {name}: {len(messages)} messages → {filepath.name}")
        except PermissionError:
            console.print(f"  [red]✗[/] {name}: Access denied")
        except Exception as e:
            console.print(f"  [red]✗[/] {name}: {e}")

    console.print(f"\n[bold green]✓ All exports saved to:[/] {output_dir.resolve()}")


async def _user_search(client: DiscordUserClient):
    """User mode: search messages across all servers."""
    keyword = Prompt.ask("[bold]Search keyword[/]")
    if not keyword.strip():
        console.print("[yellow]No keyword provided.[/]")
        return

    date_from_raw = Prompt.ask("  Start date (optional)", default="")
    date_to_raw = Prompt.ask("  End date   (optional)", default="")
    username = Prompt.ask("  Filter by username (optional)", default="")
    fmt = _ask_format()

    date_from = _parse_date(date_from_raw)
    date_to = _parse_date(date_to_raw)
    search_user_filters: list[UserFilter] = []
    if username.strip():
        search_user_filters.append(UserFilter(name_pattern=username.strip()))

    with console.status("Loading your servers..."):
        guilds = await client.get_guilds()

    all_messages = []
    output_dir = Config.ensure_export_dir()
    guilds = sorted(guilds, key=lambda g: g.get("name", "").lower())
    console.print(f"\n[bold]Searching {len(guilds)} servers for:[/] '{keyword}'")

    for guild in guilds:
        guild_id = int(guild["id"])
        try:
            channels = await client.get_guild_channels(guild_id)
        except PermissionError:
            continue
        except Exception as e:
            console.print(f"  [red]✗[/] {guild['name']}: {e}")
            continue

        text_channels = [c for c in channels if c.get("type", 99) in (0, 5)]

        for ch in text_channels:
            ch_id = int(ch["id"])
            try:
                msgs = await client.fetch_messages(
                    ch_id,
                    date_from=date_from,
                    date_to=date_to,
                    user_filters=search_user_filters,
                    keyword_filter=keyword,
                    limit=200,
                )
                if msgs:
                    console.print(
                        f"  [green]✓[/] {guild['name']} › #{ch['name']}: {len(msgs)} matches"
                    )
                    all_messages.extend(msgs)
            except PermissionError:
                pass
            except Exception as e:
                console.print(f"  [red]✗[/] {guild['name']} › #{ch.get('name', '?')}: {e}")

    if not all_messages:
        console.print("[yellow]No messages found matching your search.[/]")
        return

    all_messages.sort(key=lambda m: m.timestamp)
    console.print(f"\n[green]Found {len(all_messages)} messages total[/]")

    from .models import ExportMetadata

    metadata = ExportMetadata(
        guild_name=None,
        guild_id=None,
        channel_name=f"search_{keyword}",
        channel_id=0,
        channel_type="search",
        total_messages=len(all_messages),
        date_from=date_from,
        date_to=date_to,
        filter_usernames=search_user_filters,
        filter_keyword=keyword,
    )

    exporter_cls = get_exporter(fmt)
    exporter = exporter_cls(metadata, all_messages)
    filepath = exporter.export(output_dir)
    console.print(f"[bold green]✓ Exported to:[/] {filepath.resolve()}")


async def _user_list_servers(client: DiscordUserClient):
    with console.status("Loading your servers..."):
        guilds = await client.get_guilds()

    guilds = sorted(guilds, key=lambda g: g.get("name", "").lower())

    table = Table(title="Your Servers", box=box.ROUNDED, highlight=True, show_lines=False)
    table.add_column("#", style="bold cyan", width=5, justify="right")
    table.add_column("Server Name")
    table.add_column("Server ID", style="dim")

    for idx, g in enumerate(guilds, 1):
        table.add_row(str(idx), g.get("name", "?"), str(g.get("id", "?")))

    console.print(table)


async def _user_list_dms(client: DiscordUserClient):
    with console.status("Loading your DMs..."):
        dm_channels = await client.get_dm_channels()

    dms = [ch for ch in dm_channels if ch.get("type") == 1]
    group_dms = [ch for ch in dm_channels if ch.get("type") == 3]

    table = Table(
        title=f"Your DMs ({len(dms)} direct, {len(group_dms)} group)",
        box=box.ROUNDED, highlight=True,
    )
    table.add_column("#", style="bold cyan", width=5, justify="right")
    table.add_column("Type")
    table.add_column("Name")
    table.add_column("Channel ID", style="dim")

    idx = 1
    for ch in sorted(dms, key=lambda c: _recipient_name(c).lower()):
        table.add_row(str(idx), "DM", _recipient_name(ch), str(ch.get("id", "?")))
        idx += 1
    for ch in group_dms:
        name = ch.get("name") or _group_dm_name(ch)
        table.add_row(str(idx), "Group", name, str(ch.get("id", "?")))
        idx += 1

    console.print(table)


def _recipient_name(ch: dict) -> str:
    recipients = ch.get("recipients", [])
    if recipients:
        r = recipients[0]
        return r.get("global_name") or r.get("username", "Unknown")
    return "Unknown"


def _group_dm_name(ch: dict) -> str:
    recipients = ch.get("recipients", [])
    names = [r.get("global_name") or r.get("username", "?") for r in recipients]
    return ", ".join(names[:4]) + ("..." if len(names) > 4 else "")


async def _user_main_loop(client: DiscordUserClient):
    """Main interactive loop for user-token mode."""
    _banner()
    console.print(
        Panel(
            f"[green]✓ Logged in as:[/] {client.display_name} (ID: {client.user_id})\n"
            "[bold bright_blue]Mode:[/] [bold]User Token[/] — full access to your DMs & servers",
            border_style="green",
        )
    )

    while True:
        choice = _show_main_menu()

        if choice == "0":
            console.print("[dim]Goodbye![/]")
            await client.close()
            break
        elif choice == "1":
            await _user_pick_server_channel(client)
        elif choice == "2":
            await _user_pick_dm(client)
        elif choice == "3":
            await _user_search(client)
        elif choice == "4":
            await _user_export_all_dms(client)
        elif choice == "5":
            await _user_list_servers(client)
        elif choice == "6":
            await _user_list_dms(client)


async def _run_user_mode():
    """Start the tool in user-token mode."""
    client = DiscordUserClient(Config.USER_TOKEN)

    try:
        with console.status("[bold]Connecting to Discord..."):
            await client.connect()
    except RuntimeError as e:
        console.print(f"[bold red]Login failed![/] {e}")
        sys.exit(1)

    try:
        await _user_main_loop(client)
    finally:
        await client.close()


# ════════════════════════════════════════════════════════════════════════
#  BOT MODE — uses a Discord bot token via discord.py
# ════════════════════════════════════════════════════════════════════════

async def _bot_do_export(channel, bot: discord.Client):
    """Run the full fetch → export pipeline for a single channel (bot mode)."""
    filters = _ask_filters()
    fmt = _ask_format()

    fetcher = MessageFetcher(channel, **filters)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("{task.completed} accepted"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Fetching messages...", total=None)

        def on_progress(fetched, accepted):
            progress.update(task, completed=accepted, description=f"Scanned {fetched} messages...")

        messages = await fetcher.fetch_all(progress_callback=on_progress)

    if not messages:
        console.print("[yellow]No messages matched your filters.[/]")
        return

    metadata = fetcher.build_metadata(channel, len(messages))
    console.print(
        f"\n[green]✓ Fetched {len(messages)} messages from {metadata.source_label}[/]"
    )

    output_dir = Config.ensure_export_dir()
    exporter_cls = get_exporter(fmt)
    exporter = exporter_cls(metadata, messages)

    with console.status("Writing export file..."):
        filepath = exporter.export(output_dir)

    console.print(f"[bold green]✓ Exported to:[/] {filepath.resolve()}")


async def _bot_pick_server_channel(bot: discord.Client):
    """Bot mode: let the user pick a server → channel, then export."""
    guilds = sorted(bot.guilds, key=lambda g: g.name.lower())
    guild = _pick_from_table(
        "Your Servers",
        guilds,
        [
            ("Server", lambda g: g.name),
            ("Members", lambda g: g.member_count or "?"),
            ("Channels", lambda g: len(g.text_channels)),
        ],
    )
    if guild is None:
        return

    channels = sorted(guild.text_channels, key=lambda c: (c.category.name if c.category else "", c.name))
    channel = _pick_from_table(
        f"Text Channels in {guild.name}",
        channels,
        [
            ("Channel", lambda c: f"#{c.name}"),
            ("Category", lambda c: c.category.name if c.category else "(none)"),
            ("Topic", lambda c: (c.topic or "")[:50]),
        ],
    )
    if channel is None:
        return

    await _bot_do_export(channel, bot)


async def _bot_pick_dm(bot: discord.Client):
    """Bot mode: let the user pick a DM conversation to export."""
    dms = [ch for ch in bot.private_channels if isinstance(ch, discord.DMChannel)]
    if not dms:
        console.print(
            "[yellow]No DMs found.[/]\n"
            "[dim]In bot mode, bots can only see DMs sent directly to the bot.\n"
            "For full DM access, use [bold]user-token mode[/] instead — "
            "set DISCORD_USER_TOKEN in your .env file.[/]"
        )
        return

    dms_sorted = sorted(dms, key=lambda d: (d.recipient.display_name if d.recipient else ""))
    dm = _pick_from_table(
        "Direct Messages",
        dms_sorted,
        [
            ("User", lambda d: d.recipient.display_name if d.recipient else "Unknown"),
            ("Username", lambda d: d.recipient.name if d.recipient else "Unknown"),
            ("Channel ID", lambda d: d.id),
        ],
    )
    if dm is None:
        return

    await _bot_do_export(dm, bot)


async def _bot_search_across_servers(bot: discord.Client):
    """Bot mode: search for messages across all accessible text channels."""
    keyword = Prompt.ask("[bold]Search keyword[/]")
    if not keyword.strip():
        console.print("[yellow]No keyword provided.[/]")
        return

    date_from_raw = Prompt.ask("  Start date (optional)", default="")
    date_to_raw = Prompt.ask("  End date   (optional)", default="")
    username = Prompt.ask("  Filter by username (optional)", default="")
    fmt = _ask_format()

    date_from = _parse_date(date_from_raw)
    date_to = _parse_date(date_to_raw)
    bot_search_user_filters: list[UserFilter] = []
    if username.strip():
        bot_search_user_filters.append(UserFilter(name_pattern=username.strip()))

    all_messages = []
    output_dir = Config.ensure_export_dir()

    guilds = sorted(bot.guilds, key=lambda g: g.name.lower())
    console.print(f"\n[bold]Searching {len(guilds)} servers for:[/] '{keyword}'")

    for guild in guilds:
        for channel in guild.text_channels:
            try:
                perms = channel.permissions_for(guild.me)
                if not perms.read_message_history:
                    continue
            except Exception:
                continue

            fetcher = MessageFetcher(
                channel,
                date_from=date_from,
                date_to=date_to,
                user_filters=bot_search_user_filters,
                keyword_filter=keyword,
                limit=200,
            )

            try:
                msgs = await fetcher.fetch_all()
                if msgs:
                    console.print(
                        f"  [green]✓[/] {guild.name} › #{channel.name}: {len(msgs)} matches"
                    )
                    all_messages.extend(msgs)
            except discord.Forbidden:
                pass
            except Exception as e:
                console.print(f"  [red]✗[/] {guild.name} › #{channel.name}: {e}")

    if not all_messages:
        console.print("[yellow]No messages found matching your search.[/]")
        return

    all_messages.sort(key=lambda m: m.timestamp)
    console.print(f"\n[green]Found {len(all_messages)} messages total[/]")

    from .models import ExportMetadata

    metadata = ExportMetadata(
        guild_name=None,
        guild_id=None,
        channel_name=f"search_{keyword}",
        channel_id=0,
        channel_type="search",
        total_messages=len(all_messages),
        date_from=date_from,
        date_to=date_to,
        filter_usernames=bot_search_user_filters,
        filter_keyword=keyword,
    )

    exporter_cls = get_exporter(fmt)
    exporter = exporter_cls(metadata, all_messages)
    filepath = exporter.export(output_dir)
    console.print(f"[bold green]✓ Exported to:[/] {filepath.resolve()}")


async def _bot_export_all_dms(bot: discord.Client):
    """Bot mode: export all DM conversations."""
    dms = [ch for ch in bot.private_channels if isinstance(ch, discord.DMChannel)]
    if not dms:
        console.print(
            "[yellow]No DMs found.[/]\n"
            "[dim]In bot mode, bots can only see DMs sent directly to the bot.\n"
            "For full DM access, use [bold]user-token mode[/] instead — "
            "set DISCORD_USER_TOKEN in your .env file.[/]"
        )
        return

    fmt = _ask_format()
    filters = _ask_filters()
    output_dir = Config.ensure_export_dir()

    console.print(f"\n[bold]Exporting {len(dms)} DM conversations...[/]")

    for dm in dms:
        name = dm.recipient.display_name if dm.recipient else "Unknown"
        try:
            fetcher = MessageFetcher(dm, **filters)
            messages = await fetcher.fetch_all()
            if not messages:
                console.print(f"  [dim]Skipped {name} (no messages match)[/]")
                continue

            metadata = fetcher.build_metadata(dm, len(messages))
            exporter_cls = get_exporter(fmt)
            exporter = exporter_cls(metadata, messages)
            filepath = exporter.export(output_dir)
            console.print(f"  [green]✓[/] {name}: {len(messages)} messages → {filepath.name}")
        except discord.Forbidden:
            console.print(f"  [red]✗[/] {name}: Access denied")
        except Exception as e:
            console.print(f"  [red]✗[/] {name}: {e}")

    console.print(f"\n[bold green]✓ All exports saved to:[/] {output_dir.resolve()}")


def _bot_list_servers(bot: discord.Client):
    guilds = sorted(bot.guilds, key=lambda g: g.name.lower())
    table = Table(
        title="Your Servers", box=box.ROUNDED, highlight=True, show_lines=False
    )
    table.add_column("#", style="bold cyan", width=5, justify="right")
    table.add_column("Server Name")
    table.add_column("Members", justify="right")
    table.add_column("Text Channels", justify="right")
    table.add_column("Owner")
    table.add_column("Server ID", style="dim")

    for idx, g in enumerate(guilds, 1):
        owner = g.owner.display_name if g.owner else "?"
        table.add_row(
            str(idx), g.name, str(g.member_count or "?"),
            str(len(g.text_channels)), owner, str(g.id),
        )
    console.print(table)


def _bot_list_dms(bot: discord.Client):
    dms = [ch for ch in bot.private_channels if isinstance(ch, discord.DMChannel)]
    if not dms:
        console.print(
            "[yellow]No DMs found.[/]\n"
            "[dim]In bot mode, bots can only see DMs sent directly to the bot.\n"
            "For full DM access, use [bold]user-token mode[/] instead — "
            "set DISCORD_USER_TOKEN in your .env file.[/]"
        )
        return

    table = Table(title="Recent DMs", box=box.ROUNDED, highlight=True)
    table.add_column("#", style="bold cyan", width=5, justify="right")
    table.add_column("User")
    table.add_column("Username")
    table.add_column("Channel ID", style="dim")

    for idx, dm in enumerate(dms, 1):
        if dm.recipient:
            table.add_row(
                str(idx), dm.recipient.display_name, dm.recipient.name, str(dm.id)
            )
        else:
            table.add_row(str(idx), "Unknown", "?", str(dm.id))
    console.print(table)


# ── Bot runner & main loop ───────────────────────────────────────────────

async def _bot_main_loop(bot: discord.Client):
    """Main interactive loop for bot mode."""
    _banner()
    console.print(
        Panel(
            f"[green]✓ Logged in as:[/] {bot.user} (ID: {bot.user.id})\n"
            f"[green]Servers:[/] {len(bot.guilds)}  |  "
            f"[green]DMs cached:[/] {len(bot.private_channels)}\n"
            "[bold bright_blue]Mode:[/] [bold]Bot Token[/] — server channels only, limited DM access",
            border_style="green",
        )
    )

    while True:
        choice = _show_main_menu()

        if choice == "0":
            console.print("[dim]Goodbye![/]")
            await bot.close()
            break
        elif choice == "1":
            await _bot_pick_server_channel(bot)
        elif choice == "2":
            await _bot_pick_dm(bot)
        elif choice == "3":
            await _bot_search_across_servers(bot)
        elif choice == "4":
            await _bot_export_all_dms(bot)
        elif choice == "5":
            _bot_list_servers(bot)
        elif choice == "6":
            _bot_list_dms(bot)


# ════════════════════════════════════════════════════════════════════════
#  ENTRY POINT — pick the right mode based on available tokens
# ════════════════════════════════════════════════════════════════════════

def run():
    """Entry point for the CLI."""
    # Validate config
    problems = Config.validate()
    if problems:
        console.print("[bold red]Configuration errors:[/]")
        for p in problems:
            console.print(f"  [red]•[/] {p}")
        sys.exit(1)

    has_user = Config.has_user_token()
    has_bot = Config.has_bot_token()

    # If both tokens are set, let the user choose
    if has_user and has_bot:
        console.print(
            Panel(
                "[bold]Both tokens found.[/] Which mode do you want?\n\n"
                "  [bold cyan]1[/]  User mode — full access to YOUR DMs, servers, everything\n"
                "  [bold cyan]2[/]  Bot mode  — uses the bot account (limited DM access)",
                title="Choose Mode",
                border_style="bright_blue",
            )
        )
        mode = Prompt.ask("Mode", choices=["1", "2"], default="1")
        if mode == "1":
            asyncio.run(_run_user_mode())
            return
        # else fall through to bot mode

    # User mode takes priority
    if has_user and not has_bot:
        asyncio.run(_run_user_mode())
        return

    # Bot mode (has_bot is True at this point, or both and user chose bot)
    _run_bot_mode()


def _run_bot_mode():
    """Start the tool in bot-token mode using discord.py."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.dm_messages = True
    intents.guilds = True

    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        await _bot_main_loop(bot)

    try:
        bot.run(Config.BOT_TOKEN, log_handler=None)
    except discord.LoginFailure:
        console.print("[bold red]Login failed![/] Check your DISCORD_BOT_TOKEN in .env")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted. Goodbye![/]")
