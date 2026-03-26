from __future__ import annotations

from pathlib import Path

import pytest

from eu5miner.domains.government.laws import build_law_policy_catalog, parse_law_document
from eu5miner.formats.semantic import SemanticObject
from eu5miner.source import GameInstall


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.mark.timeout(5)
def test_parse_real_common_law_document(game_install: GameInstall) -> None:
    document = parse_law_document(_read_text(game_install.representative_files()["law_sample"]))

    law = document.get_definition("education_elites_law")
    assert law is not None
    assert law.law_category == "socioeconomic"
    assert law.potential is not None
    assert law.allow is not None
    assert "forums_of_thought" in law.policy_names()

    policy = law.get_policy("forums_of_thought")
    assert policy is not None
    assert policy.potential is not None
    assert len(policy.country_modifiers) == 1
    assert policy.estate_preferences == ("peasants_estate", "burghers_estate")
    assert policy.years == 2


@pytest.mark.timeout(5)
def test_parse_real_variant_law_documents(game_install: GameInstall) -> None:
    monarchy = parse_law_document(_read_text(game_install.representative_files()["law_secondary_sample"]))
    country_specific = parse_law_document(
        _read_text(game_install.representative_files()["law_country_specific_sample"])
    )
    io_document = parse_law_document(_read_text(game_install.representative_files()["law_io_sample"]))

    royal_court = monarchy.get_definition("royal_court_customs_law")
    assert royal_court is not None
    assert royal_court.law_gov_groups == ("monarchy",)
    military_court = royal_court.get_policy("military_court_policy")
    assert military_court is not None
    assert military_court.unique is True

    sumptuary = country_specific.get_definition("sumptuary_law")
    assert sumptuary is not None
    assert sumptuary.law_religion_groups == ("nahuatl",)
    garter = country_specific.get_definition("eng_order_of_the_garter_law")
    assert garter is not None
    assert garter.law_country_groups == ("ENG",)
    five_percent = country_specific.get_definition("fra_5_percent_tax")
    assert five_percent is not None
    five_percent_policy = five_percent.get_policy("five_percent_tax")
    assert five_percent_policy is not None
    assert five_percent_policy.months == 2

    civil_registration = io_document.get_definition("civil_registration")
    assert civil_registration is not None
    assert civil_registration.law_type == "international_organization"
    assert civil_registration.requires_vote is False
    assert civil_registration.custom_tags == ("forbids_no_policy",)
    delegated = civil_registration.get_policy("delegated_civil_registration_policy")
    assert delegated is not None
    assert delegated.on_pay_price is not None
    assert len(delegated.country_modifiers) == 3
    assert delegated.wants_this_policy_bias is not None


