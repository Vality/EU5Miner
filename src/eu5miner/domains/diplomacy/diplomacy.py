"""Higher-level diplomacy graph helpers over war and interaction adapters."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable, TypeVar

from eu5miner.domains.interfaces import flatten_definitions, get_by_name
from eu5miner.domains.diplomacy.casus_belli import CasusBelliDocument, CasusBelliDefinition
from eu5miner.domains.diplomacy.character_interactions import (
    CharacterInteractionDefinition,
    CharacterInteractionDocument,
)
from eu5miner.domains.diplomacy.country_interactions import (
    CountryInteractionDefinition,
    CountryInteractionDocument,
)
from eu5miner.domains.diplomacy.peace_treaties import PeaceTreatyDefinition, PeaceTreatyDocument
from eu5miner.domains.diplomacy.subject_types import SubjectTypeDefinition, SubjectTypeDocument
from eu5miner.domains.diplomacy import (
    WarFlowCatalog,
    build_war_flow_catalog,
    collect_casus_belli_references,
    collect_country_interaction_references,
    collect_subject_type_references,
)
from eu5miner.domains.diplomacy.wargoals import WargoalDocument
from eu5miner.formats.semantic import SemanticObject


ResolvedType = TypeVar("ResolvedType")
EdgeDefinition = PeaceTreatyDefinition | CountryInteractionDefinition | CharacterInteractionDefinition


@dataclass(frozen=True)
class DiplomacyReferenceEdge:
    source_name: str
    referenced_names: tuple[str, ...]


@dataclass(frozen=True)
class DiplomacyGraphReport:
    peace_treaty_casus_belli_links: tuple[DiplomacyReferenceEdge, ...]
    peace_treaty_subject_type_links: tuple[DiplomacyReferenceEdge, ...]
    country_interaction_casus_belli_links: tuple[DiplomacyReferenceEdge, ...]
    country_interaction_subject_type_links: tuple[DiplomacyReferenceEdge, ...]
    country_interaction_links: tuple[DiplomacyReferenceEdge, ...]
    character_interaction_subject_type_links: tuple[DiplomacyReferenceEdge, ...]
    missing_casus_belli_references: tuple[str, ...]
    missing_subject_type_references: tuple[str, ...]
    missing_country_interaction_references: tuple[str, ...]


@dataclass(frozen=True)
class DiplomacyGraphCatalog:
    war_flow_catalog: WarFlowCatalog
    country_interaction_definitions: tuple[CountryInteractionDefinition, ...] = ()
    character_interaction_definitions: tuple[CharacterInteractionDefinition, ...] = ()

    def get_country_interaction(self, name: str) -> CountryInteractionDefinition | None:
        return get_by_name(self.country_interaction_definitions, name)

    def get_character_interaction(self, name: str) -> CharacterInteractionDefinition | None:
        return get_by_name(self.character_interaction_definitions, name)

    def get_casus_belli(self, name: str) -> CasusBelliDefinition | None:
        return self.war_flow_catalog.get_casus_belli(name)

    def get_subject_type(self, name: str) -> SubjectTypeDefinition | None:
        return self.war_flow_catalog.get_subject_type(name)

    def get_casus_belli_references_for_country_interaction(
        self, name: str
    ) -> tuple[CasusBelliDefinition, ...]:
        definition = self.get_country_interaction(name)
        if definition is None:
            return ()
        return tuple(
            resolved
            for reference in collect_casus_belli_references(definition.body)
            if (resolved := self.get_casus_belli(reference)) is not None
        )

    def get_subject_type_references_for_country_interaction(
        self, name: str
    ) -> tuple[SubjectTypeDefinition, ...]:
        definition = self.get_country_interaction(name)
        if definition is None:
            return ()
        return tuple(
            resolved
            for reference in collect_subject_type_references(definition.body)
            if (resolved := self.get_subject_type(reference)) is not None
        )

    def get_subject_type_references_for_character_interaction(
        self, name: str
    ) -> tuple[SubjectTypeDefinition, ...]:
        definition = self.get_character_interaction(name)
        if definition is None:
            return ()
        return tuple(
            resolved
            for reference in collect_subject_type_references(definition.body)
            if (resolved := self.get_subject_type(reference)) is not None
        )

    def get_country_interaction_references_for_country_interaction(
        self, name: str
    ) -> tuple[CountryInteractionDefinition, ...]:
        definition = self.get_country_interaction(name)
        if definition is None:
            return ()
        return tuple(
            resolved
            for reference in collect_country_interaction_references(definition.body)
            if (resolved := self.get_country_interaction(reference)) is not None
        )

    def get_country_interactions_for_casus_belli(
        self, casus_belli_name: str
    ) -> tuple[CountryInteractionDefinition, ...]:
        return tuple(
            definition
            for definition in self.country_interaction_definitions
            if casus_belli_name in collect_casus_belli_references(definition.body)
        )

    def get_country_interactions_for_subject_type(
        self, subject_type_name: str
    ) -> tuple[CountryInteractionDefinition, ...]:
        return tuple(
            definition
            for definition in self.country_interaction_definitions
            if subject_type_name in collect_subject_type_references(definition.body)
        )

    def get_character_interactions_for_subject_type(
        self, subject_type_name: str
    ) -> tuple[CharacterInteractionDefinition, ...]:
        return tuple(
            definition
            for definition in self.character_interaction_definitions
            if subject_type_name in collect_subject_type_references(definition.body)
        )

    def build_report(self) -> DiplomacyGraphReport:
        peace_treaty_casus_belli_links, missing_cb_from_treaties = _build_edges(
            self.war_flow_catalog.peace_treaty_definitions,
            collect_casus_belli_references,
            self.war_flow_catalog.get_casus_belli,
        )
        peace_treaty_subject_type_links, missing_subject_from_treaties = _build_edges(
            self.war_flow_catalog.peace_treaty_definitions,
            collect_subject_type_references,
            self.war_flow_catalog.get_subject_type,
        )
        country_interaction_casus_belli_links, missing_cb_from_interactions = _build_edges(
            self.country_interaction_definitions,
            collect_casus_belli_references,
            self.war_flow_catalog.get_casus_belli,
        )
        country_interaction_subject_type_links, missing_subject_from_country = _build_edges(
            self.country_interaction_definitions,
            collect_subject_type_references,
            self.war_flow_catalog.get_subject_type,
        )
        country_interaction_links, missing_interaction_refs = _build_edges(
            self.country_interaction_definitions,
            collect_country_interaction_references,
            self.get_country_interaction,
        )
        character_interaction_subject_type_links, missing_subject_from_character = _build_edges(
            self.character_interaction_definitions,
            collect_subject_type_references,
            self.war_flow_catalog.get_subject_type,
        )

        return DiplomacyGraphReport(
            peace_treaty_casus_belli_links=peace_treaty_casus_belli_links,
            peace_treaty_subject_type_links=peace_treaty_subject_type_links,
            country_interaction_casus_belli_links=country_interaction_casus_belli_links,
            country_interaction_subject_type_links=country_interaction_subject_type_links,
            country_interaction_links=country_interaction_links,
            character_interaction_subject_type_links=character_interaction_subject_type_links,
            missing_casus_belli_references=tuple(
                sorted(missing_cb_from_treaties | missing_cb_from_interactions)
            ),
            missing_subject_type_references=tuple(
                sorted(
                    missing_subject_from_treaties
                    | missing_subject_from_country
                    | missing_subject_from_character
                )
            ),
            missing_country_interaction_references=tuple(sorted(missing_interaction_refs)),
        )


def build_diplomacy_graph_catalog(
    casus_belli_documents: Sequence[CasusBelliDocument],
    wargoal_documents: Sequence[WargoalDocument],
    peace_treaty_documents: Sequence[PeaceTreatyDocument],
    subject_type_documents: Sequence[SubjectTypeDocument] = (),
    country_interaction_documents: Sequence[CountryInteractionDocument] = (),
    character_interaction_documents: Sequence[CharacterInteractionDocument] = (),
) -> DiplomacyGraphCatalog:
    return DiplomacyGraphCatalog(
        war_flow_catalog=build_war_flow_catalog(
            casus_belli_documents=casus_belli_documents,
            wargoal_documents=wargoal_documents,
            peace_treaty_documents=peace_treaty_documents,
            subject_type_documents=subject_type_documents,
        ),
        country_interaction_definitions=flatten_definitions(country_interaction_documents),
        character_interaction_definitions=flatten_definitions(
            character_interaction_documents
        ),
    )


def build_diplomacy_graph_report(
    catalog: DiplomacyGraphCatalog,
) -> DiplomacyGraphReport:
    return catalog.build_report()


def _build_edges(
    definitions: Sequence[EdgeDefinition],
    collector: Callable[[SemanticObject], tuple[str, ...]],
    resolver: Callable[[str], ResolvedType | None],
) -> tuple[tuple[DiplomacyReferenceEdge, ...], set[str]]:
    edges: list[DiplomacyReferenceEdge] = []
    missing: set[str] = set()
    for definition in definitions:
        references = collector(definition.body)
        if not references:
            continue
        edges.append(
            DiplomacyReferenceEdge(
                source_name=definition.name,
                referenced_names=references,
            )
        )
        for reference in references:
            if resolver(reference) is None:
                missing.add(reference)
    return tuple(edges), missing
