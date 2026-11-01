"""Folgen von Stücken: Größen sind ganze Zahlen von 1 bis CAPACITY. Jede Folge hängt nur von (Art, n, Ordnung, Seed) ab."""

import numpy as np

import onp_constants as C

CAP = C.CAPACITY


def base_items(folge: str, n: int, rng) -> list[int]:
    """Die Stücke in ihrer natürlichen Entstehungsreihenfolge (bei den Gegnerfolgen die gegnerische)."""
    if folge == "gleich (0, 1]":
        return [int(x) for x in rng.integers(1, CAP + 1, n)]
    if folge == "gleich (0, 0,5]":
        return [int(x) for x in rng.integers(1, CAP // 2 + 1, n)]
    if folge == "gleich (0,2, 0,8]":
        return [int(x) for x in rng.integers(CAP // 5, 4 * CAP // 5 + 1, n)]
    if folge == "gleich (1/6, 1/2]":
        return [int(x) for x in rng.integers(CAP // 6, CAP // 2 + 1, n)]
    if folge == "gleich (0, 0,1]":
        return [int(x) for x in rng.integers(1, CAP // 10 + 1, n)]
    if folge == "Lognormal (Paletten)":
        raw = np.round(CAP * rng.lognormal(np.log(C.LOGNORMAL_MEDIAN), C.LOGNORMAL_SIGMA, n)).astype(int)
        return [int(x) for x in np.clip(raw, 1, CAP)]
    if folge == "drei Größen":
        return [int(x) for x in rng.choice(C.THREE_SIZES, n)]
    if folge == "Dreiphasenfolge (Gegner)":
        k = n // 3
        return [C.PHASE_SIZES[0]] * k + [C.PHASE_SIZES[1]] * k + [C.PHASE_SIZES[2]] * k
    if folge == "abwechselnd halb und winzig (Gegner)":
        return [C.HALF, C.TINY] * (n // 2)
    if folge == "von Hand (4 Stücke, wiederholt)":
        return list(C.HAND_ITEMS) * (n // 4)
    raise ValueError(f"unbekannte Folge: {folge}")


def make_items(folge: str, n: int, ordnung: str, seed: int) -> list[int]:
    rng = np.random.default_rng([seed, n, C.FOLGEN.index(folge)])
    items = base_items(folge, n, rng)
    if ordnung == "wie erzeugt":
        return items
    if ordnung == "zufällig gemischt":
        return [int(x) for x in np.random.default_rng([seed, n, 99]).permutation(items)]
    if ordnung == "aufsteigend":
        return sorted(items)
    if ordnung == "absteigend":
        return sorted(items, reverse=True)
    raise ValueError(f"unbekannte Ordnung: {ordnung}")


def known_optimum(folge: str, n: int) -> int | None:
    """Optimum der Gegnerfolgen (von Hand): unabhängig von der Reihenfolge, weil es nur von den Stücken abhängt; sonst None."""
    if folge == "Dreiphasenfolge (Gegner)":
        return n // 3                                  # je ein Stück jeder Gruppe füllt einen Behälter genau (998 + 2001 + 3001 = 6000)
    if folge == "abwechselnd halb und winzig (Gegner)":
        h = n // 2                                     # h halbe Stücke zu zweit, die h winzigen (Summe h < 3000) passen in den freien Platz oder in einen weiteren
        return h // 2 + 1 if h % 2 == 0 else (h + 1) // 2
    if folge == "von Hand (4 Stücke, wiederholt)":
        return 2 * (n // 4)                            # 3600 + 2400 und 3000 + 3000 füllen je einen Behälter genau
    return None
