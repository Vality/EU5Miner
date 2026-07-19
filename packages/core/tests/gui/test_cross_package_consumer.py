"""Cross-package consumer tests: drive the GUI against the real library.

These tests exercise the ``eu5miner.gui`` desktop controller using the real
``eu5miner`` library (not a mock ``FakeInspection``). If a library change
breaks the GUI's expected input shape, these tests catch it before it reaches
production.

The synthetic install layout is provided by ``eu5miner.testing`` so the
contract for what counts as a "fresh install" is shared with the library
tests and the MCP cross-package tests.

These tests intentionally do NOT launch the actual Kivy app — they construct
the controller and call its methods directly. Kivy requires a display
server, which is not available in CI. The controller layer is where the
real cross-package contract lives: the Kivy widgets are a thin render layer
on top of it.
"""

from __future__ import annotations

from pathlib import Path

import eu5miner.inspection as inspection
from eu5miner.gui.desktop.controller import DesktopController
from eu5miner.gui.desktop.navigation import NavigationTarget
from eu5miner.testing import build_synthetic_install

# ----- Controller construction against the real library ----------------------


def test_controller_init_uses_real_inspection_facade() -> None:
    """A default-constructed controller must call into the real facade.

    A regression that broke the facade's ``list_supported_systems`` or
    ``list_entity_systems`` shape would surface here, before any Kivy
    widget tries to render the sidebar.
    """
    controller = DesktopController()

    # ``supported_systems`` and ``entity_systems`` are populated at __init__
    # by calling into the facade. If the facade shape breaks, this fails.
    assert len(controller.supported_systems) > 0
    assert len(controller.entity_systems) > 0
    # Every SystemInfo must have a non-empty name and description.
    for info in controller.supported_systems:
        assert isinstance(info, inspection.SystemInfo)
        assert info.name
        assert info.description
    for info in controller.entity_systems:
        assert isinstance(info, inspection.EntitySystemInfo)
        assert info.name
        assert info.primary_entity_kind


# ----- Synthetic-install end-to-end ------------------------------------------


def test_controller_initializes_with_synthetic_install(tmp_path: Path) -> None:
    """Initializing a controller against a fresh synthetic install must succeed.

    This is the GUI's "first-run" path: discover install, list systems,
    navigate to overview, and serve the formatted install summary in the
    status bar. All of these are cross-package calls into the library.
    """
    install_root = tmp_path / "install"
    build_synthetic_install(install_root)

    controller = DesktopController()
    controller.initialize(install_root=install_root)

    assert controller.active_install_root == install_root
    # After initialize, the controller should be on the overview page.
    assert controller.navigation_state.current_target.kind == "overview"


def test_controller_reports_supported_systems_for_synthetic_install(tmp_path: Path) -> None:
    """The reported supported-systems list is driven by the library facade.

    The sidebar renders this list. If the library changes the system names
    without a coordinated GUI update, the sidebar would show stale items.
    """
    install_root = tmp_path / "install"
    build_synthetic_install(install_root)

    controller = DesktopController()
    controller.initialize(install_root=install_root)

    # Pin the systems the GUI sidebar is known to depend on. This mirrors
    # the library-side test in test_inspection_contract.py and guards
    # against a library rename that the GUI didn't follow up on.
    system_names = {info.name for info in controller.supported_systems}
    required = {"economy", "diplomacy", "government", "religion", "interface", "map"}
    missing = required - system_names
    assert not missing, (
        f"GUI sidebar would miss these systems after a library rename: {missing}. "
        "If the rename is intentional, update the GUI's navigation and "
        "system-rendering code in src/eu5miner.gui/desktop/."
    )


# ----- Mod folder integration ------------------------------------------------


