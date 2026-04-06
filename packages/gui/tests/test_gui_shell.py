from __future__ import annotations

from pathlib import Path

from eu5miner_gui.__main__ import main as package_main
from eu5miner_gui.app import build_shell_message
from eu5miner_gui.browser import build_browser_model, parse_browser_page_selection
from eu5miner_gui.cli import main


def test_build_shell_message_lists_supported_systems_without_install() -> None:
    message = build_shell_message()

    assert "EU5MinerGUI read-only browser ready." in message
    assert "Available pages:" in message
    assert "* overview: Install overview" in message
    assert "== Install overview ==" in message
    assert "Supported systems:" in message
    assert "Browsable entity systems:" in message
    assert "- map: Map text, map CSV, and linked setup-location coverage." in message
    assert (
        "- economy: good - Browse goods definitions with market-facing fields and related "
        "good links." in message
    )
    assert "Install summary:" in message
    assert "- Not loaded." in message


def test_build_browser_model_with_selected_system_builds_overview_and_report_pages(
    tmp_path: Path,
) -> None:
    install_root = _make_report_install(tmp_path / "install")

    model = build_browser_model(install_root, selected_system="map")

    assert model.selected_page_key == "report:map"
    assert model.page_keys() == ("overview", "report:map")
    assert model.pages[1].title == "map system report"
    assert model.pages[1].status == "ready"
    assert model.pages[1].sections[1].lines[0] == "default.map referenced files: 2"
    assert any(
        line.startswith("location hierarchy definitions:")
        for line in model.pages[1].sections[1].lines
    )


def test_parse_browser_page_selection_supports_aliases() -> None:
    assert parse_browser_page_selection("home").page_key == "overview"
    assert parse_browser_page_selection("system:map").page_key == "report:map"
    assert parse_browser_page_selection("list:religion").page_key == "entities:religion"

    detail_selection = parse_browser_page_selection("detail:map:stockholm")

    assert detail_selection.page_key == "entity:map:stockholm"
    assert detail_selection.selected_entity_system == "map"
    assert detail_selection.selected_entity_name == "stockholm"


def test_build_browser_model_with_all_systems_loads_all_report_pages(tmp_path: Path) -> None:
    install_root = _make_report_install(tmp_path / "install")

    model = build_browser_model(install_root, include_all_systems=True)

    assert model.selected_page_key == "overview"
    assert model.page_keys() == (
        "overview",
        "report:economy",
        "report:diplomacy",
        "report:government",
        "report:religion",
        "report:interface",
        "report:map",
        "entities:economy",
        "entities:government",
        "entities:religion",
        "entities:map",
    )
    assert "Loaded pages: 11 total, 3 ready, 8 unavailable" in model.pages[0].sections[0].lines
    assert "Ready report pages: report:map" in model.pages[0].sections[0].lines
    assert (
        "Unavailable report pages: report:economy, report:diplomacy, report:government, "
        "report:religion, report:interface"
    ) in model.pages[0].sections[0].lines
    assert "Ready entity list pages: entities:map" in model.pages[0].sections[0].lines
    assert (
        "Unavailable entity list pages: entities:economy, entities:government, "
        "entities:religion"
    )
    assert model.pages[1].status == "unavailable"
    assert model.pages[-1].status == "ready"


def test_build_browser_model_with_selected_entity_system_builds_list_page(tmp_path: Path) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    model = build_browser_model(install_root, selected_entity_system="religion")

    assert model.selected_page_key == "entities:religion"
    assert model.page_keys() == ("overview", "entities:religion")
    assert model.pages[1].title == "religion entities"
    assert model.pages[1].status == "ready"
    assert model.pages[1].sections[0].lines == (
        "Primary entity kind: religion",
        "Entity count: 2",
        "Sort: name",
        "List mode: compact",
        "Entity window: showing 1-2 of 2",
    )
    assert (
        "Visible detail-page examples: entity:religion:catholic, "
        "entity:religion:orthodox"
    ) in model.pages[1].navigation_hints
    assert any(
        line.startswith("catholic [christian]:") for line in model.pages[1].sections[1].lines
    )


def test_build_browser_model_requires_entity_system_for_entity_name(tmp_path: Path) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    try:
        build_browser_model(install_root, selected_entity_name="stockholm")
    except ValueError as exc:
        assert str(exc) == "An entity name requires a selected entity system."
    else:
        raise AssertionError("Expected ValueError for missing selected_entity_system")


