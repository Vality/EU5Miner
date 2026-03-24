"""Thin CLI for install inspection and parser diagnostics."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from eu5miner.formats.cst import parse_cst_document
from eu5miner.formats.script_text import ScriptFeatures, analyze_script_text
from eu5miner.source import ContentPhase, GameInstall
from eu5miner.vfs import VirtualFilesystem


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    command = args.command

    if command == "inspect-install":
        return _run_inspect_install(args)
    if command == "list-files":
        return _run_list_files(args)
    if command == "analyze-script":
        return _run_analyze_script(args)

    parser.error("A command is required")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eu5miner")
    parser.add_argument(
        "--install-root",
        type=Path,
        default=None,
        help="Explicit EU5 install root. Defaults to env var or standard Steam path.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "inspect-install",
        help="Show the discovered install, phase roots, and content sources.",
    )

    list_parser = subparsers.add_parser(
        "list-files",
        help="List merged files from the phase-aware virtual filesystem.",
    )
    list_parser.add_argument(
        "--phase",
        type=_parse_phase,
        required=True,
        help="Content phase to inspect: loading_screen, main_menu, or in_game.",
    )
    list_parser.add_argument(
        "--subpath",
        default="",
        help="Optional relative subpath under the chosen phase.",
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of merged files to print.",
    )
    list_parser.add_argument(
        "--show-contributors",
        action="store_true",
        help="Show all contributors for each merged path instead of only the winner.",
    )

    analyze_parser = subparsers.add_parser(
        "analyze-script",
        help="Run structural and CST diagnostics on a script-like file.",
    )
    target_group = analyze_parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--file",
        type=Path,
        help="Path to a script-like file to analyze.",
    )
    target_group.add_argument(
        "--representative",
        help="Representative file key from the discovered install.",
    )

    return parser


def _run_inspect_install(args: argparse.Namespace) -> int:
    install = GameInstall.discover(args.install_root)
    vfs = VirtualFilesystem.from_install(install)

    print(f"Install root: {install.root}")
    print(f"Game dir: {install.game_dir}")
    print(f"DLC dir: {install.dlc_dir}")
    print(f"Mod dir: {install.mod_dir}")
    print("Phase roots:")
    for phase in ContentPhase:
        print(f"- {phase.value}: {install.phase_dir(phase)}")
    print("Sources:")
    for source in vfs.sources:
        print(f"- {source.kind.value}:{source.name} priority={source.priority} root={source.root}")
    return 0


def _run_list_files(args: argparse.Namespace) -> int:
    install = GameInstall.discover(args.install_root)
    vfs = VirtualFilesystem.from_install(install)
    merged_files = vfs.merge_phase(args.phase, args.subpath)
    display_subpath = Path(args.subpath) if args.subpath else Path(".")

    print(f"Merged files for phase={args.phase.value} subpath={display_subpath}")
    for merged_file in merged_files[: args.limit]:
        if args.show_contributors:
            contributors = ", ".join(
                f"{contributor.source.kind.value}:{contributor.source.name}"
                for contributor in merged_file.contributors
            )
            print(
                f"- {merged_file.relative_path} "
                f"winner={merged_file.winner.source.name} from=[{contributors}]"
            )
        else:
            print(
                f"- {merged_file.relative_path} winner="
                f"{merged_file.winner.source.kind.value}:{merged_file.winner.source.name}"
            )

    print(f"Count: {len(merged_files)}")
    return 0


def _run_analyze_script(args: argparse.Namespace) -> int:
    install = GameInstall.discover(args.install_root) if args.representative else None
    target_path = _resolve_target_path(args.file, args.representative, install)
    text = target_path.read_text(encoding="utf-8", errors="replace")

    features = analyze_script_text(text)
    document = parse_cst_document(text)

    print(f"File: {target_path}")
    _print_features(features)
    print(f"token_count: {len(document.tokens)}")
    print(f"non_trivia_token_count: {len(document.non_trivia_tokens())}")
    print(f"cst_brace_balanced: {document.is_brace_balanced}")
    return 0


def _resolve_target_path(
    file_path: Path | None,
    representative: str | None,
    install: GameInstall | None,
) -> Path:
    if file_path is not None:
        return file_path
    if representative is None or install is None:
        raise ValueError("Either a file path or representative key is required")

    representative_files = install.representative_files()
    if representative not in representative_files:
        valid_keys = ", ".join(sorted(representative_files))
        raise KeyError(f"Unknown representative key '{representative}'. Valid keys: {valid_keys}")
    return representative_files[representative]


def _print_features(features: ScriptFeatures) -> None:
    print(f"balanced_braces: {features.balanced_braces}")
    print(f"brace_depth: {features.brace_depth}")
    print(f"comment_lines: {features.comment_lines}")
    print(f"gui_expression_count: {features.gui_expression_count}")
    print(f"macro_count: {features.macro_count}")
    print(f"scoped_reference_count: {features.scoped_reference_count}")
    print(f"typed_reference_count: {features.typed_reference_count}")
    print(f"entry_mode_count: {features.entry_mode_count}")


def _parse_phase(value: str) -> ContentPhase:
    try:
        return ContentPhase(value)
    except ValueError as exc:
        valid_values = ", ".join(phase.value for phase in ContentPhase)
        raise argparse.ArgumentTypeError(
            f"Unknown phase '{value}'. Expected one of: {valid_values}"
        ) from exc