def test_law_parses_inline_variant_fields_and_builds_policy_catalog() -> None:
    document = parse_law_document(
        "sample_law = {\n"
        "    law_category = administrative\n"
        "    type = international_organization\n"
        "    requires_vote = yes\n"
        "    has_levels = yes\n"
        "    unique = no\n"
        "    custom_tags = { a b }\n"
        "    show_tags_in_ui = yes\n"
        "    law_gov_group = monarchy\n"
        "    law_religion_group = { catholic orthodox }\n"
        "    law_country_group = ENG\n"
        "    policy_a = {\n"
        "        price = { gold = 10 }\n"
        "        unique = yes\n"
        "        custom_tags = { policy_tag }\n"
        "        show_tags_in_ui = no\n"
        "        estate_preferences = { nobles_estate }\n"
        "        on_pay_price = { add = 1 }\n"
        "        on_activate = { add = 2 }\n"
        "        on_fully_activated = { add = 3 }\n"
        "        on_deactivate = { add = 4 }\n"
        "        international_organization_modifier = { foo = yes }\n"
        "        country_modifier = { bar = yes }\n"
        "        province_modifier = { baz = yes }\n"
        "        location_modifier = { qux = yes }\n"
        "        modifier = { m = yes }\n"
        "        leader_modifier = { lm = yes }\n"
        "        non_leader_modifier = { nlm = yes }\n"
        "        wants_this_policy_bias = { add = 1 }\n"
        "        wants_propose_policy = { add = 2 }\n"
        "        wants_keep_policy = { add = 3 }\n"
        "        reasons_to_join = { add = 4 }\n"
        "        diplomatic_capacity_cost = 2\n"
        "        can_join_trigger = { always = yes }\n"
        "        can_leave_trigger = { always = no }\n"
        "        auto_leave_trigger = { always = no }\n"
        "        auto_disband_trigger = { always = no }\n"
        "        can_declare_war = { always = yes }\n"
        "        has_military_access = { always = yes }\n"
        "        leader = { scope = recipient }\n"
        "        leader_type = country\n"
        "        leader_change_trigger_type = timed\n"
        "        leader_change_method = vote\n"
        "        leadership_election_resolution = res_a\n"
        "        months_between_leader_changes = 12\n"
        "        has_leader_country = yes\n"
        "        has_parliament = yes\n"
        "        can_invite_countries = no\n"
        "        gives_food_access_to_members = yes\n"
        "        has_dynastic_power = no\n"
        "        join_defensive_wars_always = yes\n"
        "        join_defensive_wars_auto_call = no\n"
        "        join_defensive_wars_can_call = yes\n"
        "        join_offensive_wars_always = no\n"
        "        join_offensive_wars_auto_call = yes\n"
        "        join_offensive_wars_can_call = no\n"
        "        min_opinion = 10\n"
        "        min_trust = 20\n"
        "        antagonism_towards_leader_modifier = 0.5\n"
        "        antagonism_modifier_for_taking_land_from_fellow_member = 0.25\n"
        "        no_cb_price_modifier_for_fellow_member = -0.1\n"
        "        payments_implemented = { pay_a pay_b }\n"
        "        payments_repealed = { pay_c }\n"
        "        special_statuses_implemented = { st_a }\n"
        "        special_statuses_repealed = { st_b }\n"
        "        leader_title_key = title_key\n"
        "        title_is_suffix = yes\n"
        "        level = 2\n"
        "        years = 3\n"
        "        months = 4\n"
        "        weeks = 5\n"
        "        days = 6\n"
        "    }\n"
        "}\n"
    )

    law = document.get_definition("sample_law")
    assert law is not None
    assert law.law_type == "international_organization"
    assert law.requires_vote is True
    assert law.has_levels is True
    assert law.unique is False
    assert law.custom_tags == ("a", "b")
    assert law.show_tags_in_ui is True
    assert law.law_gov_groups == ("monarchy",)
    assert law.law_religion_groups == ("catholic", "orthodox")
    assert law.law_country_groups == ("ENG",)

    policy = law.get_policy("policy_a")
    assert policy is not None
    assert isinstance(policy.price, SemanticObject)
    assert policy.unique is True
    assert policy.custom_tags == ("policy_tag",)
    assert policy.show_tags_in_ui is False
    assert policy.estate_preferences == ("nobles_estate",)
    assert policy.on_pay_price is not None
    assert policy.on_activate is not None
    assert policy.on_fully_activated is not None
    assert policy.on_deactivate is not None
    assert len(policy.international_organization_modifiers) == 1
    assert len(policy.country_modifiers) == 1
    assert len(policy.province_modifiers) == 1
    assert len(policy.location_modifiers) == 1
    assert policy.modifier is not None
    assert policy.leader_modifier is not None
    assert policy.non_leader_modifier is not None
    assert policy.wants_this_policy_bias is not None
    assert policy.wants_propose_policy is not None
    assert policy.wants_keep_policy is not None
    assert policy.reasons_to_join is not None
    assert policy.diplomatic_capacity_cost == "2"
    assert policy.can_join_trigger is not None
    assert policy.can_leave_trigger is not None
    assert policy.auto_leave_trigger is not None
    assert policy.auto_disband_trigger is not None
    assert policy.can_declare_war is not None
    assert policy.has_military_access is not None
    assert policy.leader is not None
    assert policy.leader_type == "country"
    assert policy.leader_change_trigger_type == "timed"
    assert policy.leader_change_method == "vote"
    assert policy.leadership_election_resolution == "res_a"
    assert policy.months_between_leader_changes == 12
    assert policy.has_leader_country is True
    assert policy.has_parliament is True
    assert policy.can_invite_countries is False
    assert policy.gives_food_access_to_members is True
    assert policy.has_dynastic_power is False
    assert policy.join_defensive_wars_always is True
    assert policy.join_defensive_wars_auto_call is False
    assert policy.join_defensive_wars_can_call is True
    assert policy.join_offensive_wars_always is False
    assert policy.join_offensive_wars_auto_call is True
    assert policy.join_offensive_wars_can_call is False
    assert policy.min_opinion == "10"
    assert policy.min_trust == "20"
    assert policy.payments_implemented == ("pay_a", "pay_b")
    assert policy.payments_repealed == ("pay_c",)
    assert policy.special_statuses_implemented == ("st_a",)
    assert policy.special_statuses_repealed == ("st_b",)
    assert policy.leader_title_key == "title_key"
    assert policy.title_is_suffix is True
    assert policy.level == 2
    assert policy.years == 3
    assert policy.months == 4
    assert policy.weeks == 5
    assert policy.days == 6

    catalog = build_law_policy_catalog((document,))
    assert catalog.get_policy("policy_a") is not None
    assert catalog.get_law_for_policy("policy_a") is law
    assert tuple(policy.name for policy in catalog.get_policies_for_category("administrative")) == (
        "policy_a",
    )