def test_build_browser_model_with_selected_entity_name_builds_detail_page(
    tmp_path: Path,
) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    model = build_browser_model(
        install_root,
        selected_entity_system="map",
        selected_entity_name="stockholm",
    )

    assert model.selected_page_key == "entity:map:stockholm"
    assert model.page_keys() == (
        "overview",
        "entities:map",
        "entity:map:stockholm",
    )
    assert model.pages[2].title == "stockholm location"
    assert "hierarchy_path: world, region, area, province" in model.pages[2].sections[1].lines
    assert "country_reference -> map/country: SWE" in model.pages[2].sections[2].lines


def test_build_browser_model_entity_pages_cover_curated_systems(tmp_path: Path) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    expectations = {
        "economy": (
            "iron [raw_material]: method=mining; default_market_price=3",
            "default_market_price: 3",
            "demand_add -> economy/good: grain",
        ),
        "government": (
            "monarchy [legitimacy]: default_estate=sample_estate; heir_selections=1",
            "government_power: legitimacy",
            "default_estate -> government/estate: sample_estate",
        ),
        "religion": (
            "catholic [christian]: focuses=1",
            "group: christian",
            "religious_focus -> religion/religious_focus: sample_focus",
        ),
        "map": (
            "stockholm [province]: capital_of=SWE; setup=yes",
            "has_location_setup: yes",
            "capital_of -> map/country: SWE",
        ),
    }

    for system, (summary_line, field_line, reference_line) in expectations.items():
        model = build_browser_model(
            install_root,
            selected_entity_system=system,
            selected_entity_name=_first_entity_name_for(system),
        )
        assert summary_line in model.pages[1].sections[1].lines
        assert field_line in model.pages[2].sections[1].lines
        assert reference_line in model.pages[2].sections[2].lines


def test_build_browser_model_entity_list_sorts_by_name_by_default(tmp_path: Path) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    model = build_browser_model(install_root, selected_entity_system="economy")

    assert model.pages[1].sections[1].lines[0].startswith("grain")
    assert model.pages[1].sections[1].lines[1].startswith("iron")


def test_build_browser_model_entity_list_can_sort_by_group(tmp_path: Path) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    model = build_browser_model(
        install_root,
        selected_entity_system="economy",
        entity_list_sort="group",
    )

    assert model.pages[1].sections[0].lines[2] == "Sort: group"
    assert model.pages[1].sections[1].lines[0].startswith("grain")
    assert model.pages[1].sections[1].lines[1].startswith("iron")


def test_build_shell_message_entity_list_window_and_detail_mode(tmp_path: Path) -> None:
    install_root = _make_large_entity_browsing_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        selected_entity_system="religion",
        entity_list_mode="detail",
        entity_list_limit=3,
        entity_list_offset=4,
    )

    assert "== religion entities ==" in message
    assert "- Sort: name" in message
    assert "- List mode: detail" in message
    assert "- Entity window: showing 5-7 of 12" in message
    assert "- faith_05 [group] | page: entity:religion:faith_05" in message
    assert "- faith_07 [group] | page: entity:religion:faith_07" in message
    assert "- faith_08 [group] | page: entity:religion:faith_08" not in message
    assert (
        "- Visible detail-page examples: entity:religion:faith_05, "
        "entity:religion:faith_06, entity:religion:faith_07"
    ) in message


def test_cli_main_returns_zero(capsys) -> None:
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "EU5MinerGUI read-only browser ready." in captured.out
    assert "Available pages:" in captured.out


def test_package_main_returns_zero(capsys) -> None:
    assert package_main([]) == 0
    captured = capsys.readouterr()
    assert "EU5MinerGUI read-only browser ready." in captured.out
    assert "Available pages:" in captured.out


