"""Jede Zahl aus der README wird hier nachgerechnet (DEMO-PLAYBOOK §4): über dieselben Auswertungsfunktionen wie die App.

Feste Seeds und Längen wie in den Presets und Experimenten der App; Rundung wie in der README (drei Nachkommastellen)."""

import pytest

import onp_algorithm as A
import onp_constants as C
import onp_evaluation as ev


def _preset(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


# --- Presets -----------------------------------------------------------------------------------------------------------------------------


def test_mini_instance():
    a = _preset("Mini-Instanz von Hand")
    assert a.bins == {"Next Fit": 3, "First Fit": 2, "Best Fit": 2, "Harmonic": 3} and a.ref == 2 and a.ffd == 2 and a.lower == 2


def test_three_phase_preset_all_four_rules_need_two_thirds_more():
    a = _preset("Dreiphasenfolge (Gegner)")
    assert a.count == 1800 and a.ref == 600 and a.ffd == 600
    assert a.bins == {"Next Fit": 1000, "First Fit": 1000, "Best Fit": 1000, "Harmonic": 1000}
    assert all(q == pytest.approx(5 / 3) for q in a.ratios.values())


def test_the_same_stuff_shuffled_is_nearly_optimal_for_first_and_best_fit():
    a = _preset("Dieselben Stücke, zufällig gemischt")
    assert a.bins == {"Next Fit": 760, "First Fit": 610, "Best Fit": 610, "Harmonic": 1000} and a.ref == 600
    assert [round(a.ratios[r], 3) for r in C.REGELN] == [1.267, 1.017, 1.017, 1.667]


def test_next_fit_adversary_preset():
    a = _preset("Next-Fit-Gegner: halb und winzig")
    assert a.bins == {"Next Fit": 600, "First Fit": 301, "Best Fit": 301, "Harmonic": 301} and a.ref == 301
    assert a.ratios["Next Fit"] == pytest.approx(1.993, abs=5e-4)


def test_everyday_preset_first_fit_close_to_optimal():
    a = _preset("Alltag: gleich (0, 1]")
    assert a.bins == {"Next Fit": 809, "First Fit": 644, "Best Fit": 636, "Harmonic": 781} and (a.ref, a.ref_label, a.lower) == (619, "FFD", 607)
    assert [round(a.ratios[r], 3) for r in C.REGELN] == [1.307, 1.040, 1.027, 1.262]


def test_harmonic_everyday_preset():
    a = _preset("Harmonic im Alltag: drei Größen")
    assert a.bins == {"Next Fit": 580, "First Fit": 489, "Best Fit": 489, "Harmonic": 696} and a.ref == 489 and a.lower == 420
    assert a.ratios["Harmonic"] == pytest.approx(1.423, abs=5e-4)


# --- Experiment 1 -------------------------------------------------------------------------------------------------------------------------


def test_next_fit_against_the_alternating_sequence():
    rows = ev.nf_adversary_rows()
    assert [(r["Stücke"], r["Optimum"], r["Next Fit Behälter"]) for r in rows] == [(20, 6, 10), (200, 51, 100), (2000, 501, 1000)]
    assert [round(r["Next Fit"], 3) for r in rows] == [1.667, 1.961, 1.996]
    assert all(r[x] == 1.0 for r in rows for x in ("First Fit", "Best Fit", "Harmonic"))


def test_three_phase_prefixes():
    rows = ev.phase_rows()
    assert [r["Optimum"] for r in rows] == [100, 300, 600]
    for r in rows:
        assert r["FFD Behälter"] == r["Optimum"]
    assert [r["First Fit Behälter"] for r in rows] == [100, 400, 1000]
    assert all(r[f"{x} Behälter"] == r["First Fit Behälter"] for r in rows for x in C.REGELN)
    assert [round(r["First Fit"], 3) for r in rows] == [1.0, 1.333, 1.667]


# --- Experiment 2 -------------------------------------------------------------------------------------------------------------------------


def test_order_table_for_600_pieces_per_group():
    rows = {r["Reihenfolge"]: r for r in ev.order_rows(600)}
    assert [round(rows["wie erzeugt"][x], 3) for x in C.REGELN] == [1.667] * 4 and [round(rows["aufsteigend"][x], 3) for x in C.REGELN] == [1.667] * 4
    assert [round(rows["zufällig gemischt"][x], 3) for x in C.REGELN] == [1.267, 1.017, 1.017, 1.667]
    assert [round(rows["absteigend"][x], 3) for x in C.REGELN] == [1.667, 1.0, 1.0, 1.667]
    assert ev.order_rows(60)[1]["First Fit"] == pytest.approx(1.05, abs=5e-4)           # 60 Stücke je Gruppe: zufällig gemischt 1,05


# --- Experiment 3 -------------------------------------------------------------------------------------------------------------------------


TYPICAL = {
    "gleich (0, 1]": (1.014, 1.316, 1.034, 1.021, 1.274),
    "gleich (0, 0,5]": (1.000, 1.196, 1.013, 1.010, 1.163),
    "gleich (0,2, 0,8]": (1.012, 1.372, 1.043, 1.026, 1.390),
    "gleich (1/6, 1/2]": (1.050, 1.158, 1.014, 1.012, 1.119),
    "gleich (0, 0,1]": (1.000, 1.033, 1.002, 1.001, 1.033),
    "Lognormal (Paletten)": (1.006, 1.204, 1.024, 1.023, 1.239),
    "drei Größen": (1.165, 1.173, 1.001, 1.001, 1.414),
}


def test_typical_table():
    rows = {r["Folge"]: r for r in ev.typical_rows()}
    for folge, expected in TYPICAL.items():
        got = (rows[folge]["FFD / Summe"], *(rows[folge][r] for r in C.REGELN))
        assert got == pytest.approx(expected, abs=1.5e-3), folge


def test_typical_first_and_best_fit_stay_far_below_their_guarantee_and_harmonic_does_not():
    rows = ev.typical_rows()
    assert max(r["First Fit"] for r in rows) < 1.05 and max(r["Best Fit"] for r in rows) < 1.03 and max(r["Next Fit"] for r in rows) < 1.4
    worst = max(rows, key=lambda r: r["Harmonic"])
    assert worst["Folge"] == "drei Größen" and worst["Harmonic"] > 1.4 and worst["Harmonic"] > 1.35 * worst["First Fit"]


# --- Experiment 4 -------------------------------------------------------------------------------------------------------------------------


def test_growth_table():
    rows = ev.growth_rows()
    assert [r["n"] for r in rows] == [50, 200, 1000, 4000]
    assert [round(r["First Fit"], 3) for r in rows] == [1.044, 1.049, 1.041, 1.028] and [round(r["Best Fit"], 3) for r in rows] == [1.037, 1.037, 1.027, 1.017]
    assert [round(r["Next Fit"], 3) for r in rows] == [1.233, 1.280, 1.318, 1.317]


# --- Garantie von Harmonic -------------------------------------------------------------------------------------------------------------


def test_harmonic_guarantee_table_and_limit():
    expected = {2: 2.0, 3: 1.75, 4: 1.7222, 5: 1.7083, 6: 1.7, 8: 1.6939, 10: 1.6931, 12: 1.6926}
    for m, v in expected.items():
        assert A.harmonic_guarantee(m) == pytest.approx(v, abs=5e-5), m
    t, total = 2, 0.0
    for _ in range(8):
        total += 1 / (t - 1)
        t = t * (t - 1) + 1
    assert total == pytest.approx(1.69103, abs=5e-6)                      # Grenzwert (Literatur: 1,69103)
    assert all(a > b for a, b in zip(list(expected.values())[:-1], list(expected.values())[1:]))
    assert A.harmonic_guarantee(12) > total


def test_three_phase_with_200_pieces_per_group_is_not_exactly_five_thirds():
    a = ev.analyse(ev.Settings("First Fit", "Dreiphasenfolge (Gegner)", "wie erzeugt", 600, 7))
    assert (a.bins["First Fit"], a.ref) == (333, 200) and a.ratios["First Fit"] == pytest.approx(1.665)
