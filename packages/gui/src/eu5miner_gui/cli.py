"""CLI entrypoint for the placeholder GUI shell."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from eu5miner_gui.app import launch_app


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eu5miner-gui")
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Print the current placeholder GUI status.",
    )
    parser.parse_args(list(argv) if argv is not None else None)
    print(launch_app())
    return 0
