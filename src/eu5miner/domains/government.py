"""Higher-level helpers over government, law, estate, and parliament adapters."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from eu5miner.domains.interfaces import flatten_definitions, get_by_name
from eu5miner.domains.estate_privileges import (
    EstatePrivilegeDefinition,
    EstatePrivilegeDocument,
)
from eu5miner.domains.estates import EstateDefinition, EstateDocument
from eu5miner.domains.government_reforms import (
    GovernmentReformDefinition,
    GovernmentReformDocument,
)
from eu5miner.domains.government_types import GovernmentTypeDefinition, GovernmentTypeDocument
from eu5miner.domains.laws import (
    LawDefinition,
    LawDocument,
    LawPolicyCatalog,
    LawPolicyDefinition,
    build_law_policy_catalog,
)
from eu5miner.domains.parliament_agendas import (
    ParliamentAgendaDefinition,
    ParliamentAgendaDocument,
)
from eu5miner.domains.parliament_issues import (
    ParliamentIssueDefinition,
    ParliamentIssueDocument,
)
from eu5miner.domains.parliament_types import (
    ParliamentTypeDefinition,
    ParliamentTypeDocument,
)

@dataclass(frozen=True)
class GovernmentReferenceEdge:
    source_name: str
    referenced_names: tuple[str, ...]


@dataclass(frozen=True)
class GovernmentReport:
    government_type_default_estate_links: tuple[GovernmentReferenceEdge, ...]
    reform_government_links: tuple[GovernmentReferenceEdge, ...]
    law_government_group_links: tuple[GovernmentReferenceEdge, ...]
    privilege_estate_links: tuple[GovernmentReferenceEdge, ...]
    policy_estate_preference_links: tuple[GovernmentReferenceEdge, ...]
    parliament_agenda_estate_links: tuple[GovernmentReferenceEdge, ...]
    parliament_issue_estate_links: tuple[GovernmentReferenceEdge, ...]
    missing_government_type_references: tuple[str, ...]
    missing_estate_references: tuple[str, ...]


@dataclass(frozen=True)
class GovernmentCatalog:
    government_type_definitions: tuple[GovernmentTypeDefinition, ...] = ()
    government_reform_definitions: tuple[GovernmentReformDefinition, ...] = ()
    law_definitions: tuple[LawDefinition, ...] = ()
    law_policy_catalog: LawPolicyCatalog = LawPolicyCatalog(())
    estate_definitions: tuple[EstateDefinition, ...] = ()
    estate_privilege_definitions: tuple[EstatePrivilegeDefinition, ...] = ()
    parliament_type_definitions: tuple[ParliamentTypeDefinition, ...] = ()
    parliament_agenda_definitions: tuple[ParliamentAgendaDefinition, ...] = ()
    parliament_issue_definitions: tuple[ParliamentIssueDefinition, ...] = ()

    def get_government_type(self, name: str) -> GovernmentTypeDefinition | None:
        return get_by_name(self.government_type_definitions, name)

    def get_reform(self, name: str) -> GovernmentReformDefinition | None:
        return get_by_name(self.government_reform_definitions, name)

    def get_law(self, name: str) -> LawDefinition | None:
        return get_by_name(self.law_definitions, name)

    def get_policy(self, name: str) -> LawPolicyDefinition | None:
        return self.law_policy_catalog.get_policy(name)

    def get_estate(self, name: str) -> EstateDefinition | None:
        return get_by_name(self.estate_definitions, name)

    def get_privilege(self, name: str) -> EstatePrivilegeDefinition | None:
        return get_by_name(self.estate_privilege_definitions, name)

    def get_parliament_type(self, name: str) -> ParliamentTypeDefinition | None:
        return get_by_name(self.parliament_type_definitions, name)

    def get_parliament_agenda(self, name: str) -> ParliamentAgendaDefinition | None:
        return get_by_name(self.parliament_agenda_definitions, name)

    def get_parliament_issue(self, name: str) -> ParliamentIssueDefinition | None:
        return get_by_name(self.parliament_issue_definitions, name)

    def get_default_estate_for_government(self, government_name: str) -> EstateDefinition | None:
        definition = self.get_government_type(government_name)
        if definition is None or definition.default_character_estate is None:
            return None
        return self.get_estate(definition.default_character_estate)

    def get_reforms_for_government(self, government_name: str) -> tuple[GovernmentReformDefinition, ...]:
        return tuple(
            definition
            for definition in self.government_reform_definitions
            if definition.government == government_name
        )

    def get_laws_for_government(self, government_name: str) -> tuple[LawDefinition, ...]:
        return tuple(
            definition
            for definition in self.law_definitions
            if government_name in definition.law_gov_groups
        )

    def get_policies_for_estate(self, estate_name: str) -> tuple[LawPolicyDefinition, ...]:
        return tuple(
            policy
            for definition in self.law_policy_catalog.law_definitions
            for policy in definition.policies
            if estate_name in policy.estate_preferences
        )

    def get_privileges_for_estate(self, estate_name: str) -> tuple[EstatePrivilegeDefinition, ...]:
        return tuple(
            definition
            for definition in self.estate_privilege_definitions
            if definition.estate == estate_name
        )

    def get_parliament_agendas_for_estate(
        self, estate_name: str
    ) -> tuple[ParliamentAgendaDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_agenda_definitions
            if estate_name in definition.estates
        )

    def get_parliament_issues_for_estate(
        self, estate_name: str
    ) -> tuple[ParliamentIssueDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_issue_definitions
            if estate_name in definition.estates
        )

    def get_parliament_agendas_for_special_status(
        self, special_status: str
    ) -> tuple[ParliamentAgendaDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_agenda_definitions
            if special_status in definition.special_statuses
        )

    def get_parliament_issues_for_special_status(
        self, special_status: str
    ) -> tuple[ParliamentIssueDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_issue_definitions
            if special_status in definition.special_statuses
        )

    def get_country_parliament_types(self) -> tuple[ParliamentTypeDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_type_definitions
            if definition.parliament_type == "country"
        )

    def get_international_organization_parliament_types(
        self,
    ) -> tuple[ParliamentTypeDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_type_definitions
            if definition.parliament_type == "international_organization"
        )

    def get_country_parliament_agendas(self) -> tuple[ParliamentAgendaDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_agenda_definitions
            if definition.agenda_type in {None, "country"}
        )

    def get_international_organization_parliament_agendas(
        self,
    ) -> tuple[ParliamentAgendaDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_agenda_definitions
            if definition.agenda_type == "international_organization"
        )

    def get_country_parliament_issues(self) -> tuple[ParliamentIssueDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_issue_definitions
            if definition.issue_type in {None, "country"}
        )

    def get_international_organization_parliament_issues(
        self,
    ) -> tuple[ParliamentIssueDefinition, ...]:
        return tuple(
            definition
            for definition in self.parliament_issue_definitions
            if definition.issue_type == "international_organization"
        )

    def build_report(self) -> GovernmentReport:
        default_estate_links, missing_default_estates = _build_edges(
            self.government_type_definitions,
            lambda definition: (definition.default_character_estate,)
            if definition.default_character_estate is not None
            else (),
            self.get_estate,
        )
        reform_links, missing_reform_governments = _build_edges(
            self.government_reform_definitions,
            lambda definition: (definition.government,) if definition.government is not None else (),
            self.get_government_type,
        )
        law_links, missing_law_governments = _build_edges(
            self.law_definitions,
            lambda definition: definition.law_gov_groups,
            self.get_government_type,
        )
        privilege_links, missing_privilege_estates = _build_edges(
            self.estate_privilege_definitions,
            lambda definition: (definition.estate,) if definition.estate is not None else (),
            self.get_estate,
        )
        policy_links, missing_policy_estates = _build_edges(
            tuple(
                policy
                for definition in self.law_policy_catalog.law_definitions
                for policy in definition.policies
            ),
            lambda definition: definition.estate_preferences,
            self.get_estate,
        )
        agenda_links, missing_agenda_estates = _build_edges(
            self.parliament_agenda_definitions,
            lambda definition: definition.estates,
            self.get_estate,
        )
        issue_links, missing_issue_estates = _build_edges(
            self.parliament_issue_definitions,
            lambda definition: definition.estates,
            self.get_estate,
        )

        return GovernmentReport(
            government_type_default_estate_links=default_estate_links,
            reform_government_links=reform_links,
            law_government_group_links=law_links,
            privilege_estate_links=privilege_links,
            policy_estate_preference_links=policy_links,
            parliament_agenda_estate_links=agenda_links,
            parliament_issue_estate_links=issue_links,
            missing_government_type_references=tuple(
                sorted(missing_reform_governments | missing_law_governments)
            ),
            missing_estate_references=tuple(
                sorted(
                    missing_default_estates
                    | missing_privilege_estates
                    | missing_policy_estates
                    | missing_agenda_estates
                    | missing_issue_estates
                )
            ),
        )


def build_government_catalog(
    government_type_documents: Sequence[GovernmentTypeDocument] = (),
    government_reform_documents: Sequence[GovernmentReformDocument] = (),
    law_documents: Sequence[LawDocument] = (),
    estate_documents: Sequence[EstateDocument] = (),
    estate_privilege_documents: Sequence[EstatePrivilegeDocument] = (),
    parliament_type_documents: Sequence[ParliamentTypeDocument] = (),
    parliament_agenda_documents: Sequence[ParliamentAgendaDocument] = (),
    parliament_issue_documents: Sequence[ParliamentIssueDocument] = (),
) -> GovernmentCatalog:
    law_definitions = flatten_definitions(law_documents)
    return GovernmentCatalog(
        government_type_definitions=flatten_definitions(government_type_documents),
        government_reform_definitions=flatten_definitions(government_reform_documents),
        law_definitions=law_definitions,
        law_policy_catalog=build_law_policy_catalog(law_documents),
        estate_definitions=flatten_definitions(estate_documents),
        estate_privilege_definitions=flatten_definitions(estate_privilege_documents),
        parliament_type_definitions=flatten_definitions(parliament_type_documents),
        parliament_agenda_definitions=flatten_definitions(parliament_agenda_documents),
        parliament_issue_definitions=flatten_definitions(parliament_issue_documents),
    )


def build_government_report(catalog: GovernmentCatalog) -> GovernmentReport:
    return catalog.build_report()


def _build_edges(
    definitions: Sequence[Any],
    collector: Callable[[Any], tuple[str, ...]],
    resolver: Callable[[str], object | None],
) -> tuple[tuple[GovernmentReferenceEdge, ...], set[str]]:
    edges: list[GovernmentReferenceEdge] = []
    missing: set[str] = set()
    for definition in definitions:
        references = collector(definition)
        if not references:
            continue
        edges.append(
            GovernmentReferenceEdge(
                source_name=str(getattr(definition, "name")),
                referenced_names=references,
            )
        )
        for reference in references:
            if resolver(reference) is None:
                missing.add(reference)
    return tuple(edges), missing
