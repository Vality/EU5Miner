"""Domain adapter for price definitions."""

from __future__ import annotations

from dataclasses import dataclass

from eu5miner.formats.semantic import (
    SemanticDocument,
    SemanticEntry,
    SemanticObject,
    parse_semantic_document,
)


@dataclass(frozen=True)
class PriceDefinition:
    """One price definition."""

    name: str
    body: SemanticObject
    scaled_manpower: str | None
    scaled_sailors: str | None
    scaled_gold: str | None
    scaled_recipient_gold: str | None
    gold_per_pop: str | None
    manpower: str | None
    sailors: str | None
    gold: str | None
    stability: str | None
    war_exhaustion: str | None
    inflation: str | None
    prestige: str | None
    army_tradition: str | None
    navy_tradition: str | None
    government_power: str | None
    legitimacy: str | None
    karma: str | None
    religious_influence: str | None
    purity: str | None
    honor: str | None
    doom: str | None
    rite_power: str | None
    yanantin: str | None
    complacency: str | None
    righteousness: str | None
    harmony: str | None
    self_control: str | None
    min_value: str | None
    min_scale: str | None
    max_scale: str | None
    entry: SemanticEntry

    def get_scalar(self, key: str) -> str | None:
        return self.body.get_scalar(key)


@dataclass(frozen=True)
class PriceDocument:
    """Parsed price file."""

    definitions: tuple[PriceDefinition, ...]
    semantic_document: SemanticDocument

    def names(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.definitions)

    def get_definition(self, name: str) -> PriceDefinition | None:
        for definition in self.definitions:
            if definition.name == name:
                return definition
        return None


def parse_price_document(text: str) -> PriceDocument:
    semantic_document = parse_semantic_document(text)
    definitions: list[PriceDefinition] = []

    for entry in semantic_document.entries:
        if not isinstance(entry.value, SemanticObject):
            continue

        body = entry.value
        definitions.append(
            PriceDefinition(
                name=entry.key,
                body=body,
                scaled_manpower=body.get_scalar("scaled_manpower"),
                scaled_sailors=body.get_scalar("scaled_sailors"),
                scaled_gold=body.get_scalar("scaled_gold"),
                scaled_recipient_gold=body.get_scalar("scaled_recipient_gold"),
                gold_per_pop=body.get_scalar("gold_per_pop"),
                manpower=body.get_scalar("manpower"),
                sailors=body.get_scalar("sailors"),
                gold=body.get_scalar("gold"),
                stability=body.get_scalar("stability"),
                war_exhaustion=body.get_scalar("war_exhaustion"),
                inflation=body.get_scalar("inflation"),
                prestige=body.get_scalar("prestige"),
                army_tradition=body.get_scalar("army_tradition"),
                navy_tradition=body.get_scalar("navy_tradition"),
                government_power=body.get_scalar("government_power"),
                legitimacy=body.get_scalar("legitimacy"),
                karma=body.get_scalar("karma"),
                religious_influence=body.get_scalar("religious_influence"),
                purity=body.get_scalar("purity"),
                honor=body.get_scalar("honor"),
                doom=body.get_scalar("doom"),
                rite_power=body.get_scalar("rite_power"),
                yanantin=body.get_scalar("yanantin"),
                complacency=body.get_scalar("complacency"),
                righteousness=body.get_scalar("righteousness"),
                harmony=body.get_scalar("harmony"),
                self_control=body.get_scalar("self_control"),
                min_value=body.get_scalar("min"),
                min_scale=body.get_scalar("min_scale"),
                max_scale=body.get_scalar("max_scale"),
                entry=entry,
            )
        )

    return PriceDocument(definitions=tuple(definitions), semantic_document=semantic_document)
