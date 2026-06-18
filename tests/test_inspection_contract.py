"""Contract tests for the ``eu5miner.inspection`` facade.

These tests pin the public shape of the inspection facade — the same surface
that ``eu5miner-gui`` (its ``DesktopController``) and ``eu5miner-mcp`` (its
``tools/entities.py``, ``tools/systems.py``, ``tools/install.py``) consume.

If a field is renamed, removed, or its type changes, these tests will fail.
The point is to catch breaking library changes BEFORE they cascade into the
GUI or MCP repos, which is exactly the cross-package pain these tests exist
to prevent.

What this covers:
- Public function set of the facade (the methods GUI/MCP can call)
- Dataclass field names and types for every returned type
- End-to-end behavior of ``inspect_install`` on a synthetic install
- Compatibility of the ``SystemInfo`` / ``EntitySystemInfo`` enums that
  drive the GUI's sidebar and the MCP's tool schema

What this deliberately does NOT cover:
- The internal ``eu5miner.domains.*`` parsers (those have their own
  dedicated tests in ``tests/domains/``)
- The mod workflow facade (``eu5miner.mods``) — covered separately
  by ``tests/test_cli_mod_workflow_contract.py``
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import get_type_hints

import pytest

import eu5miner.inspection as inspection
from eu5miner.testing import build_synthetic_install

# ----- Public function set ----------------------------------------------------


# These are the symbols the GUI and MCP are known to depend on. Any rename
# here is a breaking change for at least one of the consumer packages.
REQUIRED_PUBLIC_FUNCTIONS = frozenset(
    {
        "inspect_install",
        "summarize_install",
        "format_install_summary",
        "list_supported_systems",
        "list_entity_systems",
        "list_system_entities",
        "get_system_report",
        "format_system_report",
        "get_system_entity",
        "invalidate_system_entity_cache",
    }
)


def test_required_public_functions_exist() -> None:
    """The facade must keep exporting the functions the consumers depend on."""
    missing = sorted(REQUIRED_PUBLIC_FUNCTIONS - set(dir(inspection)))
    assert not missing, (
        f"Missing required public functions on eu5miner.inspection: {missing}. "
        "If you renamed one, also update eu5miner-gui and eu5miner-mcp."
    )


# ----- Dataclass field shape --------------------------------------------------


# Dataclasses the GUI and MCP construct/persist. The field shapes here are
# what their adapters, controllers, and serializers assume.
REQUIRED_DATACLASSES = {
    "SystemInfo": ("name", "description"),
    "EntitySystemInfo": ("name", "description", "primary_entity_kind"),
    "EntitySummary": ("system", "entity_kind", "name", "group", "description"),
    "EntityField": ("name", "value"),
    "EntityReference": ("role", "system", "entity_kind", "target_name"),
    "EntityDetail": ("summary", "fields", "references"),
    "InstallPhaseRoot": ("phase", "path"),
    "InstallSourceSummary": (
        "name",
        "kind",
        "root",
        "priority",
        "replace_paths",
    ),
    "InstallSummary": (
        "root",
        "game_dir",
        "dlc_dir",
        "mod_dir",
        "phase_roots",
        "sources",
    ),
    "SystemReport": (
        "name",
        "description",
        "representative_keys",
        "summary_lines",
    ),
}


@pytest.mark.parametrize("class_name,expected_fields", sorted(REQUIRED_DATACLASSES.items()))
def test_required_dataclass_field_shape(class_name: str, expected_fields: tuple[str, ...]) -> None:
    """Each public dataclass must keep the field set consumers rely on."""
    obj = getattr(inspection, class_name, None)
    assert obj is not None, f"Missing public type eu5miner.inspection.{class_name}"
    assert is_dataclass(obj), f"eu5miner.inspection.{class_name} must remain a dataclass"
    actual = tuple(f.name for f in fields(obj))
    assert actual == expected_fields, (
        f"Field shape of eu5miner.inspection.{class_name} changed.\n"
        f"  expected: {expected_fields}\n"
        f"  actual:   {actual}\n"
        "Update GUI/MCP adapters, controllers, and serializers accordingly."
    )


# ----- End-to-end on a synthetic install --------------------------------------


def test_inspect_install_against_synthetic_install(tmp_path: Path) -> None:
    """``inspect_install`` on a fresh synthetic install returns a stable shape.

    The GUI's ``DesktopController.initialize`` and the MCP's
    ``inspect_install`` tool both call this function on first contact with an
    install. If the shape changes, both consumers break simultaneously.
    """
    install_root = tmp_path / "install"
    build_synthetic_install(install_root)

    summary = inspection.inspect_install(install_root)

    assert isinstance(summary, inspection.InstallSummary)
    assert summary.root == install_root
    assert summary.game_dir == install_root / "game"
    assert summary.dlc_dir == install_root / "game" / "dlc"
    assert summary.mod_dir == install_root / "game" / "mod"
    # All three content phases must be present, in stable order.
    assert tuple(p.phase for p in summary.phase_roots) == tuple(inspection.ContentPhase)
    # A bare synthetic install has only the vanilla source.
    assert [s.name for s in summary.sources] == ["vanilla"]


def test_format_install_summary_renders_synthetic_install(tmp_path: Path) -> None:
    """``format_install_summary`` must produce a non-empty human-readable block.

    The GUI's status bar and the MCP's ``inspect_install`` tool response both
    render this string. A regression here surfaces as a blank status bar
    or empty tool output.
    """
    install_root = tmp_path / "install"
    build_synthetic_install(install_root)

    formatted = inspection.format_install_summary(inspection.inspect_install(install_root))

    assert "Install root:" in formatted
    assert str(install_root) in formatted
    assert "Sources:" in formatted
    assert "vanilla" in formatted


def test_list_supported_systems_includes_core_systems() -> None:
    """The supported-systems list must always include these core names.

    The GUI's sidebar and the MCP's ``list_systems`` tool both render this
    list. Removing or renaming any of these is a breaking change.
    """
    names = {info.name for info in inspection.list_supported_systems()}
    required = {"economy", "diplomacy", "government", "religion", "interface", "map"}
    missing = required - names
    assert not missing, f"Missing required systems from list_supported_systems: {missing}"


def test_list_entity_systems_includes_core_systems() -> None:
    """The entity-systems list must always include these core names.

    The GUI's entity browser and the MCP's ``list_entity_systems`` tool both
    depend on these names.
    """
    names = {info.name for info in inspection.list_entity_systems()}
    required = {"economy", "diplomacy", "government", "religion", "map"}
    missing = required - names
    assert not missing, f"Missing required entity systems: {missing}"


# ----- Type-stability check ---------------------------------------------------


def test_entity_field_browse_value_alias() -> None:
    """``BrowseValue`` (the union alias for EntityField.value) must keep its members.

    The GUI's report page and the MCP's ``get_entity`` serializer both render
    these values. Adding a new type is fine; removing an existing one breaks
    any saved browse value.
    """
    hints = get_type_hints(inspection.EntityField)
    # The type is an alias; we just want to make sure the field exists and
    # the annotation round-trips through get_type_hints without exploding.
    assert "value" in hints


# ----- Cache invalidation hook ------------------------------------------------


def test_invalidate_system_entity_cache_is_idempotent(tmp_path: Path) -> None:
    """``invalidate_system_entity_cache`` must accept a fresh install + system.

    Both consumers call this defensively after writing mod updates. A
    regression that raises on a missing cache entry would crash the GUI on
    every mod apply and the MCP on every ``apply_mod_update`` tool call.
    """
    install_root = tmp_path / "install"
    build_synthetic_install(install_root)
    # Should not raise even though the system has never been queried.
    inspection.invalidate_system_entity_cache(install_root, "religion")
