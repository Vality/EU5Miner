from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import eu5miner.inspection as inspection
from eu5miner import SourceKind


@dataclass(frozen=True)
class FakeInstall:
    root: Path
    game_dir: Path
    dlc_dir: Path
    mod_dir: Path


@dataclass
class FakeInspection:
    root: Path
    auto_discover_error: Exception | None = None
    manual_discover_error: Exception | None = None
    summarize_calls: list[tuple[Path, tuple[Path, ...]]] = field(default_factory=list)
    detail_calls: list[tuple[str, str]] = field(default_factory=list)

    def discover(self, root: Path | None = None) -> FakeInstall:
        if root is None and self.auto_discover_error is not None:
            raise self.auto_discover_error
        if root is not None and self.manual_discover_error is not None:
            raise self.manual_discover_error
        actual_root = self.root if root is None else Path(root)
        return FakeInstall(
            root=actual_root,
            game_dir=actual_root / "game",
            dlc_dir=actual_root / "game" / "dlc",
            mod_dir=actual_root / "game" / "mod",
        )

    def list_supported_systems(self) -> tuple[inspection.SystemInfo, ...]:
        return (
            inspection.SystemInfo(name="economy", description="Economy report"),
            inspection.SystemInfo(name="religion", description="Religion report"),
            inspection.SystemInfo(name="map", description="Map report"),
        )

    def list_entity_systems(self) -> tuple[inspection.EntitySystemInfo, ...]:
        return (
            inspection.EntitySystemInfo(
                name="economy",
                description="Browse economy entities",
                primary_entity_kind="good",
            ),
            inspection.EntitySystemInfo(
                name="religion",
                description="Browse religion entities",
                primary_entity_kind="religion",
            ),
        )

    def summarize_install(
        self,
        install: FakeInstall,
        *,
        mod_roots: tuple[Path, ...] | None = None,
    ) -> inspection.InstallSummary:
        normalized_mod_roots = tuple(mod_roots or ())
        self.summarize_calls.append((install.root, normalized_mod_roots))
        sources = [
            inspection.InstallSourceSummary(
                name="base",
                kind=SourceKind.VANILLA,
                root=install.game_dir,
                priority=0,
                replace_paths=(),
            )
        ]
        for index, mod_root in enumerate(normalized_mod_roots, start=1):
            sources.append(
                inspection.InstallSourceSummary(
                    name=mod_root.name,
                    kind=SourceKind.MOD,
                    root=mod_root,
                    priority=index,
                    replace_paths=("common/religions",) if index == 1 else (),
                )
            )
        return inspection.InstallSummary(
            root=install.root,
            game_dir=install.game_dir,
            dlc_dir=install.dlc_dir,
            mod_dir=install.mod_dir,
            phase_roots=(),
            sources=tuple(sources),
        )

    def get_system_report(
        self,
        install: FakeInstall,
        system: str,
        *,
        language: str = "english",
    ) -> inspection.SystemReport:
        if system == "map":
            return inspection.SystemReport(
                name="map",
                description="Map report",
                representative_keys=("map_default",),
                summary_lines=("Province definitions: 2", "Location setup links: 1"),
            )
        return inspection.SystemReport(
            name=system,
            description=f"{system} report",
            representative_keys=(f"{system}_sample",),
            summary_lines=(f"{system.title()} definitions: 3",),
        )

    def list_system_entities(
        self,
        install: FakeInstall,
        system: str,
        *,
        mod_roots: tuple[Path, ...] | None = None,
    ) -> tuple[inspection.EntitySummary, ...]:
        if system == "economy":
            return (
                inspection.EntitySummary(
                    system="economy",
                    entity_kind="good",
                    name="grain",
                    group="food",
                    description="market staple",
                ),
                inspection.EntitySummary(
                    system="economy",
                    entity_kind="good",
                    name="iron",
                    group="raw_material",
                    description="tooling input",
                ),
            )
        return tuple(
            inspection.EntitySummary(
                system="religion",
                entity_kind="religion",
                name=f"faith_{index:02d}",
                group="group",
                description=f"faith description {index:02d}",
            )
            for index in range(1, 13)
        )

    def get_system_entity(
        self,
        install: FakeInstall,
        system: str,
        name: str,
        *,
        mod_roots: tuple[Path, ...] | None = None,
    ) -> inspection.EntityDetail:
        self.detail_calls.append((system, name))
        references = ()
        if system == "religion":
            references = (
                inspection.EntityReference(
                    role="related good",
                    system="economy",
                    entity_kind="good",
                    target_name="iron",
                ),
            )
        return inspection.EntityDetail(
            summary=inspection.EntitySummary(
                system=system,
                entity_kind="religion" if system == "religion" else "good",
                name=name,
                group="group",
                description="detail",
            ),
            fields=(
                inspection.EntityField(name="strength", value=2),
                inspection.EntityField(name="enabled", value=True),
            ),
            references=references,
        )


def diplomacy_helper_view() -> SimpleNamespace:
    return SimpleNamespace(
        info=SimpleNamespace(
            name="war-flow",
            title="war-flow helper report",
            description="Diplomacy helper",
        ),
        sections=(
            SimpleNamespace(
                title="Coverage summary",
                lines=("Casus belli definitions: 5", "Wargoal definitions: 1"),
            ),
            SimpleNamespace(
                title="Representative links",
                lines=("Casus belli -> wargoal: cb_conquest -> sample_goal",),
            ),
        ),
        navigation_hints=(),
    )


def religion_helper_view() -> SimpleNamespace:
    return SimpleNamespace(
        info=SimpleNamespace(
            name="religion-overview",
            title="religion-overview helper report",
            description="Religion helper",
        ),
        sections=(
            SimpleNamespace(
                title="Coverage summary",
                lines=("Religion definitions: 5", "Religion -> school links: 3"),
            ),
            SimpleNamespace(
                title="Representative links",
                lines=("Religion -> school: sunni -> sample_school",),
            ),
        ),
        navigation_hints=(),
    )
