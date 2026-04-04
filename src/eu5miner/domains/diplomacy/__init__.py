"""Public diplomacy package surface."""

from __future__ import annotations

from eu5miner.domains.diplomacy.diplomacy import (
    DiplomacyGraphCatalog,
    DiplomacyGraphReport,
    DiplomacyReferenceEdge,
    build_diplomacy_graph_catalog,
    build_diplomacy_graph_report,
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

__all__ = [
    "DiplomacyGraphCatalog",
    "DiplomacyGraphReport",
    "DiplomacyReferenceEdge",
    "WarFlowCatalog",
    "WarFlowReport",
    "WarReferenceEdge",
    "build_diplomacy_graph_catalog",
    "build_diplomacy_graph_report",
    "build_war_flow_catalog",
    "build_war_flow_report",
    "collect_casus_belli_references",
    "collect_country_interaction_references",
    "collect_subject_type_references",
]
