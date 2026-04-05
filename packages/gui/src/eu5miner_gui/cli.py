"""CLI entrypoint for the placeholder GUI shell."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from eu5miner_gui.app import (
    launch_app,
    list_entity_system_names,
    list_supported_system_names,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eu5miner-gui")
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Print the current read-only GUI shell status.",
    )
    parser.add_argument(
        "--install-root",
        type=Path,
        default=None,
        help="Optional explicit EU5 install root for inspection-backed status.",
    )
    parser.add_argument(
        "--system",
        choices=list_supported_system_names(),
        default=None,
        help="Optional supported system to summarize via eu5miner.inspection.",
    )
    parser.add_argument(
        "--entity-system",
        choices=list_entity_system_names(),
        default=None,
        help="Optional covered entity system to browse via eu5miner.inspection.",
    )
    parser.add_argument(
        "--entity",
        default=None,
        help="Optional entity name within --entity-system to open as a detail page.",
    )
    parser.add_argument(
        "--all-systems",
        action="store_true",
        help=(
            "Load report pages for all supported systems and entity list pages for all "
            "covered entity systems from the selected install."
        ),
    )
    parser.add_argument(
        "--page",
        default=None,
        help=(
            "Explicit page key to focus, such as overview, report:map, "
            "entities:religion, or entity:map:stockholm."
        ),
    )
    parser.add_argument(
        "--list-pages",
        action="store_true",
        help="Render only the page index for the current browser session.",
    )
    parser.add_argument(
        "--page-filter",
        default=None,
        help=(
            "Case-insensitive substring filter over loaded page keys, titles, "
            "descriptions, and section lines."
        ),
    )
    parser.add_argument(
        "--show-all-pages",
        action="store_true",
        help="Render all matched pages instead of only the selected page.",
    )
    parser.add_argument(
        "--language",
        default="english",
        help="Localization language used by language-backed system reports.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.list_pages and args.show_all_pages:
        parser.error("--list-pages cannot be combined with --show-all-pages")

    try:
        print(
            launch_app(
                args.install_root,
                selected_system=args.system,
                selected_entity_system=args.entity_system,
                selected_entity_name=args.entity,
                include_all_systems=args.all_systems,
                language=args.language,
                page_key=args.page,
                page_filter=args.page_filter,
                list_pages_only=args.list_pages,
                show_all_pages=args.show_all_pages,
            )
        )
    except (KeyError, ValueError) as exc:
        parser.error(_format_cli_error(exc))
    return 0


def _format_cli_error(error: Exception) -> str:
    if isinstance(error, KeyError) and len(error.args) == 1:
        return str(error.args[0])
    return str(error)
