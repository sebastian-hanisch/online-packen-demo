"""Kern gegen Handrechnung auf der Mini-Instanz und auf kleinen Folgen von Hand."""

import pytest

import onp_algorithm as A
import onp_constants as C
from onp_scenario import make_items


def test_mini_instance_by_hand(mini):
    assert A.next_fit(mini) == [0, 1, 1, 2]
    assert A.first_fit(mini) == [0, 1, 0, 1]
    assert A.best_fit(mini) == [0, 1, 0, 1]
    assert A.harmonic(mini) == [0, 1, 1, 2]
    assert A.ffd(mini) == [0, 1, 0, 1]
    assert [A.bins_used(f(mini)) for f in (A.next_fit, A.first_fit, A.best_fit, A.harmonic, A.ffd)] == [3, 2, 2, 3, 2]


def test_best_fit_differs_from_first_fit_by_hand():
    # 3500, 4500, 1000: First Fit legt die 1000 in den ersten Behälter (3500 + 1000 = 4500); Best Fit in den Behälter, der danach am vollsten ist:
    # Behälter 1 hätte danach 1500 frei, Behälter 2 nur 500 frei (4500 + 1000 = 5500): Behälter 2.
    items = [3500, 4500, 1000]
    assert A.first_fit(items) == [0, 1, 0]
    assert A.best_fit(items) == [0, 1, 1]
    # 1000, 5000, 2000, 4000: der zweite Behälter wird für die 2000 geöffnet, die 4000 füllen ihn; beide Regeln gleich
    items = [1000, 5000, 2000, 4000]
    assert A.first_fit(items) == A.best_fit(items) == [0, 0, 1, 1]


def test_three_phase_by_hand_for_six_pieces():
    # N = 6: sechs 998 füllen einen Behälter (5988), 2001 passen zu zweit (4002), die 3001 stehen einzeln: 1 + 3 + 6 = 10 Behälter für jede Regel
    items = [998] * 6 + [2001] * 6 + [3001] * 6
    for rule in (A.next_fit, A.first_fit, A.best_fit, A.harmonic):
        assert A.bins_used(rule(items)) == 10, rule.__name__
    assert A.bins_used(A.ffd(items)) == 6                                # offline: ein Stück jeder Gruppe je Behälter (998 + 2001 + 3001 = 6000)


def test_alternating_by_hand_for_six_pieces():
    items = [3000, 1] * 3
    assert A.next_fit(items) == [0, 0, 1, 1, 2, 2]
    assert A.first_fit(items) == [0, 0, 1, 0, 1, 0]
    assert A.bins_used(A.best_fit(items)) == 2
    # Harmonic: die drei 3000 sind Klasse 2 (zwei je Behälter): 2 Behälter; die drei 1 sind klein und bekommen einen eigenen Behälter: 3 Behälter
    assert A.harmonic(items) == [0, 1, 0, 1, 2, 1] and A.bins_used(A.harmonic(items)) == 3


def test_harmonic_classes_by_hand():
    # 6000 // s: 3600 → 1, 3000 und 2400 → 2, 1500 → 4, 1000 → 6 = M: klein (1000 · 6 = 6000 ≤ 6000)
    assert A.harmonic([1500] * 8) == [0, 0, 0, 0, 1, 1, 1, 1]            # Klasse 4: vier Stücke je Behälter
    assert A.harmonic([1000] * 7) == [0, 0, 0, 0, 0, 0, 1]                # klein: Next Fit, sechs je Behälter
    assert A.harmonic([6000, 6000]) == [0, 1]                             # Klasse 1: je ein Stück


def test_harmonic_guarantee_by_hand_and_known_values():
    assert A.harmonic_guarantee(2) == 2.0                                 # ein Stück knapp über 1/2 und kleine bis 1/2 mit Gewicht 2
    assert A.harmonic_guarantee(3) == pytest.approx(1.75)                # 1 + 1/2 + (3/2)(1/6)
    assert A.harmonic_guarantee(4) == pytest.approx(31 / 18)             # 1 + 1/2 + 1/3 + (4/3)(1/12): hier 1,7222
    assert A.harmonic_guarantee(6) == pytest.approx(1.7)


def test_lower_bound_and_checker(mini):
    assert A.lower_bound(mini) == 2 and A.lower_bound([1]) == 1 and A.lower_bound([6000, 1]) == 2
    assert A.is_valid(mini, [0, 1, 0, 1]) and not A.is_valid(mini, [0, 0, 0, 0]) and not A.is_valid(mini, [0, 1, 0])
    assert not A.is_valid(mini, [0, 1, 0, -1])


def test_bin_loads_and_bins_used(mini):
    assert A.bin_loads(mini, [0, 1, 0, 1]) == [6000, 6000] and A.bin_loads([], []) == [] and A.bins_used([]) == 0
    assert A.bin_loads(mini, [0, 1, 1, 2]) == [3600, 5400, 3000]


def test_sorted_orders_of_the_same_stuff():
    assert make_items("von Hand (4 Stücke, wiederholt)", 4, "absteigend", 1) == [3600, 3000, 3000, 2400]
    assert make_items("von Hand (4 Stücke, wiederholt)", 4, "aufsteigend", 1) == [2400, 3000, 3000, 3600]
    assert make_items("von Hand (4 Stücke, wiederholt)", 8, "wie erzeugt", 1) == list(C.HAND_ITEMS) * 2
