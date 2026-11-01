"""Kennzahlen, Verdikt-Logik und Experimente. Verdikte sind reine Funktionen (Art, Text); tests/test_verdicts.py prüft jede Zahl darin."""

import math
from dataclasses import dataclass

import numpy as np

import onp_algorithm as A
import onp_constants as C
from onp_scenario import base_items, known_optimum, make_items

OK_QUOTIENT, WARN_QUOTIENT = 1.1, 1.5            # Verdikt: grün unter 1,1, gelb bis 1,5, sonst Warnung
CAP = C.CAPACITY


@dataclass(frozen=True)
class Settings:
    regel: str = C.DEFAULT_REGEL
    folge: str = C.DEFAULT_FOLGE
    ordnung: str = C.DEFAULT_ORDNUNG
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    count: int                    # Zahl der Stücke
    bins: dict                    # Regel -> Zahl der Behälter
    ref: int                      # Referenz: bekanntes Optimum oder FFD
    ref_label: str
    ffd: int
    lower: int                    # Untergrenze ceil(Summe / C)
    ratios: dict                  # Regel -> Behälter / Referenz
    fills: list                   # Füllgrad (%) der Behälter der hervorgehobenen Regel
    trace: list                   # Zeilen der Ablauftabelle


def ratio(bins: float, ref: float) -> float:
    """Quotient der Behälterzahlen; ohne Referenzbehälter (leere Folge) ist 1 der neutrale Wert."""
    return 1.0 if ref <= 0 else bins / ref


def guarantee(regel: str) -> float:
    return A.harmonic_guarantee() if regel == "Harmonic" else C.GUARANTEES[regel]


def analyse(s: Settings) -> Analysis:
    items = make_items(s.folge, s.n, s.ordnung, s.seed)
    assigns = {r: f(items) for r, f in A.RULES.items()}
    bins = {r: A.bins_used(a) for r, a in assigns.items()}
    ffd_bins = A.bins_used(A.ffd(items))
    opt = known_optimum(s.folge, s.n)
    ref, label = (opt, "Optimum") if opt is not None else (ffd_bins, "FFD")
    fills = [100.0 * x / CAP for x in A.bin_loads(items, assigns[s.regel])]
    return Analysis(s, len(items), bins, ref, label, ffd_bins, A.lower_bound(items), {r: ratio(b, ref) for r, b in bins.items()}, fills, trace_rows(items, assigns))


def trace_rows(items, assigns, limit: int = C.TRACE_LEN) -> list[dict]:
    """Die ersten Stücke: Größe und Behälter (ab 1 gezählt) je Regel."""
    return [{"Stück": i + 1, "Größe": items[i], **{r: assigns[r][i] + 1 for r in C.REGELN}} for i in range(min(limit, len(items)))]


# ---------------------------------------------------------------------------------------------------------------------------------
# Experimente mit festen Folgen und Seeds


def _bins_all(items) -> dict:
    return {r: A.bins_used(f(items)) for r, f in A.RULES.items()}


def nf_adversary_rows(ns=C.NF_ADVERSARY_NS) -> list[dict]:
    """Abwechselnd halbes und winziges Stück: Next Fit verbraucht fast das Doppelte, die anderen Regeln das Optimum."""
    rows = []
    for n in ns:
        items = base_items("abwechselnd halb und winzig (Gegner)", n, None)
        opt = known_optimum("abwechselnd halb und winzig (Gegner)", n)
        b = _bins_all(items)
        rows.append({"Stücke": n, "Optimum": opt, **{r: ratio(b[r], opt) for r in C.REGELN}, "Next Fit Behälter": b["Next Fit"]})
    return rows


