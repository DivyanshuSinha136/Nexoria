"""
nexoria.cli.ui
==================
Small terminal-UI toolkit shared by every `nexoria` CLI command:
banners, status tables, spinners, prompts, colored log lines.

Built on `rich` when it's installed, but every function degrades to a
plain `print()`/`input()` implementation when it isn't -- the CLI never
hard-fails just because this one optional dependency is missing. Set
the `NO_COLOR` or `NEXORIA_NO_COLOR` environment variable (or pass
`--no-color`) to force the plain fallback even with rich installed.
"""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import Iterable, Sequence

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm
    from rich import box as _box

    _RICH_IMPORTED = True
except ImportError:  # pragma: no cover - exercised in envs without rich
    _RICH_IMPORTED = False

BRAND = "#7c5cff"
OK = "green"
WARN = "yellow"
BAD = "red"
MUTED = "dim"

_no_color_requested = bool(os.environ.get("NO_COLOR") or os.environ.get("NEXORIA_NO_COLOR"))
_use_rich = _RICH_IMPORTED and not _no_color_requested

_out = Console() if _use_rich else None
_err = Console(stderr=True) if _use_rich else None


def force_plain() -> None:
    """Disable rich output for the rest of the process (used by --no-color
    and by anything piping nexoria's output somewhere non-interactive)."""
    global _use_rich
    _use_rich = False


def using_rich() -> bool:
    return _use_rich


def banner(version: str, tagline: str = "Python-native. Rust-fast. Batteries included.") -> None:
    if _use_rich:
        _out.print(Panel.fit(
            f"[bold {BRAND}]NEXORIA[/bold {BRAND}]  [dim]v{version}[/dim]\n[dim]{tagline}[/dim]",
            border_style=BRAND, box=_box.ROUNDED, padding=(0, 2),
        ))
    else:
        print(f"Nexoria v{version} -- {tagline}")


def success(msg: str) -> None:
    if _use_rich:
        _out.print(f"[bold {OK}]\u2713[/bold {OK}] {msg}")
    else:
        print(f"[ok] {msg}")


def error(msg: str) -> None:
    if _use_rich:
        _err.print(f"[bold {BAD}]\u2717 error:[/bold {BAD}] {msg}")
    else:
        print(f"error: {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    if _use_rich:
        _out.print(f"[bold {WARN}]![/bold {WARN}] {msg}")
    else:
        print(f"warning: {msg}", file=sys.stderr)


def info(msg: str = "") -> None:
    if _use_rich:
        _out.print(msg)
    else:
        print(msg)


def rule(title: str = "") -> None:
    if _use_rich:
        _out.rule(f"[bold {BRAND}]{title}[/bold {BRAND}]" if title else "", style=BRAND)
    else:
        print(f"\n== {title} ==" if title else "\n" + "-" * 44)


def confirm(question: str, default: bool = False) -> bool:
    if _use_rich:
        return Confirm.ask(question, default=default)
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        ans = input(f"{question} {suffix} ").strip().lower()
    except EOFError:
        return default
    if not ans:
        return default
    return ans in ("y", "yes")


@contextmanager
def spinner(msg: str):
    """Show a spinner while a block of code runs; prints a plain start
    line (no live spinner) when rich isn't available or output isn't a
    real terminal."""
    if _use_rich:
        with Progress(
            SpinnerColumn(style=BRAND),
            TextColumn("[progress.description]{task.description}"),
            console=_out, transient=True,
        ) as progress:
            progress.add_task(msg, total=None)
            yield
    else:
        print(f"... {msg}")
        yield


# A status row is (label, ok, detail) where ok is True (ready/active),
# False (missing/required), or None (optional / informational).
StatusRow = tuple[str, "bool | None", str]


def status_table(title: str, sections: Sequence[tuple[str, Iterable[StatusRow]]]) -> None:
    """Render one or more named sections of status rows as a single table."""
    if _use_rich:
        table = Table(title=title, box=_box.SIMPLE_HEAVY, header_style="bold",
                      title_style=f"bold {BRAND}", show_lines=False, expand=False)
        table.add_column("Component", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Detail", style=MUTED, overflow="fold")
        first = True
        for section_name, rows in sections:
            rows = list(rows)
            if not rows:
                continue
            if not first:
                table.add_row("", "", "", end_section=True)
            first = False
            table.add_row(f"[bold {BRAND}]{section_name}[/bold {BRAND}]", "", "")
            for name, ok, detail in rows:
                table.add_row(f"  {name}", _badge(ok), detail)
        _out.print(table)
    else:
        print(f"\n{title}")
        for section_name, rows in sections:
            rows = list(rows)
            if not rows:
                continue
            print(f"\n[{section_name}]")
            for name, ok, detail in rows:
                label = "ready " if ok is True else "missing" if ok is False else "optional"
                print(f"  {name:<38} {label:<8} {detail}")


def _badge(ok: "bool | None") -> str:
    if ok is True:
        return f"[bold {OK}]\u25cf ready[/bold {OK}]"
    if ok is False:
        return f"[bold {BAD}]\u25cb missing[/bold {BAD}]"
    return f"[{MUTED}]\u2013 optional[/{MUTED}]"


def key_values(title: str, pairs: Sequence[tuple[str, str]]) -> None:
    """Small labeled panel, used for things like the dev-server startup
    banner (host, port, module, reload state)."""
    def _join(k: str, v: str) -> str:
        return f"{k} {v}" if k.endswith(".") else f"{k}: {v}"

    if _use_rich:
        body = "\n".join(f"[bold]{k}[/bold] {v}" if k.endswith(".") else f"[bold]{k}:[/bold] {v}" for k, v in pairs)
        _out.print(Panel(body, title=title, title_align="left", border_style=BRAND, box=_box.ROUNDED))
    else:
        print(f"\n{title}")
        for k, v in pairs:
            print(f"  {_join(k, v)}")
