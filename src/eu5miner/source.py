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
            "scripted_modifier_info": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "scripted_modifiers"
            / "scripted_modifiers.info",
            "scripted_list_info": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "scripted_lists"
            / "scripted_lists.info",
            "scripted_list_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "scripted_lists"
            / "country_lists.txt",
            "scripted_relation_readme": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "scripted_relations"
            / "readme.txt",
            "scripted_relation_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "scripted_relations"
            / "alliance.txt",
            "scripted_relation_secondary_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "scripted_relations"
            / "trade_access.txt",
            "on_action_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "on_action"
            / "religion_flavor_pulse.txt",
            "on_action_secondary_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "on_action"
            / "character_death_pulses.txt",
            "on_action_hardcoded_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "on_action"
            / "_hardcoded.txt",
            "script_value_info": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "script_values"
            / "_script_values.info",
            "script_value_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "script_values"
            / "best_capital_for_colony.txt",
            "script_value_scalar_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "script_values"
            / "eu4_conversions.txt",
            "building_type_readme": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "building_types"
            / "readme.txt",
            "building_type_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "building_types"
            / "common_buildings.txt",
            "building_type_secondary_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "building_types"
            / "capital_buildings.txt",
            "building_category_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "building_categories"
            / "00_default.txt",
            "goods_readme": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "goods"
            / "readme.txt",
            "goods_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "goods"
            / "00_raw_materials.txt",
            "goods_secondary_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "goods"
            / "03_food.txt",
            "price_readme": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "prices"
            / "readme.txt",
            "price_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "prices"
            / "00_hardcoded.txt",
            "price_secondary_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "prices"
            / "01_buildings.txt",
            "goods_demand_category_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "goods_demand_category"
            / "00_default.txt",
            "goods_demand_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "goods_demand"
            / "building_construction_costs.txt",
            "goods_demand_secondary_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "goods_demand"
            / "pop_demands.txt",
            "goods_demand_tertiary_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "goods_demand"
            / "from_events.txt",
            "culture_info": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "cultures"
            / "00_cultures.info",
            "culture_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "cultures"
            / "british.txt",
            "religion_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "religions"
            / "christian.txt",
            "religion_secondary_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "religions"
            / "buddhist.txt",
            "country_description_category_readme": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "country_description_categories"
            / "readme.txt",
            "country_description_category_sample": self.phase_dir(ContentPhase.IN_GAME)
            / "common"
            / "country_description_categories"
            / "categories.txt",
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
            "main_menu_country_setup_sample": self.phase_dir(ContentPhase.MAIN_MENU)
            / "setup"
            / "start"
            / "10_countries.txt",
            "main_menu_location_setup_sample": self.phase_dir(ContentPhase.MAIN_MENU)
            / "setup"
            / "start"
            / "21_locations.txt",
            "loading_screen_localization_sample": self.phase_dir(ContentPhase.LOADING_SCREEN)
            / "localization"
            / "english"
            / "load_tips_l_english.yml",
            "map_default": self.phase_dir(ContentPhase.IN_GAME) / "map_data" / "default.map",
            "map_definitions": self.phase_dir(ContentPhase.IN_GAME)
            / "map_data"
            / "definitions.txt",
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
