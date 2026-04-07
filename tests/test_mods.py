from __future__ import annotations

from pathlib import Path

from eu5miner import apply_mod_update, format_mod_update_report, plan_mod_update
from eu5miner.inspection import list_system_entities
from eu5miner.mods import ModUpdateAdvisoryKind, ModUpdateWarningKind, ModUpdateWriteKind
from eu5miner.source import ContentPhase
from eu5miner.vfs import ContentSource, SourceKind, VirtualFilesystem
from tests.integration_support import build_synthetic_install


def _write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_plan_mod_update_wraps_metadata_and_content_writes(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])

    update = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    assert update.metadata_write.kind is ModUpdateWriteKind.METADATA
    assert update.metadata_write.path == mod_root / ".metadata" / "metadata.json"
    assert update.metadata_write.content == "{}\n"
    assert len(update.content_writes) == 1
    assert update.content_writes[0].kind is ModUpdateWriteKind.CONTENT
    assert update.content_writes[0].relative_path == Path("common") / "buildings" / "new.txt"
    assert update.content_writes[0].content == "building = {}\n"
    assert update.replace_paths_to_add == ()
    assert update.blocked_emissions == ()
    assert update.warnings == ()
    assert update.advisories == ()


def test_plan_mod_update_surfaces_replace_path_recommendations(tmp_path: Path) -> None:
    vanilla_root = tmp_path / "vanilla"
    mod_root = tmp_path / "my_mod"

    _write_file(vanilla_root / "in_game" / "common" / "buildings" / "a.txt", "vanilla\n")

    vfs = VirtualFilesystem(
        [
            ContentSource("vanilla", SourceKind.VANILLA, vanilla_root, 0),
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
        ]
    )

    update = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "a.txt",),
        content_by_relative_path={"common/buildings/a.txt": "modded\n"},
    )

    assert update.replace_paths_to_add == ("game/in_game/common/buildings",)
    assert len(update.advisories) == 1
    assert update.advisories[0].kind is ModUpdateAdvisoryKind.ADD_REPLACE_PATH
    assert update.advisories[0].raw_path == "game/in_game/common/buildings"
    assert update.content_writes[0].relative_path == Path("common") / "buildings" / "a.txt"
    assert update.content_writes[0].content == "modded\n"

    report = format_mod_update_report(update)

    assert "Summary:" in report
    assert "intended content outputs: 1" in report
    assert "materialized writes: 2" in report
    assert "replace_path additions: 1" in report
    assert "blocked intended outputs: 0" in report
    assert "advisories: 1" in report
    assert "Metadata replace_path additions:" in report
    assert "Advisories:" in report
    assert "Planning metadata update to add replace_path entry:" in report
    assert "game/in_game/common/buildings" in report
    assert "override: common/buildings/a.txt" in report


def test_plan_mod_update_surfaces_blocked_emissions(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    late_mod_root = tmp_path / "late_mod"

    _write_file(late_mod_root / "in_game" / "common" / "buildings" / "a.txt", "late\n")

    vfs = VirtualFilesystem(
        [
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
            ContentSource("late_mod", SourceKind.MOD, late_mod_root, 110),
        ]
    )

    update = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "a.txt",),
    )

    assert len(update.blocked_emissions) == 1
    assert update.blocked_emissions[0].relative_path == Path("common") / "buildings" / "a.txt"
    assert update.blocked_emissions[0].blocker_source_names == ("late_mod",)
    assert len(update.warnings) == 1
    assert update.warnings[0].kind is ModUpdateWarningKind.BLOCKED_EMISSION
    assert update.warnings[0].relative_path == Path("common") / "buildings" / "a.txt"
    assert update.warnings[0].blocker_source_names == ("late_mod",)
    assert update.content_writes == ()

    report = format_mod_update_report(update)

    assert "Summary:" in report
    assert "intended content outputs: 1" in report
    assert "materialized writes: 1" in report
    assert "blocked intended outputs: 1" in report
    assert "warnings: 1" in report
    assert "advisories: 0" in report
    assert "Warnings:" in report
    assert "common/buildings/a.txt will be shadowed" in report
    assert "late_mod" in report


def test_apply_mod_update_materializes_files_and_reports_statuses(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])

    planned = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "building = {}\n"},
    )

    applied = apply_mod_update(planned)

    assert applied.metadata_write.kind is ModUpdateWriteKind.METADATA
    assert applied.metadata_write.path.read_text(encoding="utf-8") == "{}\n"
    assert len(applied.content_writes) == 1
    assert applied.content_writes[0].path.read_text(encoding="utf-8") == "building = {}\n"

    report = format_mod_update_report(applied)

    assert "Applied mod update: my_mod" in report
    assert "Summary:" in report
    assert "created directories:" in report
    assert "created writes: 2" in report
    assert "updated writes: 0" in report
    assert "unchanged writes: 0" in report
    assert "advisories: 0" in report
    assert "created:" in report
    assert "metadata.json" in report
    assert "new.txt" in report


