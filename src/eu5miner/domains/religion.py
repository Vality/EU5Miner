"""Higher-level helpers over religion-adjacent domain adapters."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from eu5miner.domains.holy_sites import HolySiteDefinition, HolySiteDocument
from eu5miner.domains.religions import ReligionDefinition, ReligionDocument
from eu5miner.domains.religious_aspects import (
    ReligiousAspectDefinition,
    ReligiousAspectDocument,
)
from eu5miner.domains.religious_factions import (
    ReligiousFactionDefinition,
    ReligiousFactionDocument,
)
from eu5miner.domains.religious_figures import (
    ReligiousFigureDefinition,
    ReligiousFigureDocument,
)
from eu5miner.domains.religious_focuses import (
    ReligiousFocusDefinition,
    ReligiousFocusDocument,
)
from eu5miner.domains.religious_schools import (
    ReligiousSchoolDefinition,
    ReligiousSchoolDocument,
)
from eu5miner.formats.semantic import SemanticObject, SemanticScalar


@dataclass(frozen=True)
class ReligionReferenceEdge:
    source_name: str
    referenced_names: tuple[str, ...]


@dataclass(frozen=True)
class ReligionReport:
    religion_aspect_links: tuple[ReligionReferenceEdge, ...]
    religion_faction_links: tuple[ReligionReferenceEdge, ...]
    religion_focus_links: tuple[ReligionReferenceEdge, ...]
    religion_school_links: tuple[ReligionReferenceEdge, ...]
    religion_holy_site_links: tuple[ReligionReferenceEdge, ...]
    religion_figure_links: tuple[ReligionReferenceEdge, ...]
    missing_religious_faction_references: tuple[str, ...]
    missing_religious_focus_references: tuple[str, ...]
    missing_religious_school_references: tuple[str, ...]


@dataclass(frozen=True)
class ReligionCatalog:
    religion_definitions: tuple[ReligionDefinition, ...] = ()
    religious_aspect_definitions: tuple[ReligiousAspectDefinition, ...] = ()
    religious_faction_definitions: tuple[ReligiousFactionDefinition, ...] = ()
    religious_focus_definitions: tuple[ReligiousFocusDefinition, ...] = ()
    religious_school_definitions: tuple[ReligiousSchoolDefinition, ...] = ()
    religious_figure_definitions: tuple[ReligiousFigureDefinition, ...] = ()
    holy_site_definitions: tuple[HolySiteDefinition, ...] = ()

    def get_religion(self, name: str) -> ReligionDefinition | None:
        for definition in self.religion_definitions:
            if definition.name == name:
                return definition
        return None

    def get_religious_aspect(self, name: str) -> ReligiousAspectDefinition | None:
        for definition in self.religious_aspect_definitions:
            if definition.name == name:
                return definition
        return None

    def get_religious_faction(self, name: str) -> ReligiousFactionDefinition | None:
        for definition in self.religious_faction_definitions:
            if definition.name == name:
                return definition
        return None

    def get_religious_focus(self, name: str) -> ReligiousFocusDefinition | None:
        for definition in self.religious_focus_definitions:
            if definition.name == name:
                return definition
        return None

    def get_religious_school(self, name: str) -> ReligiousSchoolDefinition | None:
        for definition in self.religious_school_definitions:
            if definition.name == name:
                return definition
        return None

    def get_religious_figure(self, name: str) -> ReligiousFigureDefinition | None:
        for definition in self.religious_figure_definitions:
            if definition.name == name:
                return definition
        return None

    def get_holy_site(self, name: str) -> HolySiteDefinition | None:
        for definition in self.holy_site_definitions:
            if definition.name == name:
                return definition
        return None

    def get_religious_aspects_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousAspectDefinition, ...]:
        return tuple(
            definition
            for definition in self.religious_aspect_definitions
            if religion_name in definition.religions
        )

    def get_religious_factions_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousFactionDefinition, ...]:
        religion = self.get_religion(religion_name)
        if religion is None:
            return ()
        return tuple(
            definition
            for definition in self.religious_faction_definitions
            if definition.name in religion.factions
        )

    def get_religious_focuses_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousFocusDefinition, ...]:
        religion = self.get_religion(religion_name)
        if religion is None:
            return ()
        return tuple(
            definition
            for definition in self.religious_focus_definitions
            if definition.name in religion.religious_focuses
        )

    def get_religious_schools_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousSchoolDefinition, ...]:
        religion = self.get_religion(religion_name)
        if religion is None:
            return ()
        explicit_school_names = set(religion.religious_schools)
        return tuple(
            definition
            for definition in self.religious_school_definitions
            if definition.name in explicit_school_names
            or _object_mentions_religion(definition.enabled_for_country, religion)
            or _object_mentions_religion(definition.enabled_for_character, religion)
        )

    def get_religious_figures_for_religion(
        self, religion_name: str
    ) -> tuple[ReligiousFigureDefinition, ...]:
        religion = self.get_religion(religion_name)
        if religion is None:
            return ()
        return tuple(
            definition
            for definition in self.religious_figure_definitions
            if _object_mentions_religion(definition.enabled_for_religion, religion)
        )

    def get_holy_sites_for_religion(self, religion_name: str) -> tuple[HolySiteDefinition, ...]:
        return tuple(
            definition
            for definition in self.holy_site_definitions
            if religion_name in definition.religions
        )

    def build_report(self) -> ReligionReport:
        aspect_links = _build_edges_without_resolution(
            self.religion_definitions,
            lambda definition: tuple(
                aspect.name for aspect in self.get_religious_aspects_for_religion(definition.name)
            ),
        )
        faction_links, missing_factions = _build_edges(
            self.religion_definitions,
            lambda definition: definition.factions,
            self.get_religious_faction,
        )
        focus_links, missing_focuses = _build_edges(
            self.religion_definitions,
            lambda definition: definition.religious_focuses,
            self.get_religious_focus,
        )
        school_links = _build_edges_without_resolution(
            self.religion_definitions,
            lambda definition: tuple(
                school.name for school in self.get_religious_schools_for_religion(definition.name)
            ),
        )
        missing_schools = tuple(
            sorted(
                {
                    school_name
                    for definition in self.religion_definitions
                    for school_name in definition.religious_schools
                    if self.get_religious_school(school_name) is None
                }
            )
        )
        holy_site_links = _build_edges_without_resolution(
            self.religion_definitions,
            lambda definition: tuple(
                site.name for site in self.get_holy_sites_for_religion(definition.name)
            ),
        )
        figure_links = _build_edges_without_resolution(
            self.religion_definitions,
            lambda definition: tuple(
                figure.name for figure in self.get_religious_figures_for_religion(definition.name)
            ),
        )
        return ReligionReport(
            religion_aspect_links=aspect_links,
            religion_faction_links=faction_links,
            religion_focus_links=focus_links,
            religion_school_links=school_links,
            religion_holy_site_links=holy_site_links,
            religion_figure_links=figure_links,
            missing_religious_faction_references=missing_factions,
            missing_religious_focus_references=missing_focuses,
            missing_religious_school_references=missing_schools,
        )


def build_religion_catalog(
    religion_documents: Sequence[ReligionDocument],
    religious_aspect_documents: Sequence[ReligiousAspectDocument] = (),
    religious_faction_documents: Sequence[ReligiousFactionDocument] = (),
    religious_focus_documents: Sequence[ReligiousFocusDocument] = (),
    religious_school_documents: Sequence[ReligiousSchoolDocument] = (),
    religious_figure_documents: Sequence[ReligiousFigureDocument] = (),
    holy_site_documents: Sequence[HolySiteDocument] = (),
) -> ReligionCatalog:
    return ReligionCatalog(
        religion_definitions=tuple(
            definition for document in religion_documents for definition in document.definitions
        ),
        religious_aspect_definitions=tuple(
            definition
            for document in religious_aspect_documents
            for definition in document.definitions
        ),
        religious_faction_definitions=tuple(
            definition
            for document in religious_faction_documents
            for definition in document.definitions
        ),
        religious_focus_definitions=tuple(
            definition
            for document in religious_focus_documents
            for definition in document.definitions
        ),
        religious_school_definitions=tuple(
            definition
            for document in religious_school_documents
            for definition in document.definitions
        ),
        religious_figure_definitions=tuple(
            definition
            for document in religious_figure_documents
            for definition in document.definitions
        ),
        holy_site_definitions=tuple(
            definition for document in holy_site_documents for definition in document.definitions
        ),
    )


def build_religion_report(catalog: ReligionCatalog) -> ReligionReport:
    return catalog.build_report()


def _build_edges[
    DefinitionT
](
    definitions: Sequence[DefinitionT],
    collector: Callable[[DefinitionT], tuple[str, ...]],
    resolver: Callable[[str], Any | None],
) -> tuple[tuple[ReligionReferenceEdge, ...], tuple[str, ...]]:
    edges: list[ReligionReferenceEdge] = []
    missing: set[str] = set()

    for definition in definitions:
        source_name = getattr(definition, "name")
        references = tuple(reference for reference in collector(definition) if reference)
        if not references:
            continue
        edges.append(ReligionReferenceEdge(source_name=source_name, referenced_names=references))
        for reference in references:
            if resolver(reference) is None:
                missing.add(reference)

    return tuple(edges), tuple(sorted(missing))


def _build_edges_without_resolution[
    DefinitionT
](
    definitions: Sequence[DefinitionT],
    collector: Callable[[DefinitionT], tuple[str, ...]],
) -> tuple[ReligionReferenceEdge, ...]:
    edges: list[ReligionReferenceEdge] = []
    for definition in definitions:
        source_name = getattr(definition, "name")
        references = tuple(reference for reference in collector(definition) if reference)
        if references:
            edges.append(ReligionReferenceEdge(source_name=source_name, referenced_names=references))
    return tuple(edges)


def _object_mentions_religion(body: SemanticObject | None, religion: ReligionDefinition) -> bool:
    if body is None:
        return False
    scalar_texts = set(_iter_scalar_texts(body))
    if f"religion:{religion.name}" in scalar_texts:
        return True
    if religion.group is not None and f"religion_group:{religion.group}" in scalar_texts:
        return True
    return False


def _iter_scalar_texts(body: SemanticObject) -> tuple[str, ...]:
    values: list[str] = []
    for entry in body.entries:
        if isinstance(entry.value, SemanticScalar):
            values.append(entry.value.text)
        elif isinstance(entry.value, SemanticObject):
            values.extend(_iter_scalar_texts(entry.value))
    return tuple(values)
