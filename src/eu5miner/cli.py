"""Thin CLI for install inspection, parser diagnostics, system reports, and mod workflows."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from eu5miner.cli_reports import build_system_report, format_system_report, list_systems
from eu5miner.formats.cst import parse_cst_document
from eu5miner.formats.script_text import ScriptFeatures, analyze_script_text
from eu5miner.mods import (
    AppliedModUpdate,
    PlannedModUpdate,
    apply_mod_update,
    format_mod_update_report,
    plan_mod_update,
)
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
    if command == "list-systems":
        return _run_list_systems()
    if command == "analyze-script":
        return _run_analyze_script(args)
    if command == "report-system":
        return _run_report_system(args)
    if command == "plan-mod-update":
        return _run_plan_mod_update(args)
    if command == "apply-mod-update":
        return _run_apply_mod_update(args)

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

    subparsers.add_parser(
        "list-systems",
        help="List the major system reports available in the CLI.",
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

    report_parser = subparsers.add_parser(
        "report-system",
        help="Build a higher-level report for a major implemented system.",
    )
    report_parser.add_argument(
        "--system",
        choices=[info.name for info in list_systems()],
        required=True,
        help="Major system to summarize.",
    )
    report_parser.add_argument(
        "--language",
        default="english",
        help="Localization language to use for interface reports. Defaults to english.",
    )

    plan_parser = subparsers.add_parser(
        "plan-mod-update",
        help=(
            "Dry-run a mod subtree update and report planned writes, "
            "metadata actions, and warnings."
        ),
    )
    plan_parser.add_argument(
        "--mod-root",
        type=Path,
        required=True,
        help="Root path for the target mod to plan.",
    )
    plan_parser.add_argument(
        "--later-mod-root",
        action="append",
        type=Path,
        default=[],
        help=(
            "Additional mod roots loaded after the target mod; "
            "repeat to model higher-priority mods."
        ),
    )
    plan_parser.add_argument(
        "--phase",
        type=_parse_phase,
        required=True,
        help="Content phase to plan: loading_screen, main_menu, or in_game.",
    )
    plan_parser.add_argument(
        "--subtree",
        required=True,
        help="Relative subtree root beneath the chosen phase, for example common/buildings.",
    )
    plan_parser.add_argument(
        "--intended-path",
        action="append",
        default=[],
        help="Relative file path to emit beneath the chosen phase; repeat for multiple outputs.",
    )
    plan_parser.add_argument(
        "--content-root",
        action="append",
        type=Path,
        default=[],
        help=(
            "Recursively include all files under a content root using their "
            "paths relative to that root."
        ),
    )

    apply_parser = subparsers.add_parser(
        "apply-mod-update",
        help=("Apply a mod subtree update, materialize files, and report notes and warnings."),
    )
    apply_parser.add_argument(
        "--mod-root",
        type=Path,
        required=True,
        help="Root path for the target mod to update.",
    )
    apply_parser.add_argument(
        "--later-mod-root",
        action="append",
        type=Path,
        default=[],
        help=(
            "Additional mod roots loaded after the target mod; "
            "repeat to model higher-priority mods."
        ),
    )
    apply_parser.add_argument(
        "--phase",
        type=_parse_phase,
        required=True,
        help="Content phase to update: loading_screen, main_menu, or in_game.",
    )
    apply_parser.add_argument(
        "--subtree",
        required=True,
        help="Relative subtree root beneath the chosen phase, for example common/buildings.",
    )
    apply_parser.add_argument(
        "--intended-path",
        action="append",
        default=[],
        help="Relative file path to emit beneath the chosen phase; repeat for multiple outputs.",
    )
    apply_parser.add_argument(
        "--content-file",
        action="append",
        default=[],
        help=(
            "Map one emitted relative path to a source file using "
            "relative/path=source-file.txt; repeat for multiple files."
        ),
    )
    apply_parser.add_argument(
        "--content-root",
        action="append",
        type=Path,
        default=[],
        help=(
            "Recursively include all files under a content root using their "
            "paths relative to that root."
        ),
    )
    apply_parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Refuse to overwrite existing files when the content differs.",
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


def _run_list_systems() -> int:
    print("Supported system reports:")
    for info in list_systems():
        print(f"- {info.name}: {info.description}")
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
    print(f"top_level_entry_count: {len(document.entries)}")
    print(f"cst_brace_balanced: {document.is_brace_balanced}")
    return 0


def _run_report_system(args: argparse.Namespace) -> int:
    install = GameInstall.discover(args.install_root)
    report = build_system_report(install, args.system, language=args.language)
    print(format_system_report(report))
    return 0


def _run_plan_mod_update(args: argparse.Namespace) -> int:
    try:
        update = _plan_cli_mod_update(args)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(format_mod_update_report(update))
    _emit_update_diagnostics(update)

    return 0


def _run_apply_mod_update(args: argparse.Namespace) -> int:
    try:
        update = _plan_cli_mod_update(args)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        applied_update = apply_mod_update(update, overwrite=not args.no_overwrite)
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(format_mod_update_report(applied_update))
    _emit_update_diagnostics(applied_update.plan)
    return 0


def _plan_cli_mod_update(args: argparse.Namespace) -> PlannedModUpdate:
    install = GameInstall.discover(args.install_root)
    mod_roots = [args.mod_root, *args.later_mod_root]
    vfs = VirtualFilesystem.from_install(install, mod_roots=mod_roots)
    content_mapping = _parse_content_file_mappings(getattr(args, "content_file", []))
    content_mapping.update(_collect_content_root_files(args.content_root))
    intended_paths = tuple(Path(path) for path in args.intended_path)
    content_paths = tuple(content_mapping)

    if not intended_paths and not content_paths:
        raise ValueError(
            "At least one --intended-path, --content-file, or --content-root entry is required"
        )

    return plan_mod_update(
        vfs,
        args.mod_root.name,
        args.phase,
        Path(args.subtree),
        intended_relative_paths=intended_paths + content_paths,
        content_by_relative_path=_read_content_mapping(content_mapping),
    )


def _emit_update_diagnostics(update: PlannedModUpdate | AppliedModUpdate) -> None:
    for advisory in update.advisories:
        print(f"note: {advisory.message}", file=sys.stderr)
    for warning in update.warnings:
        print(f"warning: {warning.message}", file=sys.stderr)


def _parse_content_file_mappings(values: list[str]) -> dict[Path, Path]:
    mappings: dict[Path, Path] = {}
    for value in values:
        relative_text, separator, source_text = value.partition("=")
        if not separator or not relative_text or not source_text:
            raise ValueError(
                "Content file mappings must use the form relative/path=source-file.txt"
            )
        mappings[Path(relative_text)] = Path(source_text)
    return mappings


def _collect_content_root_files(content_roots: list[Path]) -> dict[Path, Path]:
    mappings: dict[Path, Path] = {}
    for root in content_roots:
        if not root.exists():
            raise FileNotFoundError(f"Content root does not exist: {root}")
        if not root.is_dir():
            raise ValueError(f"Content root is not a directory: {root}")
        for source_path in sorted(path for path in root.rglob("*") if path.is_file()):
            relative_path = source_path.relative_to(root)
            mappings[relative_path] = source_path
    return mappings


def _read_content_mapping(
    content_files: dict[Path, Path],
) -> Mapping[str | Path, str] | None:
    if not content_files:
        return None
    missing_sources = [path for path in content_files.values() if not path.exists()]
    if missing_sources:
        missing_text = ", ".join(str(path) for path in missing_sources)
        raise FileNotFoundError(f"Content source file is missing: {missing_text}")
    return {
        relative_path: source_path.read_text(encoding="utf-8", errors="replace")
        for relative_path, source_path in content_files.items()
    }


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