def phase_rows(group: int = C.PHASES_N) -> list[dict]:
    """Dreiphasenfolge: Präfixe nach Gruppe 1, 2, 3 mit dem Optimum von Hand (nur für durch 6 teilbare Gruppen)."""
    assert group % 6 == 0
    items = base_items("Dreiphasenfolge (Gegner)", 3 * group, None)
    opts = {"nach Gruppe 1": math.ceil(group * C.PHASE_SIZES[0] / CAP), "nach Gruppe 2": group // 2, "nach Gruppe 3": group}
    rows = []
    for name, m in (("nach Gruppe 1", group), ("nach Gruppe 2", 2 * group), ("nach Gruppe 3", 3 * group)):
        prefix = items[:m]
        b = _bins_all(prefix)
        rows.append({"Präfix": name, "Optimum": opts[name], **{r: ratio(b[r], opts[name]) for r in C.REGELN}, **{f"{r} Behälter": b[r] for r in C.REGELN}, "FFD Behälter": A.bins_used(A.ffd(prefix))})
    return rows


def order_rows(group: int = C.ORDER_NS[-1], seed: int = C.DEFAULT_SEED) -> list[dict]:
    """Dieselben 3·group Stücke der Dreiphasenfolge in vier Reihenfolgen; Quotient zum Optimum group."""
    rows = []
    for ordnung in C.ORDNUNGEN:
        items = make_items("Dreiphasenfolge (Gegner)", 3 * group, ordnung, seed)
        b = _bins_all(items)
        rows.append({"Reihenfolge": ordnung, **{r: ratio(b[r], group) for r in C.REGELN}})
    return rows


def typical_rows(n: int = C.SWEEP_N, seeds=C.SWEEP_SEEDS) -> list[dict]:
    """Mittel über feste Seeds: Quotient jeder Regel zu FFD für die sieben Zufallsverteilungen, dazu FFD/Summenschranke."""
    rows = []
    for folge in C.TYPICAL_FOLGEN:
        acc = {r: [] for r in C.REGELN}
        gap = []
        for sd in seeds:
            items = make_items(folge, n, "wie erzeugt", sd)
            ref = A.bins_used(A.ffd(items))
            gap.append(ratio(ref, A.lower_bound(items)))
            b = _bins_all(items)
            for r in C.REGELN:
                acc[r].append(ratio(b[r], ref))
        rows.append({"Folge": folge, "FFD / Summe": float(np.mean(gap)), **{r: float(np.mean(v)) for r, v in acc.items()}})
    return rows


def growth_rows(ns=C.GROWTH_NS, seeds=C.GROWTH_SEEDS, folge: str = "gleich (0, 1]") -> list[dict]:
    """Wächst n, nähern sich First Fit und Best Fit dem Optimum; Next Fit nicht."""
    rows = []
    for n in ns:
        acc = {r: [] for r in ("Next Fit", "First Fit", "Best Fit")}
        for sd in seeds:
            items = make_items(folge, n, "wie erzeugt", sd)
            ref = A.bins_used(A.ffd(items))
            for r in acc:
                acc[r].append(ratio(A.bins_used(A.RULES[r](items)), ref))
        rows.append({"n": n, **{r: float(np.mean(v)) for r, v in acc.items()}})
    return rows


# ---------------------------------------------------------------------------------------------------------------------------------
# Verdikte (rein: Art, Text)


def delta_text(value: float, reference: float, label: str) -> tuple[str, str]:
    """Text und Farbregel des Deltas: „mein Wert minus Referenz“. Ein auf zwei Stellen gleicher Wert bekommt keinen Pfeil und keine Farbe."""
    d = value - reference
    if abs(d) < 0.005:
        return f"gleich wie {label}", "off"
    return f"{d:+.2f} gegen {label}", "inverse"


def guarantee_phrase(regel: str, g: float) -> str:
    if regel == "Harmonic":
        return f"Die Garantie (asymptotisch, für 6 Klassen aus einer eigenen Herleitung) ist {g:.2f}."
    return f"Die Garantie (asymptotisch) ist {g:g}."


def verdict_kern(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Was kostet die Regel gegenüber der Referenz auf dieser Folge?"""
    s = a.settings
    q = a.ratios[s.regel]
    g = guarantee(s.regel)
    text = (f"**{s.regel}** braucht {a.bins[s.regel]} Behälter, das {a.ref_label} {a.ref}: das **{q:.3f}-Fache**. {guarantee_phrase(s.regel, g)} "
            f"Die Folge nutzt davon {q / g * 100:.0f} %.")
    kind = "success" if q < OK_QUOTIENT else "info" if q < WARN_QUOTIENT else "warning"
    return kind, text


def verdict_nf(rows: list[dict]) -> tuple[str, str]:
    """Experiment 1a: Next Fit gegen die abwechselnde Folge."""
    first, last = rows[0], rows[-1]
    others = ("First Fit", "Best Fit", "Harmonic")
    if len({last[r] for r in others}) == 1:
        rest = f"First Fit, Best Fit und Harmonic liegen alle bei {last['First Fit']:.3f}."
    else:
        rest = f"First Fit, Best Fit und Harmonic liegen bei {last['First Fit']:.3f}, {last['Best Fit']:.3f} und {last['Harmonic']:.3f}."
    return "warning", (f"Next Fit liegt bei {first['Stücke']} Stücken beim {first['Next Fit']:.3f}-Fachen des Optimums, bei {last['Stücke']} beim **{last['Next Fit']:.3f}-Fachen**: "
                       f"es nähert sich dem Doppelten. {rest}")


def verdict_phasen(rows: list[dict]) -> tuple[str, str]:
    """Experiment 1b: Dreiphasenfolge, Präfixe."""
    last = rows[-1]
    worst = {r: max(x[r] for x in rows) for r in C.REGELN}
    gleich = len({round(v, 6) for v in worst.values()}) == 1
    kopf = (f"Alle vier Regeln erreichen auf dem längsten Präfix das **{last['First Fit']:.3f}-Fache** des Optimums, nach der zweiten Gruppe das {rows[1]['First Fit']:.3f}-Fache. "
            if gleich else f"Auf dem längsten Präfix: Next Fit {last['Next Fit']:.3f}, First Fit {last['First Fit']:.3f}, Best Fit {last['Best Fit']:.3f}, Harmonic {last['Harmonic']:.3f}. ")
    return "warning", kopf + (f"Behälter nach der dritten Gruppe: Optimum {last['Optimum']}, FFD (offline) {last['FFD Behälter']}, Next Fit {last['Next Fit Behälter']}, First Fit {last['First Fit Behälter']}, "
                              f"Best Fit {last['Best Fit Behälter']}, Harmonic {last['Harmonic Behälter']}.")


def verdict_reihenfolge(rows: list[dict]) -> tuple[str, str]:
    """Experiment 2: dieselben Stücke in vier Reihenfolgen."""
    by = {r["Reihenfolge"]: r for r in rows}
    ff = {k: v["First Fit"] for k, v in by.items()}
    harm = [v["Harmonic"] for v in by.values()]
    if max(harm) - min(harm) < 0.005:
        harm_text = f"Harmonic ist reihenfolgeblind: in jeder Reihenfolge {max(harm):.3f}."
    else:
        harm_text = f"Harmonic schwankt nur wenig: {min(harm):.3f} bis {max(harm):.3f}."
    return "info", (f"Dieselben Stücke: First Fit zahlt in gegnerischer Reihenfolge das **{ff['wie erzeugt']:.3f}-Fache**, zufällig gemischt {ff['zufällig gemischt']:.3f}, "
                    f"absteigend {ff['absteigend']:.3f} (das ist First Fit Decreasing). {harm_text}")


def verdict_typisch(rows: list[dict]) -> tuple[str, str]:
    """Experiment 3: Zufallsverteilungen."""
    ff_max = max(r["First Fit"] for r in rows)
    bf_max = max(r["Best Fit"] for r in rows)
    nf = [r["Next Fit"] for r in rows]
    harm_worst = max(rows, key=lambda r: r["Harmonic"])
    return "info", (f"First Fit liegt auf allen {len(rows)} Verteilungen höchstens beim {ff_max:.3f}-Fachen von FFD, Best Fit beim {bf_max:.3f}-Fachen (Garantie je 1,7). "
                    f"Next Fit zwischen {min(nf):.3f} und {max(nf):.3f} (Garantie 2). Harmonic hat dieselbe Garantie wie First Fit und liegt bei „{harm_worst['Folge']}“ beim **{harm_worst['Harmonic']:.3f}-Fachen**.")


def verdict_laenge(rows: list[dict]) -> tuple[str, str]:
    """Experiment 4: wachsende Länge."""
    a, b = rows[0], rows[-1]
    return "info", (f"Von n = {a['n']} auf n = {b['n']} Stücke sinkt der Quotient von First Fit von {a['First Fit']:.3f} auf {b['First Fit']:.3f}, von Best Fit von {a['Best Fit']:.3f} auf {b['Best Fit']:.3f}; "
                    f"Next Fit bleibt bei {b['Next Fit']:.3f} (vorher {a['Next Fit']:.3f}).")
