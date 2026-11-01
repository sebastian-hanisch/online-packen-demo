"""Orakel-Test online-packen-demo / online_packen: unabhängige Rechenwege gegen den Kern.

Orakel 1: das Optimum exakt (CP-SAT, OR-Tools) gegen die Aufzählung aller Zuordnungen; damit ist das Orakel selbst geprüft.
Orakel 2: das bekannte Optimum der Gegnerfolgen und die Untergrenze gegen CP-SAT; FFD ist nie besser als das Optimum.
Orakel 3: First Fit, Best Fit und Harmonic gegen zweite, plumpere Fassungen (Listen und explizite Behälter statt Zähler und Arrays)."""

import itertools
import math

import numpy as np
import pytest

import onp_algorithm as A
import onp_constants as C
from onp_scenario import known_optimum, make_items

CP = pytest.importorskip("ortools.sat.python.cp_model")


def opt_exact(items, cap=C.CAPACITY):
    n = len(items)
    ub = A.bins_used(A.ffd(items, cap))
    if math.ceil(sum(items) / cap) == ub:
        return ub
    m = CP.CpModel()
    x = {(i, b): m.NewBoolVar(f"x{i}_{b}") for i in range(n) for b in range(ub)}
    y = [m.NewBoolVar(f"y{b}") for b in range(ub)]
    for i in range(n):
        m.Add(sum(x[i, b] for b in range(ub)) == 1)
    for b in range(ub):
        m.Add(sum(items[i] * x[i, b] for i in range(n)) <= cap * y[b])
    m.Minimize(sum(y))
    s = CP.CpSolver()
    s.parameters.max_time_in_seconds = 30
    s.parameters.num_workers = 1
    s.parameters.random_seed = 1
    assert s.Solve(m) == CP.OPTIMAL
    return int(round(s.ObjectiveValue()))


def brute_opt(items, cap):
    n = len(items)
    best = n
    for assign in itertools.product(range(n), repeat=n):
        if max(assign) >= best:
            continue
        loads: dict = {}
        ok = True
        for it, b in zip(items, assign):
            loads[b] = loads.get(b, 0) + it
            if loads[b] > cap:
                ok = False
                break
        if ok:
            best = min(best, len(loads))
    return best


def test_cp_sat_equals_enumeration_on_small_instances():
    rng = np.random.default_rng(0)
    for _ in range(40):
        items = [int(x) for x in rng.integers(2, 14, int(rng.integers(3, 8)))]
        assert opt_exact(items, 20) == brute_opt(items, 20), items


def test_known_optimum_of_the_gegner_sequences_equals_cp_sat():
    for n in (6, 12, 18):
        items = make_items("Dreiphasenfolge (Gegner)", n, "wie erzeugt", 0)
        assert opt_exact(items) == known_optimum("Dreiphasenfolge (Gegner)", n), n
    for n in (4, 6, 8, 10, 14):
        items = make_items("abwechselnd halb und winzig (Gegner)", n, "wie erzeugt", 0)
        assert opt_exact(items) == known_optimum("abwechselnd halb und winzig (Gegner)", n), n
    for n in (4, 8, 12):
        items = make_items("von Hand (4 Stücke, wiederholt)", n, "wie erzeugt", 0)
        assert opt_exact(items) == known_optimum("von Hand (4 Stücke, wiederholt)", n), n


def test_ffd_is_never_better_than_the_optimum_and_the_lower_bound_never_above():
    rng = np.random.default_rng(1)
    for _ in range(40):
        items = [int(x) for x in rng.integers(300, 4200, int(rng.integers(6, 16)))]
        opt = opt_exact(items)
        assert A.lower_bound(items) <= opt <= A.bins_used(A.ffd(items))


def first_fit_lists(items, cap):
    bins = []
    for s in items:
        for b in bins:
            if sum(b) + s <= cap:
                b.append(s)
                break
        else:
            bins.append([s])
    return len(bins)


def best_fit_lists(items, cap):
    bins = []
    for s in items:
        cand = [b for b in bins if sum(b) + s <= cap]
        if cand:
            min(cand, key=lambda b: cap - sum(b) - s).append(s)
        else:
            bins.append([s])
    return len(bins)


def harmonic_lists(items, cap, m=C.HARMONIC_M):
    classes: dict = {}
    small = []
    for s in items:
        if s * m <= cap:
            small.append(s)
        else:
            classes.setdefault(cap // s, []).append(s)
    n = sum(math.ceil(len(v) / j) for j, v in classes.items())
    bins, load = 0, cap + 1
    for s in small:
        if load + s > cap:
            bins, load = bins + 1, 0
        load += s
    return n + bins


def test_first_best_fit_and_harmonic_equal_their_second_versions():
    rng = np.random.default_rng(2)
    for _ in range(60):
        items = [int(x) for x in rng.integers(1, 6001, int(rng.integers(1, 80)))]
        assert A.bins_used(A.first_fit(items)) == first_fit_lists(items, 6000), items
        assert A.bins_used(A.best_fit(items)) == best_fit_lists(items, 6000), items
        assert A.bins_used(A.harmonic(items)) == harmonic_lists(items, 6000), items
