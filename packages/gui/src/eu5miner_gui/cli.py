"""CLI entrypoint for the placeholder GUI shell."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from eu5miner_gui.app import launch_app, list_supported_system_names


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
        "--language",
        default="english",
        help="Localization language used by language-backed system reports.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    print(
        launch_app(
            args.install_root,
            selected_system=args.system,
            language=args.language,
        )
    )
    return 0
