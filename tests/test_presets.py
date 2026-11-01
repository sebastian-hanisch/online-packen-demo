"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; Permalink; feste Experimente."""

import onp_constants as C
import onp_evaluation as ev
import onp_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_control_ranges():
    for preset in C.PRESETS.values():
        assert preset["regel"] in C.REGELN and preset["folge"] in C.FOLGEN and preset["ordnung"] in C.ORDNUNGEN
        assert preset["n"] in C.N_OPTIONS and 0 <= preset["seed"] <= C.SEED_MAX


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_choice_has_a_help_text_and_defaults_are_valid():
    assert set(C.FOLGEN_HILFE) == set(C.FOLGEN) and set(C.REGEL_HILFE) == set(C.REGELN) and set(C.ORDNUNG_HILFE) == set(C.ORDNUNGEN)
    assert C.DEFAULT_FOLGE in C.FOLGEN and C.DEFAULT_REGEL in C.REGELN and C.DEFAULT_ORDNUNG in C.ORDNUNGEN and C.DEFAULT_N in C.N_OPTIONS
    assert list(C.N_OPTIONS) == sorted(C.N_OPTIONS) and C.N_OPTIONS[0] == C.N_MIN and C.N_OPTIONS[-1] == C.N_MAX


def test_the_phases_group_is_divisible_by_six_and_orders_are_in_the_sweep():
    assert C.PHASES_N % 6 == 0 and C.ORDER_NS[-1] % 6 == 0 and C.DEFAULT_N % 18 == 0
    assert set(C.TYPICAL_FOLGEN) <= set(C.FOLGEN) and not set(C.TYPICAL_FOLGEN) & {"Dreiphasenfolge (Gegner)", "abwechselnd halb und winzig (Gegner)", "von Hand (4 Stücke, wiederholt)"}


def test_experiment_rows_have_the_documented_shape():
    rows = ev.nf_adversary_rows(ns=(20, 40))
    assert [r["Stücke"] for r in rows] == [20, 40] and all(r["First Fit"] >= 1.0 for r in rows)
    rows = ev.phase_rows(group=12)
    assert [r["Präfix"] for r in rows] == ["nach Gruppe 1", "nach Gruppe 2", "nach Gruppe 3"] and [r["Optimum"] for r in rows] == [2, 6, 12]
    rows = ev.order_rows(group=12)
    assert [r["Reihenfolge"] for r in rows] == list(C.ORDNUNGEN)
    rows = ev.typical_rows(n=100, seeds=(1, 2))
    assert [r["Folge"] for r in rows] == list(C.TYPICAL_FOLGEN) and all(r[x] >= 1.0 - 1e-9 for r in rows for x in C.REGELN)
    rows = ev.growth_rows(ns=(50,), seeds=(1,))
    assert [r["n"] for r in rows] == [50]
