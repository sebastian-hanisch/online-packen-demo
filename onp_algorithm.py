"""Kern: eindimensionales Packen. Jede Online-Regel liefert für jedes Stück die Nummer des Behälters (0, 1, 2, ...), in den es sofort und endgültig gelegt wird.

Next Fit, First Fit, Best Fit und Harmonic kennen nur die bisherigen Stücke; First Fit Decreasing (offline) sortiert vorher und dient als Referenz."""

import math
from fractions import Fraction

import numpy as np

import onp_constants as C


def next_fit(items, cap=C.CAPACITY):
    assign, b, load = [], -1, cap + 1
    for s in items:
        if load + s > cap:
            b += 1
            load = 0
        load += s
        assign.append(b)
    return assign


def first_fit(items, cap=C.CAPACITY):
    load = np.zeros(len(items) + 1, dtype=np.int64)
    nb, assign = 0, []
    for s in items:
        fits = load[:nb] <= cap - s
        i = int(np.argmax(fits)) if nb and fits.any() else nb
        if i == nb:
            nb += 1
        load[i] += s
        assign.append(i)
    return assign


def best_fit(items, cap=C.CAPACITY):
    load = np.zeros(len(items) + 1, dtype=np.int64)
    nb, assign = 0, []
    for s in items:
        rest = cap - load[:nb] - s
        cand = np.flatnonzero(rest >= 0)
        i = int(cand[np.argmin(rest[cand])]) if cand.size else nb
        if i == nb:
            nb += 1
        load[i] += s
        assign.append(i)
    return assign


def harmonic(items, cap=C.CAPACITY, m=C.HARMONIC_M):
    """Harmonic_m: Klasse j = cap // s (1 .. m − 1) für Stücke mit s > cap/m, genau j Stücke je Behälter; kleinere Stücke per Next Fit in eigenen Behältern."""
    assign, nb = [], 0
    count: dict = {}               # Klasse -> Zahl der Stücke
    open_bin: dict = {}            # Klasse -> offener Behälter
    small_bin, small_load = -1, cap + 1
    for s in items:
        if s * m <= cap:
            if small_load + s > cap:
                small_bin, small_load, nb = nb, 0, nb + 1
            small_load += s
            assign.append(small_bin)
            continue
        j = cap // s
        if count.get(j, 0) % j == 0:
            open_bin[j] = nb
            nb += 1
        count[j] = count.get(j, 0) + 1
        assign.append(open_bin[j])
    return assign


def ffd(items, cap=C.CAPACITY):
    """First Fit Decreasing (offline): Stücke absteigend sortieren, dann First Fit; Rückgabe in der ursprünglichen Reihenfolge der Stücke."""
    order = sorted(range(len(items)), key=lambda i: -items[i])
    sub = first_fit([items[i] for i in order], cap)
    assign = [0] * len(items)
    for pos, i in enumerate(order):
        assign[i] = sub[pos]
    return assign


RULES = {"Next Fit": next_fit, "First Fit": first_fit, "Best Fit": best_fit, "Harmonic": harmonic}


def bins_used(assign) -> int:
    return (max(assign) + 1) if assign else 0


def bin_loads(items, assign) -> list[int]:
    return [int(x) for x in np.bincount(assign, weights=items, minlength=bins_used(assign))] if assign else []


def lower_bound(items, cap=C.CAPACITY) -> int:
    return math.ceil(sum(items) / cap)


def is_valid(items, assign, cap=C.CAPACITY) -> bool:
    """Unabhängiger Prüfer: jedes Stück hat einen Behälter, kein Behälter ist überfüllt."""
    if len(items) != len(assign) or any(a < 0 for a in assign):
        return False
    loads: dict = {}
    for s, a in zip(items, assign):
        loads[a] = loads.get(a, 0) + s
    return all(v <= cap for v in loads.values())


def harmonic_guarantee(m: int = C.HARMONIC_M) -> float:
    """Garantie von Harmonic_m als größtes Gewicht, das in einen Behälter des Optimums passt (eigene Herleitung im Stil von Lee/Lee).

    Gewicht 1/j für ein Stück der Klasse j (Größe knapp über 1/(j+1)), m/(m − 1) mal die Größe für ein kleines Stück. Aufzählung in Brüchen."""
    best = Fraction(0)

    def rec(j, used, weight):
        nonlocal best
        if j == m:
            best = max(best, weight + Fraction(m, m - 1) * (1 - used))
            return
        n = 0
        while n <= j + 1:
            u = used + Fraction(n, j + 1)
            if u >= 1 and n > 0:
                break
            rec(j + 1, u, weight + Fraction(n, j))
            n += 1

    rec(1, Fraction(0), Fraction(0))
    return float(best)