def test_cli_selected_system_report_from_synthetic_install(tmp_path: Path, capsys) -> None:
    install_root = _make_report_install(tmp_path / "install")

    exit_code = main(["--install-root", str(install_root), "--system", "map"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Selected page: report:map" in captured.out
    assert "* report:map: map system report" in captured.out
    assert "== map system report ==" in captured.out
    assert "Navigation:" in captured.out
    assert "- Page key: report:map" in captured.out
    assert "- Direct page flag: --page report:map" in captured.out
    assert "- Selection flags: --system map" in captured.out
    assert "- Session position: 2 of 2 loaded pages" in captured.out
    assert "- Previous page: overview" in captured.out
    assert "- Overview page: overview" in captured.out
    assert "Representative files:" in captured.out
    assert "- map_default" in captured.out
    assert "- default.map referenced files: 2" in captured.out
    assert "- location hierarchy definitions: 2" in captured.out


def test_cli_all_systems_from_synthetic_install(tmp_path: Path, capsys) -> None:
    install_root = _make_report_install(tmp_path / "install")

    exit_code = main(["--install-root", str(install_root), "--all-systems"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Selected page: overview" in captured.out
    assert "* overview: Install overview" in captured.out
    assert "- report:economy: economy system report (unavailable)" in captured.out
    assert "- report:map: map system report" in captured.out
    assert "- entities:map: map entities" in captured.out
    assert "== Install overview ==" in captured.out
    assert "== economy system report ==" not in captured.out
    assert "== map system report ==" not in captured.out
    assert "== map entities ==" not in captured.out


def test_cli_selected_entity_detail_from_synthetic_install(tmp_path: Path, capsys) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "--entity-system",
            "government",
            "--entity",
            "monarchy",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Selected page: entity:government:monarchy" in captured.out
    assert "- entities:government: government entities" in captured.out
    assert "== monarchy government_type ==" in captured.out
    assert "- government_power: legitimacy" in captured.out
    assert "- default_estate -> government/estate: sample_estate" in captured.out


def test_build_shell_message_page_key_selects_one_page_from_all_systems(tmp_path: Path) -> None:
    install_root = _make_report_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        include_all_systems=True,
        page_key="report:map",
    )

    assert "Selected page: report:map" in message
    assert "* report:map: map system report" in message
    assert "== map system report ==" in message
    assert "== Install overview ==" not in message
    assert "== economy system report ==" not in message
    assert "== map entities ==" not in message


def test_build_shell_message_filter_limits_visible_pages(tmp_path: Path) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        selected_entity_system="religion",
        page_filter="catholic",
    )

    assert "Selected page: entities:religion" in message
    assert "Page filter: catholic" in message
    assert "Available pages (1 of 2 loaded):" in message
    assert "* entities:religion: religion entities" in message
    assert "== religion entities ==" in message
    assert "== Install overview ==" not in message


def test_build_shell_message_empty_filter_shows_guidance(tmp_path: Path) -> None:
    install_root = _make_report_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        include_all_systems=True,
        page_filter="does-not-match",
    )

    assert "Selected page: none" in message
    assert "Available pages (0 of 11 loaded):" in message
    assert "No pages matched the current filter." in message
    assert "Page filters only search already-loaded pages." in message


def test_build_shell_message_list_pages_only_hides_page_content(tmp_path: Path) -> None:
    install_root = _make_report_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        include_all_systems=True,
        list_pages_only=True,
    )

    assert "Available pages:" in message
    assert "Index mode: page content hidden." in message
    assert "== Install overview ==" not in message
    assert "== map system report ==" not in message


def test_build_shell_message_page_window_keeps_selected_page_visible(tmp_path: Path) -> None:
    install_root = _make_report_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        include_all_systems=True,
        page_key="entities:map",
        page_list_limit=3,
    )

    assert "Available pages (showing 9-11 of 11 loaded):" in message
    assert "Page window: showing 9-11 of 11 matched pages." in message
    assert "* entities:map: map entities" in message
    assert "- overview: Install overview" not in message


def test_build_shell_message_page_window_offset_can_hide_selected_page(tmp_path: Path) -> None:
    install_root = _make_report_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        include_all_systems=True,
        page_key="entities:map",
        page_list_limit=3,
        page_list_offset=0,
    )

    assert "Available pages (showing 1-3 of 11 loaded):" in message
    assert "Page window: showing 1-3 of 11 matched pages." in message
    assert "Selected page is outside the current page window." in message
    assert "* entities:map: map entities" not in message
    assert "- overview: Install overview" in message


def test_build_shell_message_section_line_limit_truncates_large_entity_lists(
    tmp_path: Path,
) -> None:
    install_root = _make_large_entity_browsing_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        selected_entity_system="religion",
        section_line_limit=5,
    )

    assert "== religion entities ==" in message
    assert "- Entity count: 12" in message
    assert "- faith_01 [group]" in message
    assert "- faith_05 [group]" in message
    assert "- faith_06 [group]" in message
    assert "- faith_12 [group]" in message


