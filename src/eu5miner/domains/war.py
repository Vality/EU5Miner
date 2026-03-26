"""Helpers that connect the war-related domain adapters."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from eu5miner.domains.casus_belli import CasusBelliDefinition, CasusBelliDocument
from eu5miner.domains.peace_treaties import PeaceTreatyDefinition, PeaceTreatyDocument
from eu5miner.domains.subject_types import SubjectTypeDefinition, SubjectTypeDocument
from eu5miner.domains.wargoals import WargoalDefinition, WargoalDocument
from eu5miner.formats.semantic import SemanticObject, SemanticScalar


@dataclass(frozen=True)
class WarFlowCatalog:
    """Cross-reference index over casus belli, wargoals, and peace treaties."""

    casus_belli_definitions: tuple[CasusBelliDefinition, ...]
    wargoal_definitions: tuple[WargoalDefinition, ...]
    peace_treaty_definitions: tuple[PeaceTreatyDefinition, ...]
    subject_type_definitions: tuple[SubjectTypeDefinition, ...] = ()

    def get_casus_belli(self, name: str) -> CasusBelliDefinition | None:
        for definition in self.casus_belli_definitions:
            if definition.name == name:
                return definition
        return None

    def get_wargoal(self, name: str) -> WargoalDefinition | None:
        for definition in self.wargoal_definitions:
            if definition.name == name:
                return definition
        return None

    def get_peace_treaty(self, name: str) -> PeaceTreatyDefinition | None:
        for definition in self.peace_treaty_definitions:
            if definition.name == name:
                return definition
        return None

    def get_subject_type(self, name: str) -> SubjectTypeDefinition | None:
        for definition in self.subject_type_definitions:
            if definition.name == name:
                return definition
        return None

    def get_wargoal_for_casus_belli(self, casus_belli_name: str) -> WargoalDefinition | None:
        casus_belli = self.get_casus_belli(casus_belli_name)
        if casus_belli is None or casus_belli.war_goal_type is None:
            return None
        return self.get_wargoal(casus_belli.war_goal_type)

    def get_casus_belli_for_wargoal(self, wargoal_name: str) -> tuple[CasusBelliDefinition, ...]:
        return tuple(
            definition
            for definition in self.casus_belli_definitions
            if definition.war_goal_type == wargoal_name
        )

    def get_casus_belli_references_for_peace_treaty(
        self, peace_treaty_name: str
    ) -> tuple[CasusBelliDefinition, ...]:
        peace_treaty = self.get_peace_treaty(peace_treaty_name)
        if peace_treaty is None:
            return ()

        references = collect_casus_belli_references(peace_treaty.body)
        return tuple(
            definition
            for name in references
            if (definition := self.get_casus_belli(name)) is not None
        )

    def get_peace_treaties_for_casus_belli(
        self, casus_belli_name: str
    ) -> tuple[PeaceTreatyDefinition, ...]:
        return tuple(
            definition
            for definition in self.peace_treaty_definitions
            if casus_belli_name in collect_casus_belli_references(definition.body)
        )

    def get_peace_treaties_for_wargoal(
        self, wargoal_name: str
    ) -> tuple[PeaceTreatyDefinition, ...]:
        matched_names = {
            definition.name for definition in self.get_casus_belli_for_wargoal(wargoal_name)
        }
        return tuple(
            definition
            for definition in self.peace_treaty_definitions
            if matched_names & set(collect_casus_belli_references(definition.body))
        )

    def get_subject_type_references_for_peace_treaty(
        self, peace_treaty_name: str
    ) -> tuple[SubjectTypeDefinition, ...]:
        peace_treaty = self.get_peace_treaty(peace_treaty_name)
        if peace_treaty is None:
            return ()

        references = collect_subject_type_references(peace_treaty.body)
        return tuple(
            definition
            for name in references
            if (definition := self.get_subject_type(name)) is not None
        )

    def get_peace_treaties_for_subject_type(
        self, subject_type_name: str
    ) -> tuple[PeaceTreatyDefinition, ...]:
        return tuple(
            definition
            for definition in self.peace_treaty_definitions
            if subject_type_name in collect_subject_type_references(definition.body)
        )


def build_war_flow_catalog(
    casus_belli_documents: Sequence[CasusBelliDocument],
    wargoal_documents: Sequence[WargoalDocument],
    peace_treaty_documents: Sequence[PeaceTreatyDocument],
    subject_type_documents: Sequence[SubjectTypeDocument] = (),
) -> WarFlowCatalog:
    return WarFlowCatalog(
        casus_belli_definitions=tuple(
            definition
            for document in casus_belli_documents
            for definition in document.definitions
        ),
        wargoal_definitions=tuple(
            definition
            for document in wargoal_documents
            for definition in document.definitions
        ),
        peace_treaty_definitions=tuple(
            definition
            for document in peace_treaty_documents
            for definition in document.definitions
        ),
        subject_type_definitions=tuple(
            definition
            for document in subject_type_documents
            for definition in document.definitions
        ),
    )


def collect_casus_belli_references(body: SemanticObject) -> tuple[str, ...]:
    return _collect_prefixed_references(body, "casus_belli:")


def collect_subject_type_references(body: SemanticObject) -> tuple[str, ...]:
    return _collect_prefixed_references(body, "subject_type:")


def _collect_prefixed_references(body: SemanticObject, prefix: str) -> tuple[str, ...]:
    references: list[str] = []
    seen: set[str] = set()
    for scalar_text in _iter_scalar_texts(body):
        if not scalar_text.startswith(prefix):
            continue
        reference = scalar_text.split(":", 1)[1]
        if reference in seen:
            continue
        seen.add(reference)
        references.append(reference)
    return tuple(references)


def _iter_scalar_texts(body: SemanticObject) -> tuple[str, ...]:
    values: list[str] = []
    _append_scalar_texts(body, values)
    return tuple(values)


def _append_scalar_texts(body: SemanticObject, values: list[str]) -> None:
    for entry in body.entries:
        if isinstance(entry.value, SemanticScalar):
            values.append(entry.value.text)
        elif isinstance(entry.value, SemanticObject):
            _append_scalar_texts(entry.value, values)
