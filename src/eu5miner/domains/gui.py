"""Domain adapter for EU5 GUI script files."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains._parse_helpers import entry_object, entry_scalar_text
from eu5miner.formats import semantic


@dataclass(frozen=True)
class GuiConstant:
    """One top-level GUI constant or variable assignment."""

    name: str
    value_text: str | None
    value_object: semantic.SemanticObject | None
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class GuiTemplateDefinition:
    """One top-level named GUI template."""

    name: str
    body: semantic.SemanticObject
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class GuiTypeDefinition:
    """One `type ... = kind { ... }` definition inside a GUI type group."""

    name: str
    widget_kind: str | None
    body: semantic.SemanticObject
    internal_name: str | None
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class GuiTypeGroup:
    """One top-level `types GroupName { ... }` library."""

    name: str
    definitions: tuple[GuiTypeDefinition, ...]
    body: semantic.SemanticObject
    entry: semantic.SemanticEntry

    def definition_names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> GuiTypeDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


@dataclass(frozen=True)
class GuiRootDefinition:
    """One standalone top-level GUI definition such as `window = { ... }`."""

    definition_kind: str
    body_prefix: str
    body: semantic.SemanticObject
    internal_name: str | None
    widget_id: str | None
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class GuiDocument:
    """Parsed GUI script file."""

    constants: tuple[GuiConstant, ...]
    templates: tuple[GuiTemplateDefinition, ...]
    type_groups: tuple[GuiTypeGroup, ...]
    root_definitions: tuple[GuiRootDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def constant_names(self) -> tuple[str, ...]:
        return tuple(constant.name for constant in self.constants)

    def template_names(self) -> tuple[str, ...]:
        return tuple(template.name for template in self.templates)

    def type_group_names(self) -> tuple[str, ...]:
        return tuple(group.name for group in self.type_groups)

    def root_definition_kinds(self) -> tuple[str, ...]:
        return tuple(definition.definition_kind for definition in self.root_definitions)

    def get_constant(self, name: str) -> GuiConstant | None:
        for constant in self.constants:
            if constant.name == name:
                return constant
        return None

    def get_template(self, name: str) -> GuiTemplateDefinition | None:
        for template in self.templates:
            if template.name == name:
                return template
        return None

    def get_type_group(self, name: str) -> GuiTypeGroup | None:
        for group in self.type_groups:
            if group.name == name:
                return group
        return None

    def get_root_definition(self, definition_kind: str) -> GuiRootDefinition | None:
        for definition in self.root_definitions:
            if definition.definition_kind == definition_kind:
                return definition
        return None

    def get_root_definition_by_name(self, name: str) -> GuiRootDefinition | None:
        for definition in self.root_definitions:
            if definition.internal_name == name:
                return definition
        return None


def parse_gui_document(text: str) -> GuiDocument:
    semantic_document = semantic.parse_semantic_document(text)
    constants: list[GuiConstant] = []
    templates: list[GuiTemplateDefinition] = []
    type_groups: list[GuiTypeGroup] = []
    root_definitions: list[GuiRootDefinition] = []

    for entry in semantic_document.entries:
        if entry.key.startswith("@"):
            constants.append(_parse_constant(entry))
            continue

        if not isinstance(entry.value, semantic.SemanticObject):
            continue

        template_name = _keyword_suffix(entry, "template")
        if template_name is not None:
            templates.append(
                GuiTemplateDefinition(
                    name=template_name,
                    body=entry.value,
                    entry=entry,
                )
            )
            continue

        type_group_name = _keyword_suffix(entry, "types")
        if type_group_name is not None:
            type_groups.append(_parse_type_group(entry, type_group_name))
            continue

        root_definitions.append(
            GuiRootDefinition(
                definition_kind=entry.key,
                body_prefix=entry.value.prefix,
                body=entry.value,
                internal_name=entry.value.get_scalar("name"),
                widget_id=entry.value.get_scalar("widgetid"),
                entry=entry,
            )
        )

    return GuiDocument(
        constants=tuple(constants),
        templates=tuple(templates),
        type_groups=tuple(type_groups),
        root_definitions=tuple(root_definitions),
        semantic_document=semantic_document,
    )


def _parse_constant(entry: semantic.SemanticEntry) -> GuiConstant:
    return GuiConstant(
        name=entry.key,
        value_text=entry_scalar_text(entry),
        value_object=entry_object(entry),
        entry=entry,
    )


def _parse_type_group(entry: semantic.SemanticEntry, group_name: str) -> GuiTypeGroup:
    assert isinstance(entry.value, semantic.SemanticObject)

    definitions = tuple(
        _parse_type_definition(child)
        for child in entry.value.entries
        if isinstance(child.value, semantic.SemanticObject)
        and _keyword_suffix(child, "type") is not None
    )

    return GuiTypeGroup(
        name=group_name,
        definitions=definitions,
        body=entry.value,
        entry=entry,
    )


def _parse_type_definition(entry: semantic.SemanticEntry) -> GuiTypeDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    type_name = _keyword_suffix(entry, "type")
    if type_name is None:
        raise ValueError(f"GUI type entry is missing a declared name: {entry.key!r}")

    return GuiTypeDefinition(
        name=type_name,
        widget_kind=entry.value.prefix or None,
        body=entry.value,
        internal_name=entry.value.get_scalar("name"),
        entry=entry,
    )


def _keyword_suffix(entry: semantic.SemanticEntry, keyword: str) -> str | None:
    head_tokens = entry.node.head_tokens
    if not head_tokens or head_tokens[0].text != keyword:
        return None

    suffix = " ".join(token.text for token in head_tokens[1:])
    return suffix or None
