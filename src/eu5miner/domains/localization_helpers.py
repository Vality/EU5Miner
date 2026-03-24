"""Domain adapters for customizable, effect, and trigger localization helpers."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats import semantic


@dataclass(frozen=True)
class LocalizationVariant:
    """One named localization variant mapping."""

    name: str
    localization_key: str
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class CustomizableLocalizationText:
    """One conditional text branch in a customizable localization definition."""

    localization_key: str | None
    trigger: semantic.SemanticObject | None
    fallback: bool | None
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class CustomizableLocalizationDefinition:
    """One customizable localization definition."""

    name: str
    body: semantic.SemanticObject
    scope_type: str | None
    texts: tuple[CustomizableLocalizationText, ...]
    random_valid: bool | None
    parent: str | None
    suffix: str | None
    fallback: bool | None
    entry: semantic.SemanticEntry


@dataclass(frozen=True)
class CustomizableLocalizationDocument:
    """Parsed customizable localization file."""

    definitions: tuple[CustomizableLocalizationDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> CustomizableLocalizationDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


@dataclass(frozen=True)
class EffectLocalizationDefinition:
    """One effect localization definition."""

    name: str
    body: semantic.SemanticObject
    variants: tuple[LocalizationVariant, ...]
    is_category: bool
    entry: semantic.SemanticEntry

    def get_variant(self, name: str) -> str | None:
        for variant in self.variants:
            if variant.name == name:
                return variant.localization_key
        return None


@dataclass(frozen=True)
class EffectLocalizationDocument:
    """Parsed effect localization file."""

    definitions: tuple[EffectLocalizationDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> EffectLocalizationDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


@dataclass(frozen=True)
class TriggerLocalizationDefinition:
    """One trigger localization definition."""

    name: str
    body: semantic.SemanticObject
    variants: tuple[LocalizationVariant, ...]
    entry: semantic.SemanticEntry

    def get_variant(self, name: str) -> str | None:
        for variant in self.variants:
            if variant.name == name:
                return variant.localization_key
        return None


@dataclass(frozen=True)
class TriggerLocalizationDocument:
    """Parsed trigger localization file."""

    definitions: tuple[TriggerLocalizationDefinition, ...]
    semantic_document: semantic.SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> TriggerLocalizationDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_customizable_localization_document(text: str) -> CustomizableLocalizationDocument:
    semantic_document = semantic.parse_semantic_document(text)
    definitions: list[CustomizableLocalizationDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, semantic.SemanticObject):
            continue
        definitions.append(_parse_customizable_localization_definition(entry))

    return CustomizableLocalizationDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def parse_effect_localization_document(text: str) -> EffectLocalizationDocument:
    semantic_document = semantic.parse_semantic_document(text)
    definitions: list[EffectLocalizationDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, semantic.SemanticObject):
            continue
        definitions.append(_parse_effect_localization_definition(entry))

    return EffectLocalizationDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def parse_trigger_localization_document(text: str) -> TriggerLocalizationDocument:
    semantic_document = semantic.parse_semantic_document(text)
    definitions: list[TriggerLocalizationDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, semantic.SemanticObject):
            continue
        definitions.append(_parse_trigger_localization_definition(entry))

    return TriggerLocalizationDocument(
        definitions=tuple(definitions),
        semantic_document=semantic_document,
    )


def _parse_customizable_localization_definition(
    entry: semantic.SemanticEntry,
) -> CustomizableLocalizationDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    texts = tuple(
        _parse_customizable_localization_text(text_entry)
        for text_entry in entry.value.find_entries("text")
        if isinstance(text_entry.value, semantic.SemanticObject)
    )

    return CustomizableLocalizationDefinition(
        name=entry.key,
        body=entry.value,
        scope_type=_normalized_scalar(entry.value.get_scalar("type")),
        texts=texts,
        random_valid=_parse_bool_or_none(entry.value.get_scalar("random_valid")),
        parent=_normalized_scalar(entry.value.get_scalar("parent")),
        suffix=_normalized_scalar(entry.value.get_scalar("suffix")),
        fallback=_parse_bool_or_none(entry.value.get_scalar("fallback")),
        entry=entry,
    )


def _parse_customizable_localization_text(
    entry: semantic.SemanticEntry,
) -> CustomizableLocalizationText:
    assert isinstance(entry.value, semantic.SemanticObject)

    return CustomizableLocalizationText(
        localization_key=_normalized_scalar(entry.value.get_scalar("localization_key")),
        trigger=entry.value.get_object("trigger"),
        fallback=_parse_bool_or_none(entry.value.get_scalar("fallback")),
        entry=entry,
    )


def _parse_effect_localization_definition(
    entry: semantic.SemanticEntry,
) -> EffectLocalizationDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    return EffectLocalizationDefinition(
        name=entry.key,
        body=entry.value,
        variants=_parse_variants(entry.value),
        is_category=entry.key.startswith("_"),
        entry=entry,
    )


def _parse_trigger_localization_definition(
    entry: semantic.SemanticEntry,
) -> TriggerLocalizationDefinition:
    assert isinstance(entry.value, semantic.SemanticObject)

    return TriggerLocalizationDefinition(
        name=entry.key,
        body=entry.value,
        variants=_parse_variants(entry.value),
        entry=entry,
    )


def _parse_variants(body: semantic.SemanticObject) -> tuple[LocalizationVariant, ...]:
    variants: list[LocalizationVariant] = []

    for child in body.entries:
        localization_key = _scalar_value(child)
        if localization_key is None:
            continue
        normalized_key = _strip_quotes(localization_key)
        if normalized_key is None:
            continue
        variants.append(
            LocalizationVariant(
                name=child.key,
                localization_key=normalized_key,
                entry=child,
            )
        )

    return tuple(variants)


def _scalar_value(entry: semantic.SemanticEntry | None) -> str | None:
    if entry is None or entry.value is None:
        return None
    if hasattr(entry.value, "text"):
        return entry.value.text
    return None


def _normalized_scalar(value: str | None) -> str | None:
    return _strip_quotes(value)


def _strip_quotes(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def _parse_bool_or_none(value: str | None) -> bool | None:
    if value is None:
        return None
    if value in {"yes", "true"}:
        return True
    if value in {"no", "false"}:
        return False
    return None
