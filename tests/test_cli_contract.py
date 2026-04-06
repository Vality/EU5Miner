from __future__ import annotations

import argparse

from eu5miner.cli import build_parser
from eu5miner.inspection import list_supported_systems

EXPECTED_CLI_COMMANDS = (
    "inspect-install",
    "list-systems",
    "list-files",
    "analyze-script",
    "report-system",
    "plan-mod-update",
    "apply-mod-update",
)


def _get_command_parsers() -> dict[str, argparse.ArgumentParser]:
    parser = build_parser()
    subparser_action = next(
        action
        for action in parser._actions
        if getattr(action, "dest", None) == "command" and hasattr(action, "choices")
    )
    return dict(subparser_action.choices)


def _get_action(parser: argparse.ArgumentParser, dest: str) -> argparse.Action:
    return next(action for action in parser._actions if action.dest == dest)


def test_cli_parser_publishes_documented_command_set() -> None:
    parser = build_parser()
    command_parsers = _get_command_parsers()

    assert parser.prog == "eu5miner"
    assert _get_action(parser, "install_root").default is None
    assert tuple(command_parsers) == EXPECTED_CLI_COMMANDS


def test_report_system_cli_tracks_supported_system_contract() -> None:
    report_parser = _get_command_parsers()["report-system"]
    system_action = _get_action(report_parser, "system")
    language_action = _get_action(report_parser, "language")

    assert tuple(system_action.choices) == tuple(info.name for info in list_supported_systems())
    assert language_action.default == "english"


def test_cli_parser_keeps_thin_option_surface_for_workflow_commands() -> None:
    command_parsers = _get_command_parsers()

    assert {
        action.dest
        for action in command_parsers["list-files"]._actions
        if action.dest != "help"
    } == {"phase", "subpath", "limit", "show_contributors"}
    assert {
        action.dest
        for action in command_parsers["plan-mod-update"]._actions
        if action.dest != "help"
    } == {"mod_root", "later_mod_root", "phase", "subtree", "intended_path", "content_root"}
    assert {
        action.dest
        for action in command_parsers["apply-mod-update"]._actions
        if action.dest != "help"
    } == {
        "mod_root",
        "later_mod_root",
        "phase",
        "subtree",
        "intended_path",
        "content_file",
        "content_root",
        "no_overwrite",
    }


def test_analyze_script_cli_requires_exactly_one_target_mode() -> None:
    analyze_parser = _get_command_parsers()["analyze-script"]

    assert len(analyze_parser._mutually_exclusive_groups) == 1

    target_group = analyze_parser._mutually_exclusive_groups[0]
    assert target_group.required is True
    assert tuple(action.dest for action in target_group._group_actions) == (
        "file",
        "representative",
    )