def test_apply_mod_update_preserves_warnings_for_blocked_outputs(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    late_mod_root = tmp_path / "late_mod"

    _write_file(late_mod_root / "in_game" / "common" / "buildings" / "a.txt", "late\n")

    vfs = VirtualFilesystem(
        [
            ContentSource("my_mod", SourceKind.MOD, mod_root, 100),
            ContentSource("late_mod", SourceKind.MOD, late_mod_root, 110),
        ]
    )

    planned = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "a.txt",),
    )

    applied = apply_mod_update(planned)

    assert len(applied.warnings) == 1
    assert applied.warnings[0].kind is ModUpdateWarningKind.BLOCKED_EMISSION
    assert applied.content_writes == ()

    report = format_mod_update_report(applied)

    assert "Summary:" in report
    assert "blocked intended outputs: 1" in report
    assert "warnings: 1" in report
    assert "Warnings:" in report
    assert "common/buildings/a.txt will be shadowed" in report


def test_apply_mod_update_reports_updated_and_unchanged_write_counts(tmp_path: Path) -> None:
    mod_root = tmp_path / "my_mod"
    target_path = mod_root / "in_game" / "common" / "buildings" / "new.txt"

    _write_file(mod_root / ".metadata" / "metadata.json", "{}\n")
    _write_file(target_path, "old\n")

    vfs = VirtualFilesystem([ContentSource("my_mod", SourceKind.MOD, mod_root, 100)])
    planned = plan_mod_update(
        vfs,
        "my_mod",
        ContentPhase.IN_GAME,
        Path("common") / "buildings",
        intended_relative_paths=(Path("common") / "buildings" / "new.txt",),
        content_by_relative_path={Path("common") / "buildings" / "new.txt": "new\n"},
    )

    applied = apply_mod_update(planned)

    assert planned.metadata_write.existed is True
    assert planned.content_writes[0].existed is True
    assert applied.created_directories == ()
    assert applied.created_write_count == 0
    assert applied.updated_write_count == 1
    assert applied.unchanged_write_count == 1
    assert applied.metadata_write.path.read_text(encoding="utf-8") == "{}\n"
    assert applied.content_writes[0].path.read_text(encoding="utf-8") == "new\n"

    report = format_mod_update_report(applied)

    assert "created writes: 0" in report
    assert "updated writes: 1" in report
    assert "unchanged writes: 1" in report
    assert "updated:" in report
    assert "unchanged:" in report


def test_apply_mod_update_invalidates_matching_entity_cache(tmp_path: Path) -> None:
    install = _build_economy_entity_install(tmp_path / "economy")
    mod_root = tmp_path / "my_mod"
    relative_path = Path("common") / "goods" / "coal.txt"
    vfs = VirtualFilesystem.from_install(install, mod_roots=[mod_root])

    before = list_system_entities(install, "economy", mod_roots=[mod_root])
    planned = plan_mod_update(
        vfs,
        mod_root.name,
        ContentPhase.IN_GAME,
        Path("common") / "goods",
        intended_relative_paths=(relative_path,),
        content_by_relative_path={
            relative_path: (
                "coal = { method = mining category = raw_material default_market_price = 5 }\n"
            )
        },
    )

    apply_mod_update(planned)
    after = list_system_entities(install, "economy", mod_roots=[mod_root])

    assert all(summary.name != "coal" for summary in before)
    assert any(summary.name == "coal" for summary in after)


def _build_economy_entity_install(root: Path):
    install = build_synthetic_install(root / "install")
    representative_files = install.representative_files()
    fixture_texts = {
        "goods_sample": (
            "iron = {\n"
            "    method = mining\n"
            "    category = raw_material\n"
            "    default_market_price = 3\n"
            "}\n"
        ),
        "goods_secondary_sample": "grain = { method = farming category = food }\n",
        "price_sample": "build_road = { gold = 10 }\n",
        "price_secondary_sample": "granary = { tools = 5 }\n",
        "generic_action_market_sample": (
            "create_market = {\n"
            "    type = owncountry\n"
            "    select_trigger = { looking_for_a = market }\n"
            "}\n"
        ),
        "generic_action_secondary_sample": (
            "open_employment = {\n"
            "    type = owncountry\n"
            "    select_trigger = { looking_for_a = employment_system }\n"
            "}\n"
        ),
        "generic_action_loan_sample": (
            "take_loan = {\n"
            "    type = owncountry\n"
            "    select_trigger = { looking_for_a = bank_loan }\n"
            "}\n"
        ),
        "attribute_column_default_sample": (
            "defaults = { name = { widget = default_text_column } }\n"
        ),
        "attribute_column_market_sample": (
            "market = { name = { widget = default_text_column } }\n"
        ),
        "attribute_column_trade_sample": (
            "trade = { route = { widget = default_text_column } }\n"
        ),
        "attribute_column_secondary_sample": (
            "goods = { price = { widget = default_numeric_column } }\n"
        ),
        "attribute_column_loan_sample": (
            "loan = { size = { widget = default_numeric_column } }\n"
        ),
    }

    for key, text in fixture_texts.items():
        _write_file(representative_files[key], text)

    return install
