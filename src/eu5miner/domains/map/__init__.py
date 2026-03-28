"""Map and location domain adapters."""

from eu5miner.domains.map.location_setup_links import (
	CountryLocationDefinition,
	CountryLocationDocument,
	CountryLocationGroup,
	LinkedLocationDefinition,
	LinkedLocationDocument,
	LocationCountryReference,
	LocationHierarchyDefinition,
	LocationHierarchyDocument,
	LocationSetupDefinition,
	LocationSetupDocument,
	build_linked_location_document,
	parse_country_location_document,
	parse_location_hierarchy_document,
	parse_location_setup_document,
)
from eu5miner.domains.map.map_csv_helpers import (
	MapAdjacencyDefinition,
	MapAdjacencyDocument,
	MapPortDefinition,
	MapPortDocument,
	parse_map_adjacencies_document,
	parse_map_ports_document,
)
from eu5miner.domains.map.map_text import (
	DefaultMapDocument,
	DefaultMapReferencedFiles,
	SoundTollDefinition,
	parse_default_map_document,
)
from eu5miner.domains.map.setup_countries import (
	SetupCountryDefinition,
	SetupCountryDocument,
	parse_setup_country_document,
)

__all__ = [
	"CountryLocationDefinition",
	"CountryLocationDocument",
	"CountryLocationGroup",
	"DefaultMapDocument",
	"DefaultMapReferencedFiles",
	"LinkedLocationDefinition",
	"LinkedLocationDocument",
	"LocationCountryReference",
	"LocationHierarchyDefinition",
	"LocationHierarchyDocument",
	"LocationSetupDefinition",
	"LocationSetupDocument",
	"MapAdjacencyDefinition",
	"MapAdjacencyDocument",
	"MapPortDefinition",
	"MapPortDocument",
	"SetupCountryDefinition",
	"SetupCountryDocument",
	"SoundTollDefinition",
	"build_linked_location_document",
	"parse_country_location_document",
	"parse_default_map_document",
	"parse_location_hierarchy_document",
	"parse_location_setup_document",
	"parse_map_adjacencies_document",
	"parse_map_ports_document",
	"parse_setup_country_document",
]
