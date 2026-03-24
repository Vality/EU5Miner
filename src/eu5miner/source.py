"""Source discovery and initial phase-aware file enumeration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from eu5miner.paths import resolve_install_path


class ContentPhase(StrEnum):
    """Known EU5 content loading phases."""

    LOADING_SCREEN = "loading_screen"
    MAIN_MENU = "main_menu"
    IN_GAME = "in_game"


@dataclass(frozen=True)
class GameInstall:
    """Discovered structure for a local EU5 installation."""

    root: Path
    game_dir: Path
    dlc_dir: Path
    mod_dir: Path

    @classmethod
    def discover(cls, root: str | Path | None = None) -> GameInstall:
        install_root = resolve_install_path(root)
        game_dir = install_root / "game"
        dlc_dir = game_dir / "dlc"
        mod_dir = game_dir / "mod"

        required_paths = [
            install_root,
            game_dir,
            game_dir / ContentPhase.LOADING_SCREEN.value,
            game_dir / ContentPhase.MAIN_MENU.value,
            game_dir / ContentPhase.IN_GAME.value,
        ]
        missing = [path for path in required_paths if not path.exists()]
        if missing:
            missing_text = ", ".join(str(path) for path in missing)
            raise FileNotFoundError(f"EU5 install is missing expected paths: {missing_text}")

        return cls(root=install_root, game_dir=game_dir, dlc_dir=dlc_dir, mod_dir=mod_dir)

    def phase_dir(self, phase: ContentPhase) -> Path:
        return self.game_dir / phase.value

    def iter_phase_files(
        self,
        phase: ContentPhase,
        relative_subpath: str | Path = "",
    ) -> list[Path]:
        base_dir = self.phase_dir(phase)
        search_root = base_dir / Path(relative_subpath)
        if not search_root.exists():
            return []
        return sorted(path for path in search_root.rglob("*") if path.is_file())

    def representative_files(self) -> dict[str, Path]:
        return {
            "events_readme": self.phase_dir(ContentPhase.IN_GAME) / "events" / "readme.txt",
            "event_sample": self.phase_dir(ContentPhase.IN_GAME) / "events" / "civil_war.txt",
            "mission_readme": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "missions"
            / "____Info.txt",
            "mission_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "missions"
            / "generic_conquer_province_mission_pack.txt",
            "situation_readme": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "situations"
            / "readme.txt",
            "situation_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "situations"
            / "black_death.txt",
            "disaster_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "disasters"
            / "english_civil_war.txt",
            "customizable_localization_info": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "customizable_localization"
            / "customizable_localization.info",
            "customizable_localization_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "customizable_localization"
            / "00_customizable_localization.txt",
            "effect_localization_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "effect_localization"
            / "country_effects.txt",
            "trigger_localization_info": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "trigger_localization"
            / "_trigger_localization.info",
            "trigger_localization_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "trigger_localization"
            / "country_triggers.txt",
            "english_effects_localization": self.phase_dir(ContentPhase.MAIN_MENU)
            / "localization"
            / "english"
            / "effects_l_english.yml",
            "english_triggers_localization": self.phase_dir(ContentPhase.MAIN_MENU)
            / "localization"
            / "english"
            / "triggers_l_english.yml",
            "english_laws_localization": self.phase_dir(ContentPhase.MAIN_MENU)
            / "localization"
            / "english"
            / "laws_and_policies_l_english.yml",
            "scripted_trigger": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "scripted_triggers"
            / "country_triggers.txt",
            "scripted_effect": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "scripted_effects"
            / "country_effects.txt",
            "setup_country_readme": self.phase_dir(ContentPhase.IN_GAME)
            / "setup"
            / "countries"
            / "00_readme.info",
            "setup_country_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "setup"
            / "countries"
            / "france.txt",
            "gui_sample": self.phase_dir(ContentPhase.IN_GAME) / "gui" / "agenda_view.gui",
            "gui_types_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "gui"
            / "eventwindow.gui",
            "gui_library_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "gui"
            / "ui_library.gui",
            "main_menu_scenarios_sample": self.phase_dir(ContentPhase.MAIN_MENU)
            / "common"
            / "scenarios"
            / "00_scenarios.txt",
            "loading_screen_localization_sample": self.phase_dir(ContentPhase.LOADING_SCREEN)
            / "localization"
            / "english"
            / "load_tips_l_english.yml",
            "map_default": self.phase_dir(ContentPhase.IN_GAME) / "map_data" / "default.map",
            "map_adjacencies": self.phase_dir(ContentPhase.IN_GAME)
            / "map_data"
            / "adjacencies.csv",
            "map_ports": self.phase_dir(ContentPhase.IN_GAME) / "map_data" / "ports.csv",
            "localization_sample": self.phase_dir(ContentPhase.MAIN_MENU)
            / "localization"
            / "english"
            / "actions_l_english.yml",
            "dlc_metadata": self.dlc_dir / "D000_shared" / "D000_shared.dlc.json",
        }
