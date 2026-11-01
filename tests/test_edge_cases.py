"""Randfälle: kleinste Folgen, Extremwerte der Regler, jede Folge hat die gewünschte Gestalt."""

import pytest

import onp_algorithm as A
import onp_constants as C
import onp_evaluation as ev
from onp_scenario import known_optimum, make_items


@pytest.mark.parametrize("folge", C.FOLGEN)
@pytest.mark.parametrize("ordnung", C.ORDNUNGEN)
@pytest.mark.parametrize("n", [4, 12, 100])
def test_items_are_in_range_reproducible_and_of_the_expected_count(folge, ordnung, n):
    items = make_items(folge, n, ordnung, 5)
    assert items == make_items(folge, n, ordnung, 5)
    assert all(isinstance(s, int) and 1 <= s <= C.CAPACITY for s in items)
    expected = {"Dreiphasenfolge (Gegner)": 3 * (n // 3), "abwechselnd halb und winzig (Gegner)": 2 * (n // 2), "von Hand (4 Stücke, wiederholt)": 4 * (n // 4)}
    assert len(items) == expected.get(folge, n)


def test_orders_are_rearrangements_of_the_same_stuff():
    for folge in C.FOLGEN:
        base = sorted(make_items(folge, 120, "wie erzeugt", 3))
        for ordnung in C.ORDNUNGEN:
            assert sorted(make_items(folge, 120, ordnung, 3)) == base
        assert make_items(folge, 120, "aufsteigend", 3) == base and make_items(folge, 120, "absteigend", 3) == base[::-1]


def test_shuffled_order_depends_on_the_seed_and_differs_from_the_original():
    a = make_items("gleich (0, 1]", 200, "zufällig gemischt", 1)
    assert a != make_items("gleich (0, 1]", 200, "wie erzeugt", 1) and a != make_items("gleich (0, 1]", 200, "zufällig gemischt", 2)


def test_distribution_ranges():
    assert max(make_items("gleich (0, 0,5]", 2000, "wie erzeugt", 1)) <= C.CAPACITY // 2
    items = make_items("gleich (0,2, 0,8]", 2000, "wie erzeugt", 1)
    assert min(items) >= C.CAPACITY // 5 and max(items) <= 4 * C.CAPACITY // 5
    items = make_items("gleich (1/6, 1/2]", 2000, "wie erzeugt", 1)
    assert min(items) >= C.CAPACITY // 6 and max(items) <= C.CAPACITY // 2
    assert max(make_items("gleich (0, 0,1]", 2000, "wie erzeugt", 1)) <= C.CAPACITY // 10
    assert set(make_items("drei Größen", 2000, "wie erzeugt", 1)) == set(C.THREE_SIZES)
    assert max(make_items("Lognormal (Paletten)", 2000, "wie erzeugt", 1)) <= C.CAPACITY


def test_gegner_sequences_by_hand():
    assert make_items("Dreiphasenfolge (Gegner)", 6, "wie erzeugt", 0) == [998, 998, 2001, 2001, 3001, 3001]
    assert make_items("abwechselnd halb und winzig (Gegner)", 6, "wie erzeugt", 0) == [3000, 1, 3000, 1, 3000, 1]
    assert sum(C.PHASE_SIZES) == C.CAPACITY                               # je ein Stück jeder Gruppe füllt einen Behälter genau


def test_known_optimum_by_hand():
    assert known_optimum("Dreiphasenfolge (Gegner)", 600) == 200 and known_optimum("Dreiphasenfolge (Gegner)", 12) == 4
    assert known_optimum("abwechselnd halb und winzig (Gegner)", 6) == 2 and known_optimum("abwechselnd halb und winzig (Gegner)", 8) == 3
    assert known_optimum("von Hand (4 Stücke, wiederholt)", 12) == 6 and known_optimum("gleich (0, 1]", 100) is None


def test_extreme_settings_run_for_every_folge():
    for folge in C.FOLGEN:
        for n in (C.N_MIN, C.N_MAX):
            a = ev.analyse(ev.Settings("Harmonic", folge, "wie erzeugt", n, C.SEED_MAX))
            assert a.lower <= a.ffd and all(b >= a.lower for b in a.bins.values())


def test_single_piece_and_full_piece():
    for rule in A.RULES.values():
        assert A.bins_used(rule([1])) == 1 and A.bins_used(rule([C.CAPACITY])) == 1 and A.bins_used(rule([C.CAPACITY] * 5)) == 5 and rule([]) == []


def test_ratio_guard_and_trace_shape():
    assert ev.ratio(5, 0) == 1.0
    a = ev.analyse(ev.Settings("Next Fit", "von Hand (4 Stücke, wiederholt)", "wie erzeugt", 4, 1))
    assert [r["Next Fit"] for r in a.trace] == [1, 2, 2, 3] and [r["First Fit"] for r in a.trace] == [1, 2, 1, 2]
    assert a.bins == {"Next Fit": 3, "First Fit": 2, "Best Fit": 2, "Harmonic": 3} and (a.ref, a.ref_label) == (2, "Optimum")
    assert len(ev.analyse(ev.Settings(n=1200, folge="gleich (0, 1]")).trace) == C.TRACE_LEN


def test_fills_are_percentages_and_sum_to_the_total():
    a = ev.analyse(ev.Settings("First Fit", "gleich (0, 1]", "wie erzeugt", 600, 3))
    items = make_items("gleich (0, 1]", 600, "wie erzeugt", 3)
    assert all(0 < f <= 100 for f in a.fills) and len(a.fills) == a.bins["First Fit"]
    assert sum(a.fills) * C.CAPACITY / 100 == pytest.approx(sum(items))
