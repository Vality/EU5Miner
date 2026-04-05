"""Package main entrypoint for module and wheel execution."""

from __future__ import annotations

from collections.abc import Sequence

from eu5miner_gui.cli import main as cli_main


def main(argv: Sequence[str] | None = None) -> int:
    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())