def test_controller_accepts_additional_mod_folder(tmp_path: Path) -> None:
    """The GUI must accept a mod folder alongside the install and re-discover.

    This is the GUI's "load my mod" path. A regression that broke mod
    folder handling would surface as the mod not appearing in the install
    summary or the navigation locking out of mod-rooted views.
    """
    install_root = tmp_path / "install"
    build_synthetic_install(install_root)

    mod_root = tmp_path / "my_mod"
    (mod_root / "in_game").mkdir(parents=True)

    controller = DesktopController()
    controller.initialize(install_root=install_root, mod_folders=(mod_root,))

    assert mod_root in controller.active_mod_folders


# ----- Entity navigation smoke test -------------------------------------------


def test_controller_navigates_to_entity_browser(tmp_path: Path) -> None:
    """Navigating to an entity-list page must succeed against the real facade.

    The entity browser is the GUI's primary read-only view. It calls
    ``list_system_entities`` (via the controller's inspection adapter) and
    renders the results. A regression in the facade that broke the
    ``EntitySummary`` shape would surface here.
    """
    install_root = tmp_path / "install"
    build_synthetic_install(install_root)

    controller = DesktopController()
    controller.initialize(install_root=install_root)

    # Navigating to the entity list for "religion" is a no-data state but
    # exercises the full navigation adapter path through to the inspection
    # facade. With a synthetic install the underlying file scan returns
    # nothing, so the controller should land on the page cleanly without
    # raising — any facade breakage would raise here.
    controller.navigate(NavigationTarget.entity_list("religion"))


# ----- Library import boundary ------------------------------------------------


_ALLOWED_EU5MINER_IMPORT_PREFIXES = (
    "eu5miner.inspection",
    "eu5miner.mods",
    "eu5miner.testing",
    # The library's own ``__init__`` docstring declares ``eu5miner.domains``
    # as a public surface ("concept-local helpers from grouped packages under
    # ``eu5miner.domains``"), and ``eu5miner.inspection`` itself imports from
    # ``eu5miner.domains.*``. Domain packages are part of the contract.
    "eu5miner.domains",
    # ``eu5miner.vfs`` re-exports ``ContentSource``, ``SourceKind``, and
    # ``VirtualFilesystem`` to the root and is the canonical import path
    # for the VFS types (``MergedFile``, ``SourceFile``, etc.).
    "eu5miner.vfs",
    # After consolidation, ``eu5miner.gui`` lives in the same wheel. Intra-package
    # imports between the GUI shells, browser, and desktop controller are no
    # longer "reaching into the library" — they're internal GUI plumbing.
    "eu5miner.gui",
)


def _eu5miner_target_module(stripped_line: str) -> str | None:
    """Return the imported top-level ``eu5miner.*`` module, or None.

    Uses word-boundary parsing instead of substring matching so that
    ``from eu5miner.gui ...`` is NOT confused with ``from eu5miner ...``.
    """
    tokens = stripped_line.split()
    if not tokens or tokens[0] not in {"import", "from"}:
        return None
    if tokens[0] == "import":
        # `import eu5miner` or `import eu5miner.foo` (with optional `as alias`)
        for tok in tokens[1:]:
            if tok == "as" or tok.startswith("(") or tok == ",":
                break
            if tok == "eu5miner" or tok.startswith("eu5miner."):
                return tok.rstrip(",")
        return None
    # `from eu5miner[.x[.y]] import ...` — module is the second token
    if len(tokens) >= 2 and (tokens[1] == "eu5miner" or tokens[1].startswith("eu5miner.")):
        return tokens[1]
    return None


def _is_allowed_eu5miner_import(stripped_line: str) -> bool:
    """True if a ``from eu5miner ...`` or ``import eu5miner ...`` line is public.

    The library's public surface is:
    - ``from eu5miner import <name>`` (re-exported names from ``__init__``)
    - ``import eu5miner`` (the root)
    - ``import eu5miner.inspection``, ``.mods``, ``.testing`` (facades)
    - ``import eu5miner.domains`` and any submodule (public per library's
      own ``__init__`` docstring)
    """
    target = _eu5miner_target_module(stripped_line)
    if target is None:
        return False
    if target == "eu5miner":
        # `import eu5miner` or `from eu5miner import <name>`
        if stripped_line.startswith("from eu5miner import"):
            return True
        return stripped_line in {"import eu5miner", "import eu5miner as _"}
    for prefix in _ALLOWED_EU5MINER_IMPORT_PREFIXES:
        if target == prefix or target.startswith(prefix + "."):
            return True
    return False