def test_build_shell_message_entity_detail_navigation_hints_parent_page(tmp_path: Path) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        selected_entity_system="government",
        selected_entity_name="monarchy",
    )

    assert "== monarchy government_type ==" in message
    assert "Navigation:" in message
    assert "- Page key: entity:government:monarchy" in message
    assert "- Direct page flag: --page entity:government:monarchy" in message
    assert "- Selection flags: --entity-system government --entity monarchy" in message
    assert "- Session position: 3 of 3 loaded pages" in message
    assert "- Previous page: entities:government" in message
    assert "- Overview page: overview" in message
    assert "- Parent list page: entities:government" in message


def test_build_shell_message_report_navigation_shows_neighboring_pages(tmp_path: Path) -> None:
    install_root = _make_report_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        include_all_systems=True,
        page_key="report:map",
    )

    assert "Selected page: report:map" in message
    assert "- Session position: 7 of 11 loaded pages" in message
    assert "- Previous page: report:interface" in message
    assert "- Next page: entities:economy" in message


def test_build_shell_message_unavailable_page_adds_recovery_guidance(
    tmp_path: Path,
) -> None:
    install_root = _make_report_install(tmp_path / "install")

    message = build_shell_message(
        install_root,
        include_all_systems=True,
        page_key="report:economy",
    )

    assert "== economy system report ==" in message
    assert "- Direct page flag: --page report:economy" in message
    assert "- Selection flags: --system economy" in message
    assert "- Session position: 2 of 11 loaded pages" in message
    assert "- Next page: report:diplomacy" in message
    assert "- Unavailable from selected install." in message
    assert "- Check the overview page for install roots and loaded content sources." in message
    assert (
        "- Unavailable pages stay indexed so partial or synthetic installs keep a stable "
        "session."
    ) in message


def test_build_shell_message_quotes_entity_selection_flag_values_with_spaces(
    tmp_path: Path,
) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    model = build_browser_model(
        install_root,
        selected_entity_system="religion",
        selected_entity_name="holy order",
    )

    navigation_lines = model.pages[-1].navigation_hints
    assert navigation_lines == ()

    message = build_shell_message(
        install_root,
        selected_entity_system="religion",
        selected_entity_name="holy order",
    )

    assert (
        "- Selection flags: --entity-system religion --entity \"holy order\""
        in message
    )


