"""Public diplomacy package surface."""

from __future__ import annotations

from eu5miner.domains.diplomacy.casus_belli import (
    CasusBelliDefinition,
    CasusBelliDocument,
    parse_casus_belli_document,
)
from eu5miner.domains.diplomacy.character_interactions import (
    CharacterInteractionColumn,
    CharacterInteractionDefinition,
    CharacterInteractionDocument,
    CharacterInteractionSelectTrigger,
    parse_character_interaction_document,
)
from eu5miner.domains.diplomacy.country_interactions import (
    CountryInteractionColumn,
    CountryInteractionDefinition,
    CountryInteractionDocument,
    CountryInteractionSelectTrigger,
    parse_country_interaction_document,
)
from eu5miner.domains.diplomacy.diplomacy import (
    DiplomacyGraphCatalog,
    DiplomacyGraphReport,
    DiplomacyReferenceEdge,
    build_diplomacy_graph_catalog,
    build_diplomacy_graph_report,
)
from eu5miner.domains.diplomacy.generic_actions import (
    GenericActionColumn,
    GenericActionDefinition,
    GenericActionDocument,
    GenericActionSelectTrigger,
    parse_generic_action_document,
)
from eu5miner.domains.diplomacy.peace_treaties import (
    PeaceTreatyColumn,
    PeaceTreatyDefinition,
    PeaceTreatyDocument,
    PeaceTreatySelectTrigger,
    parse_peace_treaty_document,
)
from eu5miner.domains.diplomacy.subject_types import (
    SubjectTypeDefinition,
    SubjectTypeDocument,
    parse_subject_type_document,
)
from eu5miner.domains.diplomacy.war import (
    WarFlowCatalog,
    WarFlowReport,
    WarReferenceEdge,
    build_war_flow_catalog,
    build_war_flow_report,
    collect_casus_belli_references,
    collect_country_interaction_references,
    collect_subject_type_references,
)
from eu5miner.domains.diplomacy.wargoals import (
    WargoalDefinition,
    WargoalDocument,
    WargoalParticipantDefinition,
    parse_wargoal_document,
)

__all__ = [
    "CasusBelliDefinition",
    "CasusBelliDocument",
    "CharacterInteractionColumn",
    "CharacterInteractionDefinition",
    "CharacterInteractionDocument",
    "CharacterInteractionSelectTrigger",
    "CountryInteractionColumn",
    "CountryInteractionDefinition",
    "CountryInteractionDocument",
    "CountryInteractionSelectTrigger",
    "DiplomacyGraphCatalog",
    "DiplomacyGraphReport",
    "DiplomacyReferenceEdge",
    "GenericActionColumn",
    "GenericActionDefinition",
    "GenericActionDocument",
    "GenericActionSelectTrigger",
    "PeaceTreatyColumn",
    "PeaceTreatyDefinition",
    "PeaceTreatyDocument",
    "PeaceTreatySelectTrigger",
    "SubjectTypeDefinition",
    "SubjectTypeDocument",
    "WarFlowCatalog",
    "WarFlowReport",
    "WarReferenceEdge",
    "WargoalDefinition",
    "WargoalDocument",
    "WargoalParticipantDefinition",
    "build_diplomacy_graph_catalog",
    "build_diplomacy_graph_report",
    "build_war_flow_catalog",
    "build_war_flow_report",
    "collect_casus_belli_references",
    "collect_country_interaction_references",
    "collect_subject_type_references",
    "parse_casus_belli_document",
    "parse_character_interaction_document",
    "parse_country_interaction_document",
    "parse_generic_action_document",
    "parse_peace_treaty_document",
    "parse_subject_type_document",
    "parse_wargoal_document",
]
