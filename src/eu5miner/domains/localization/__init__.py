"""Localization-related domain adapters."""

from eu5miner.domains.localization.localization_bundles import (
	LocalizationBundle,
	LocalizationBundleEntry,
	LocalizationReference,
	build_localization_bundle,
	collect_customizable_localization_references,
	collect_effect_localization_references,
	collect_trigger_localization_references,
	find_missing_localization_references,
)
from eu5miner.domains.localization.localization_helpers import (
	CustomizableLocalizationDefinition,
	CustomizableLocalizationDocument,
	CustomizableLocalizationText,
	EffectLocalizationDefinition,
	EffectLocalizationDocument,
	LocalizationVariant,
	TriggerLocalizationDefinition,
	TriggerLocalizationDocument,
	parse_customizable_localization_document,
	parse_effect_localization_document,
	parse_trigger_localization_document,
)

__all__ = [
	"CustomizableLocalizationDefinition",
	"CustomizableLocalizationDocument",
	"CustomizableLocalizationText",
	"EffectLocalizationDefinition",
	"EffectLocalizationDocument",
	"LocalizationBundle",
	"LocalizationBundleEntry",
	"LocalizationReference",
	"LocalizationVariant",
	"TriggerLocalizationDefinition",
	"TriggerLocalizationDocument",
	"build_localization_bundle",
	"collect_customizable_localization_references",
	"collect_effect_localization_references",
	"collect_trigger_localization_references",
	"find_missing_localization_references",
	"parse_customizable_localization_document",
	"parse_effect_localization_document",
	"parse_trigger_localization_document",
]
