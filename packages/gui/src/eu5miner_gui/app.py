"""Minimal GUI application shell."""

from eu5miner import ContentPhase


def build_placeholder_message() -> str:
    return (
        "EU5MinerGUI placeholder shell ready. "
        f"Core library available for phase {ContentPhase.IN_GAME.value}."
    )


def launch_app() -> str:
    return build_placeholder_message()