def test_cli_rejects_negative_browser_window_controls(capsys) -> None:
    try:
        main(["--page-list-limit", "-1"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected CLI parse failure")

    captured = capsys.readouterr()
    assert "page_list_limit cannot be negative." in captured.err

    try:
        main(["--entity-list-offset", "-1"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected CLI parse failure")

    captured = capsys.readouterr()
    assert "entity_list_offset cannot be negative." in captured.err


def test_cli_page_key_can_open_entity_detail_without_explicit_entity_flags(
    tmp_path: Path,
    capsys,
) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "--page",
            "entity:government:monarchy",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Selected page: entity:government:monarchy" in captured.out
    assert "* entity:government:monarchy: monarchy government_type" in captured.out
    assert "== monarchy government_type ==" in captured.out


def test_cli_page_alias_can_open_entity_detail_without_explicit_entity_flags(
    tmp_path: Path,
    capsys,
) -> None:
    install_root = _make_entity_browsing_install(tmp_path / "install")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "--page",
            "detail:government:monarchy",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Selected page: entity:government:monarchy" in captured.out
    assert "* entity:government:monarchy: monarchy government_type" in captured.out
    assert "== monarchy government_type ==" in captured.out


def test_cli_page_target_suggests_closest_supported_system(tmp_path: Path, capsys) -> None:
    install_root = _make_report_install(tmp_path / "install")

    try:
        main(["--install-root", str(install_root), "--page", "system:mapp"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected CLI parse failure")

    captured = capsys.readouterr()
    assert "Unknown system 'mapp'. Did you mean 'map'?" in captured.err


def test_cli_show_all_pages_restores_full_page_dump(tmp_path: Path, capsys) -> None:
    install_root = _make_report_install(tmp_path / "install")

    exit_code = main(
        ["--install-root", str(install_root), "--all-systems", "--show-all-pages"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "== Install overview ==" in captured.out
    assert "== economy system report ==" in captured.out
    assert "== diplomacy system report ==" in captured.out
    assert "== government system report ==" in captured.out
    assert "== religion system report ==" in captured.out
    assert "== interface system report ==" in captured.out
    assert "== map system report ==" in captured.out
    assert "== map entities ==" in captured.out


def test_cli_entity_list_source_sort_and_limit_controls(tmp_path: Path, capsys) -> None:
    install_root = _make_large_entity_browsing_install(tmp_path / "install")

    exit_code = main(
        [
            "--install-root",
            str(install_root),
            "--entity-system",
            "religion",
            "--entity-list-sort",
            "source",
            "--entity-list-limit",
            "2",
            "--entity-list-offset",
            "1",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "- Sort: source" in captured.out
    assert "- Entity window: showing 2-3 of 12" in captured.out
    assert "- faith_02" in captured.out
    assert "- faith_03" in captured.out
    assert "- faith_04" not in captured.out


def _make_report_install(install_root: Path) -> Path:
    game_dir = install_root / "game"
    for phase_name in ("loading_screen", "main_menu", "in_game"):
        (game_dir / phase_name).mkdir(parents=True, exist_ok=True)
    (game_dir / "dlc").mkdir(parents=True, exist_ok=True)
    (game_dir / "mod").mkdir(parents=True, exist_ok=True)

    _write_text(
        game_dir / "in_game" / "map_data" / "default.map",
        'definitions = "definitions.txt"\n'
        'adjacencies = "adjacencies.csv"\n'
        'ports = "ports.csv"\n'
        "wrap_x = no\n",
    )
    _write_text(
        game_dir / "in_game" / "map_data" / "definitions.txt",
        "world = {\n"
        "    region = {\n"
        "        area = {\n"
        "            province = { stockholm uppsala }\n"
        "        }\n"
        "    }\n"
        "}\n",
    )
    _write_text(
        game_dir / "in_game" / "map_data" / "adjacencies.csv",
        "From;To;Type;Through;start_x;start_y;stop_x;stop_y;Comment\n"
        "stockholm;uppsala;river;;1;2;3;4;synthetic\n",
    )
    _write_text(
        game_dir / "in_game" / "map_data" / "ports.csv",
        "LandProvince;SeaZone;x;y;\nstockholm;inner_sea;10;20;x\n",
    )
    _write_text(
        game_dir / "main_menu" / "setup" / "start" / "10_countries.txt",
        "countries = {\n"
        "    countries = {\n"
        "        SWE = {\n"
        "            own_control_core = { stockholm uppsala }\n"
        "            capital = stockholm\n"
        "        }\n"
        "    }\n"
        "}\n",
    )
    _write_text(
        game_dir / "main_menu" / "setup" / "start" / "21_locations.txt",
        "locations = {\n"
        "    stockholm = { timed_modifiers = { } }\n"
        "}\n",
    )
    return install_root


def _make_entity_browsing_install(install_root: Path) -> Path:
    game_dir = install_root / "game"
    for phase_name in ("loading_screen", "main_menu", "in_game"):
        (game_dir / phase_name).mkdir(parents=True, exist_ok=True)
    (game_dir / "dlc").mkdir(parents=True, exist_ok=True)
    (game_dir / "mod").mkdir(parents=True, exist_ok=True)

    for relative_path, text in _entity_fixture_texts().items():
        _write_text(game_dir / relative_path, text)

    return install_root


def _make_large_entity_browsing_install(install_root: Path) -> Path:
    install_root = _make_entity_browsing_install(install_root)
    game_dir = install_root / "game"

    _write_text(
        game_dir / "in_game" / "common" / "religions" / "00_religions.txt",
        _large_religion_fixture_text(12),
    )

    return install_root


def _entity_fixture_texts() -> dict[Path, str]:
    return {
        Path("in_game/common/goods/00_goods.txt"): (
            "iron = {\n"
            "    method = mining\n"
            "    category = raw_material\n"
            "    default_market_price = 3\n"
            "    demand_add = { grain = 0.5 }\n"
            "}\n"
            "grain = { method = farming category = food }\n"
        ),
        Path("in_game/common/prices/00_prices.txt"): "build_road = { iron = 10 }\n",
        Path("in_game/common/generic_actions/00_actions.txt"): (
            "create_market = {\n"
            "    type = owncountry\n"
            "    select_trigger = { looking_for_a = market }\n"
            "}\n"
        ),
        Path("in_game/common/attribute_columns/00_columns.txt"): (
            "market = { name = { widget = default_text_column } }\n"
        ),
        Path("in_game/common/government_types/00_government_types.txt"): (
            "monarchy = {\n"
            "    heir_selection = cognatic\n"
            "    government_power = legitimacy\n"
            "    default_character_estate = sample_estate\n"
            "}\n"
        ),
        Path("in_game/common/government_reforms/00_reforms.txt"): (
            "sample_reform = { government = monarchy years = 2 country_modifier = { add = 1 } }\n"
        ),
        Path("in_game/common/laws/00_laws.txt"): (
            "sample_law = {\n"
            "    law_category = administrative\n"
            "    law_gov_group = monarchy\n"
            "    policy_a = { years = 2 country_modifier = { add = 1 } "
            "estate_preferences = { sample_estate } }\n"
            "}\n"
        ),
        Path("in_game/common/estates/00_estates.txt"): (
            "sample_estate = { color = pop_nobles power_per_pop = 25 tax_per_pop = 100 "
            "ruler = yes }\n"
        ),
        Path("in_game/common/estate_privileges/00_privileges.txt"): (
            "sample_privilege = { estate = sample_estate country_modifier = { add = 1 } }\n"
        ),
        Path("in_game/common/parliament_types/00_parliament_types.txt"): (
            "sample_parliament = { type = country modifier = { add = 1 } }\n"
        ),
        Path("in_game/common/parliament_agendas/00_agendas.txt"): (
            "sample_agenda = { type = country estate = sample_estate chance = 10 "
            "on_accept = { add = 1 } }\n"
        ),
        Path("in_game/common/parliament_issues/00_issues.txt"): (
            "sample_issue = { type = country estate = sample_estate chance = 0 "
            "on_debate_passed = { add = 1 } }\n"
        ),
        Path("in_game/common/religions/00_religions.txt"): (
            "catholic = {\n"
            "    group = christian\n"
            "    factions = { sample_faction }\n"
            "    religious_focuses = { sample_focus }\n"
            "    religious_school = sample_school\n"
            "    religious_aspects = { sample_aspect }\n"
            "    tags = { catholic_gfx }\n"
            "}\n"
            "orthodox = { group = christian }\n"
        ),
        Path("in_game/common/religious_aspects/00_aspects.txt"): (
            "sample_aspect = { religion = catholic enabled = { always = yes } modifier = "
            "{ add = 1 } opinions = { sample_aspect = 10 } }\n"
        ),
        Path("in_game/common/religious_factions/00_factions.txt"): (
            "sample_faction = { visible = { always = yes } enabled = { always = yes } "
            "actions = { action_a action_b } }\n"
        ),
        Path("in_game/common/religious_focuses/00_focuses.txt"): (
            "sample_focus = { monthly_progress = { add = 1 } modifier_on_completion = "
            "{ add = 1 } }\n"
        ),
        Path("in_game/common/religious_schools/00_schools.txt"): (
            "sample_school = { color = rgb { 1 2 3 } enabled_for_country = { always = "
            "yes } modifier = { add = 1 } }\n"
        ),
        Path("in_game/common/religious_figures/00_figures.txt"): (
            "sample_figure = { enabled_for_religion = { group = religion_group:christian } }\n"
        ),
        Path("in_game/common/holy_sites/00_holy_sites.txt"): (
            "sample_site = { location = rome type = temple importance = 4 religions = "
            "{ catholic } }\n"
        ),
        Path("in_game/map_data/definitions.txt"): (
            "world = {\n"
            "    region = {\n"
            "        area = {\n"
            "            province = { stockholm }\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        Path("main_menu/setup/start/10_countries.txt"): (
            "countries = {\n"
            "    countries = {\n"
            "        SWE = {\n"
            "            own_control_core = { stockholm }\n"
            "            capital = stockholm\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
        Path("main_menu/setup/start/21_locations.txt"): (
            "locations = {\n    stockholm = { timed_modifiers = { } }\n}\n"
        ),
    }


def _first_entity_name_for(system: str) -> str:
    names = {
        "economy": "iron",
        "government": "monarchy",
        "religion": "catholic",
        "map": "stockholm",
    }
    return names[system]


def _large_religion_fixture_text(religion_count: int) -> str:
    religion_blocks = [
        (
            f"faith_{index:02d} = {{\n"
            "    group = group\n"
            f"    description = synthetic religion {index}\n"
            "}\n"
        )
        for index in range(1, religion_count + 1)
    ]
    return "".join(religion_blocks)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
