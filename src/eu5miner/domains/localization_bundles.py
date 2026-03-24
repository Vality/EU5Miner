"""Localization bundle indexing and helper cross-reference utilities."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.domains.localization_helpers import CustomizableLocalizationDocument
from eu5miner.domains.localization_helpers import EffectLocalizationDefinition
from eu5miner.domains.localization_helpers import EffectLocalizationDocument
from eu5miner.domains.localization_helpers import TriggerLocalizationDefinition
from eu5miner.domains.localization_helpers import TriggerLocalizationDocument
from eu5miner.formats.localization import LocalizationFile
from eu5miner.formats.localization import parse_localization


@dataclass(frozen=True)
class LocalizationBundleEntry:
    """One localization key/value entry plus its source file label."""

    key: str
    value: str
    source_name: str


@dataclass(frozen=True)
class LocalizationBundle:
    """Merged localization entries for one language across multiple files."""

    language: str
    entries: tuple[LocalizationBundleEntry, ...]

    def keys(self) -> tuple[str, ...]:
        return tuple(entry.key for entry in self.entries)

    def find_entries(self, key: str) -> tuple[LocalizationBundleEntry, ...]:
        return tuple(entry for entry in self.entries if entry.key == key)

    def get_entry(self, key: str) -> LocalizationBundleEntry | None:
        matches = self.find_entries(key)
        if not matches:
            return None
        return matches[-1]

    def get_value(self, key: str) -> str | None:
        entry = self.get_entry(key)
        if entry is None:
            return None
        return entry.value

    def duplicate_keys(self) -> tuple[str, ...]:
        counts: dict[str, int] = {}
        for entry in self.entries:
            counts[entry.key] = counts.get(entry.key, 0) + 1
        return tuple(sorted(key for key, count in counts.items() if count > 1))


@dataclass(frozen=True)
class LocalizationReference:
    """One emitted localization-key reference from a helper definition."""

    family: str
    definition_name: str
    variant_name: str
    localization_key: str


def build_localization_bundle(sources: tuple[tuple[str, str], ...]) -> LocalizationBundle:
    parsed_sources = tuple((source_name, parse_localization(text)) for source_name, text in sources)
    if not parsed_sources:
        raise ValueError("At least one localization source is required")

    language = parsed_sources[0][1].language
    if any(localization_file.language != language for _, localization_file in parsed_sources[1:]):
        raise ValueError("All localization sources in a bundle must share the same language")

    entries: list[LocalizationBundleEntry] = []
    for source_name, localization_file in parsed_sources:
        entries.extend(_bundle_entries_for_file(source_name, localization_file))

    return LocalizationBundle(language=language, entries=tuple(entries))


def collect_customizable_localization_references(
    document: CustomizableLocalizationDocument,
) -> tuple[LocalizationReference, ...]:
    references: list[LocalizationReference] = []

    for definition in document.definitions:
        for index, text in enumerate(definition.texts, start=1):
            if text.localization_key is None:
                continue
            references.append(
                LocalizationReference(
                    family="customizable_localization",
                    definition_name=definition.name,
                    variant_name=f"text[{index}]",
                    localization_key=text.localization_key,
                )
            )

    return tuple(references)


def collect_effect_localization_references(
    document: EffectLocalizationDocument,
) -> tuple[LocalizationReference, ...]:
    return _collect_variant_references("effect_localization", document.definitions)


def collect_trigger_localization_references(
    document: TriggerLocalizationDocument,
) -> tuple[LocalizationReference, ...]:
    return _collect_variant_references("trigger_localization", document.definitions)


def find_missing_localization_references(
    bundle: LocalizationBundle,
    references: tuple[LocalizationReference, ...],
) -> tuple[LocalizationReference, ...]:
    return tuple(
        reference
        for reference in references
        if bundle.get_entry(reference.localization_key) is None
    )


def _bundle_entries_for_file(
    source_name: str,
    localization_file: LocalizationFile,
) -> tuple[LocalizationBundleEntry, ...]:
    return tuple(
        LocalizationBundleEntry(
            key=entry.key,
            value=entry.value,
            source_name=source_name,
        )
        for entry in localization_file.entries
    )


def _collect_variant_references(
    family: str,
    definitions: tuple[EffectLocalizationDefinition | TriggerLocalizationDefinition, ...],
) -> tuple[LocalizationReference, ...]:
    references: list[LocalizationReference] = []

    for definition in definitions:
        for variant in definition.variants:
            references.append(
                LocalizationReference(
                    family=family,
                    definition_name=definition.name,
                    variant_name=variant.name,
                    localization_key=variant.localization_key,
                )
            )

    return tuple(references)