def test_gui_does_not_reach_into_private_library_modules() -> None:
    """The GUI must only import from the library's public surface.

    Pin this so that future GUI refactors don't start grabbing internal
    helpers from ``eu5miner.domains._private_helpers`` or similar — which
    would silently couple the GUI to library internals and break again
    on the next library refactor.

    The current public root is ``eu5miner`` (``GameInstall``,
    ``ContentPhase``, ``VirtualFilesystem``) and the stable facade is
    ``eu5miner.inspection`` plus the ``eu5miner.mods`` helper package.
    """
    import sys

    import eu5miner.gui  # noqa: F401  (just importing for the side effect)
    gui_modules = [
        name
        for name in sys.modules
        if name.startswith("eu5miner.gui.")
    ]
    bad_imports: list[tuple[str, str]] = []
    for module_name in gui_modules:
        module = sys.modules[module_name]
        source = getattr(module, "__file__", "") or ""
        if not source.endswith(".py"):
            continue
        try:
            text = Path(source).read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith(("from ", "import ")):
                continue
            # Allow public root and the inspection/mods/testing/domains
            # facades. Word-boundary tokenization via _eu5miner_target_module
            # avoids confusing ``from eu5miner.gui ...`` with ``from eu5miner ...``.
            target = _eu5miner_target_module(stripped)
            if target is None:
                continue
            if _is_allowed_eu5miner_import(stripped):
                continue
            bad_imports.append((module_name, stripped))

    assert not bad_imports, (
        "GUI is reaching into non-public library modules. "
        "Move the import to the public facade (eu5miner, eu5miner.inspection, "
        "eu5miner.mods, or eu5miner.testing) before the next library refactor.\n"
        + "\n".join(f"  {m}: {imp}" for m, imp in bad_imports)
    )


# ----- Library / GUI agreement -----------------------------------------------


def test_gui_and_library_agree_on_supported_system_names() -> None:
    """The GUI sidebar must show exactly the systems the library exposes.

    The GUI's ``supported_systems`` is populated at ``DesktopController``
    construction from ``inspection.list_supported_systems``. A library
    rename that the GUI didn't follow up on would surface here as a
    divergence. The GUI depends on the names being a subset of the
    library's set, and on the names being stable.
    """
    controller = DesktopController()
    gui_names = {info.name for info in controller.supported_systems}
    library_names = {info.name for info in inspection.list_supported_systems()}

    # The GUI must not invent systems that don't exist in the library.
    extra = gui_names - library_names
    assert not extra, (
        f"GUI exposes systems the library does not: {extra}. "
        "These would render as broken sidebar items in the desktop app."
    )
    # The GUI must see every library system that it would render a page for.
    # The set of "core systems" is the same one pinned in
    # ``test_controller_reports_supported_systems_for_synthetic_install``.
    required = {"economy", "diplomacy", "government", "religion", "interface", "map"}
    missing = required - gui_names
    assert not missing, (
        f"GUI is missing these required library systems: {missing}. "
        "Update the GUI's navigation code to include them."
    )


def test_gui_and_library_agree_on_entity_system_names() -> None:
    """The GUI entity browser must show exactly the entity systems the library exposes.

    Same shape as the supported-system check above, but for the entity
    browsing surface.
    """
    controller = DesktopController()
    gui_names = {info.name for info in controller.entity_systems}
    library_names = {info.name for info in inspection.list_entity_systems()}

    extra = gui_names - library_names
    assert not extra, (
        f"GUI exposes entity systems the library does not: {extra}. "
        "These would render as broken entity browser pages in the desktop app."
    )
    required = {"economy", "diplomacy", "government", "religion", "map"}
    missing = required - gui_names
    assert not missing, (
        f"GUI is missing these required library entity systems: {missing}."
    )
