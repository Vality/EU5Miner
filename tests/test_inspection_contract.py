from __future__ import annotations

import eu5miner
import eu5miner.inspection as inspection_api
from eu5miner.inspection import list_entity_systems, list_supported_systems

EXPECTED_SUPPORTED_SYSTEMS = (
    (
        "economy",
        "Goods, prices, production, demand, and market helper coverage.",
    ),
    (
        "diplomacy",
        "War-flow, diplomacy graph, and unit-family coverage.",
    ),
    (
        "government",
        "Government, law, estate, parliament, and institution coverage.",
    ),
    (
        "religion",
        "Religion, holy-site, and religious helper coverage.",
    ),
    (
        "interface",
        "Localization, GUI, and frontend-content coverage.",
    ),
    (
        "map",
        "Map text, map CSV, and linked setup-location coverage.",
    ),
)

EXPECTED_BROWSABLE_SYSTEMS = (
    (
        "economy",
        "Browse goods definitions with market-facing fields and related good links.",
        "good",
    ),
    (
        "diplomacy",
        "Browse casus belli definitions with linked wargoals, peace treaties, "
        "and country interactions.",
        "casus_belli",
    ),
    (
        "government",
        "Browse government types with linked reforms, laws, and default estates.",
        "government_type",
    ),
    (
        "religion",
        "Browse religions with linked aspects, factions, focuses, schools, "
        "figures, and holy sites.",
        "religion",
    ),
    (
        "map",
        "Browse linked locations merged from map hierarchy and main-menu setup data.",
        "location",
    ),
)


def test_supported_systems_match_stabilized_order_and_descriptions() -> None:
    systems = tuple((system.name, system.description) for system in list_supported_systems())

    assert systems == EXPECTED_SUPPORTED_SYSTEMS


def test_browsable_entity_systems_match_stabilized_subset_order_and_descriptions() -> None:
    systems = tuple(
        (system.name, system.description, system.primary_entity_kind)
        for system in list_entity_systems()
    )

    assert systems == EXPECTED_BROWSABLE_SYSTEMS
    assert tuple(system[0] for system in EXPECTED_BROWSABLE_SYSTEMS) == tuple(
        name for name, _description in EXPECTED_SUPPORTED_SYSTEMS if name != "interface"
    )


def test_root_package_keeps_inspection_facade_as_an_explicit_import_boundary() -> None:
    root_exports = set(eu5miner.__all__)
    inspection_exports = set(inspection_api.__all__)

    assert inspection_exports.isdisjoint(root_exports)
    for name in inspection_api.__all__:
        assert hasattr(inspection_api, name)
        assert not hasattr(eu5miner, name)
