"""CLI entrypoint for the placeholder GUI shell."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from eu5miner.gui.app import (
    build_navigation_target,
    build_shell_message,
    launch_desktop,
    list_diplomacy_helper_names,
    list_entity_system_names,
    list_religion_helper_names,
    list_supported_system_names,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eu5miner-gui")
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Print the current read-only browser shell instead of launching the desktop app.",
    )
    parser.add_argument(
        "--mod-root",
        action="append",
        default=[],
        help=(
            "Optional additional mod folder to load alongside the active install. "
            "Can be repeated."
        ),
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
        "--diplomacy-helper",
        choices=list_diplomacy_helper_names(),
        default=None,
        help=(
            "Optional diplomacy helper page to load from representative install files, "
            "such as war-flow or diplomacy-graph."
        ),
    )
    parser.add_argument(
        "--religion-helper",
        choices=list_religion_helper_names(),
        default=None,
        help=(
            "Optional religion helper page to load from representative install files, "
            "such as religion-overview."
        ),
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
            "Explicit page key to focus, such as overview or home, report:map or "
            "system:map, entities:religion or list:religion, helper:war-flow or "
            "diplomacy-helper:war-flow, helper:religion-overview or "
            "religion-helper:religion-overview, or entity:map:stockholm or "
            "detail:map:stockholm."
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
        "--page-list-limit",
        type=int,
        default=12,
        help=(
            "Maximum page-index entries to show at once. Use 0 to disable truncation. "
            "Defaults to 12."
        ),
    )
    parser.add_argument(
        "--page-list-offset",
        type=int,
        default=None,
        help=(
            "Optional zero-based page-index window offset. When omitted, the page index "
            "keeps the selected page in view when possible."
        ),
    )
    parser.add_argument(
        "--section-line-limit",
        type=int,
        default=25,
        help=(
            "Maximum rendered lines per section before truncation. Use 0 to disable "
            "truncation. Defaults to 25."
        ),
    )
    parser.add_argument(
        "--entity-list-sort",
        choices=("name", "group", "source"),
        default="name",
        help=(
            "Sort entity list pages by entity name, group then name, or original source "
            "order. Defaults to name."
        ),
    )
    parser.add_argument(
        "--entity-list-mode",
        choices=("compact", "detail"),
        default="compact",
        help=(
            "Render entity list pages as compact summaries or include explicit detail-page "
            "keys. Defaults to compact."
        ),
    )
    parser.add_argument(
        "--entity-list-limit",
        type=int,
        default=25,
        help=(
            "Maximum entity rows to show on entity list pages before windowing. Use 0 to "
            "disable truncation. Defaults to 25."
        ),
    )
    parser.add_argument(
        "--entity-list-offset",
        type=int,
        default=None,
        help=(
            "Optional zero-based entity-list window offset. Defaults to the start of the "
            "sorted entity list."
        ),
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
        if args.describe:
            print(
                build_shell_message(
                    args.install_root,
                    selected_system=args.system,
                    selected_entity_system=args.entity_system,
                    selected_entity_name=args.entity,
                    selected_diplomacy_helper=args.diplomacy_helper,
                    selected_religion_helper=args.religion_helper,
                    include_all_systems=args.all_systems,
                    language=args.language,
                    page_key=args.page,
                    page_filter=args.page_filter,
                    list_pages_only=args.list_pages,
                    show_all_pages=args.show_all_pages,
                    page_list_limit=args.page_list_limit,
                    page_list_offset=args.page_list_offset,
                    section_line_limit=args.section_line_limit,
                    entity_list_sort=args.entity_list_sort,
                    entity_list_mode=args.entity_list_mode,
                    entity_list_limit=args.entity_list_limit,
                    entity_list_offset=args.entity_list_offset,
                )
            )
            return 0

        build_navigation_target(
            args.install_root,
            selected_system=args.system,
            selected_entity_system=args.entity_system,
            selected_entity_name=args.entity,
            selected_diplomacy_helper=args.diplomacy_helper,
            selected_religion_helper=args.religion_helper,
            page_key=args.page,
        )
        return launch_desktop(
            args.install_root,
            selected_system=args.system,
            selected_entity_system=args.entity_system,
            selected_entity_name=args.entity,
            selected_diplomacy_helper=args.diplomacy_helper,
            selected_religion_helper=args.religion_helper,
            page_key=args.page,
            mod_roots=tuple(args.mod_root),
        )
    except (KeyError, ValueError) as exc:
        parser.error(_format_cli_error(exc))
    return 0


def shell_main(argv: Sequence[str] | None = None) -> int:
    shell_argv = [*(list(argv) if argv is not None else []), "--describe"]
    return main(shell_argv)


def _format_cli_error(error: Exception) -> str:
    if isinstance(error, KeyError) and len(error.args) == 1:
        return str(error.args[0])
    return str(error)
