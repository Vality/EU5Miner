"""Wheel entrypoint for direct execution of the built EU5Miner archive."""

from __future__ import annotations

from collections.abc import Sequence

from eu5miner.__main__ import main as package_main


def main(argv: Sequence[str] | None = None) -> int:
    return package_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())