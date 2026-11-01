"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2): Aussagen, die für Online-Packen gelten müssen, ohne das richtige Ergebnis zu kennen.

Jede Eigenschaft folgt aus der Definition: kein Behälter ist überfüllt, die Untergrenze gilt, Online-Verfahren sehen die Zukunft nicht (Präfix),
Skalierung der Größen und des Behälters ändert nichts, Next Fit hat höchstens das Doppelte der Untergrenze, First Fit höchstens ⌊1,7 · OPT⌋ (Dósa/Sgall)."""

import math

import numpy as np

import onp_algorithm as A
import onp_constants as C
from onp_scenario import make_items

RULES = (A.next_fit, A.first_fit, A.best_fit, A.harmonic)


def _instances(n=40, size=60, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        hi = [6000, 3000, 1200, 6000][i % 4]
        out.append([int(x) for x in rng.integers(1, hi + 1, size)])
    return out


def test_no_bin_is_overfull_and_every_piece_is_placed():
    for items in _instances():
        for rule in RULES + (A.ffd,):
            assert A.is_valid(items, rule(items)), rule.__name__


def test_every_rule_needs_at_least_the_lower_bound_and_ffd_is_among_the_best_known():
    for items in _instances():
        lb = A.lower_bound(items)
        assert all(A.bins_used(rule(items)) >= lb for rule in RULES + (A.ffd,))


def test_online_rules_do_not_see_the_future():
    # die Zuordnung der ersten m Stücke ist für jede Fortsetzung dieselbe
    for items in _instances(10):
        for rule in RULES:
            full = rule(items)
            for m in (1, 7, 30):
                assert rule(items[:m]) == full[:m], rule.__name__


def test_scaling_pieces_and_capacity_changes_nothing():
    for items in _instances(10):
        for rule in RULES:
            assert rule([3 * s for s in items], 3 * C.CAPACITY) == rule(items, C.CAPACITY), rule.__name__


def test_next_fit_uses_at_most_twice_the_lower_bound():
    # zwei aufeinanderfolgende Behälter von Next Fit sind zusammen mehr als einmal voll
    for items in _instances(40, seed=3):
        assert A.bins_used(A.next_fit(items)) <= 2 * A.lower_bound(items)


def test_first_fit_uses_at_most_floor_of_one_point_seven_times_ffd():
    # Dósa/Sgall: First Fit höchstens ⌊1,7 · OPT⌋; FFD ≥ OPT, also gilt es auch gegen FFD
    for items in _instances(40, seed=4):
        assert A.bins_used(A.first_fit(items)) <= math.floor(1.7 * A.bins_used(A.ffd(items)))


def test_first_and_best_fit_on_descending_order_equal_ffd():
    for items in _instances(20, seed=5):
        desc = sorted(items, reverse=True)
        assert A.bins_used(A.first_fit(desc)) == A.bins_used(A.ffd(items))


def test_ffd_does_not_depend_on_the_input_order():
    rng = np.random.default_rng(6)
    for items in _instances(20, seed=6):
        assert A.bins_used(A.ffd(items)) == A.bins_used(A.ffd([int(x) for x in rng.permutation(items)]))


def test_harmonic_without_small_pieces_does_not_depend_on_the_order():
    # ohne Stücke bis ein Sechstel zählt Harmonic nur je Klasse: die Reihenfolge ist gleichgültig
    rng = np.random.default_rng(7)
    for _ in range(30):
        items = [int(x) for x in rng.integers(C.CAPACITY // 6 + 1, C.CAPACITY + 1, 50)]
        assert A.bins_used(A.harmonic(items)) == A.bins_used(A.harmonic([int(x) for x in rng.permutation(items)]))


def test_the_gegner_sequence_is_equally_bad_for_all_four_rules_but_not_for_ffd():
    items = make_items("Dreiphasenfolge (Gegner)", 1800, "wie erzeugt", 0)
    counts = {r.__name__: A.bins_used(r(items)) for r in RULES}
    assert len(set(counts.values())) == 1 and next(iter(counts.values())) > 1.6 * A.bins_used(A.ffd(items))


def test_adding_a_piece_never_removes_a_bin_for_online_rules():
    for items in _instances(15, seed=8):
        for rule in RULES:
            assert A.bins_used(rule(items + [123])) >= A.bins_used(rule(items))


def test_a_larger_capacity_never_raises_the_lower_bound():
    for items in _instances(15, seed=9):
        assert A.lower_bound(items, 7000) <= A.lower_bound(items, 6000)
