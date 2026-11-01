"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Verzweigung steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text). Die Tests geben ihr Analyse-Objekte oder Zeilen mit gesetzten Werten und prüfen die Art und jede genannte Zahl."""

import onp_evaluation as ev


def _analysis(regel="First Fit", q=1.665, bins=333, ref=200, label="Optimum"):
    s = ev.Settings(regel=regel)
    ratios = {r: q for r in ("Next Fit", "First Fit", "Best Fit", "Harmonic")}
    return ev.Analysis(s, 600, {r: bins for r in ratios}, ref, label, 200, 200, ratios, [], [])


def test_kern_names_bins_reference_ratio_guarantee_and_share():
    kind, text = ev.verdict_kern(_analysis())
    assert kind == "warning"
    assert "**First Fit** braucht 333 Behälter, das Optimum 200: das **1.665-Fache**." in text
    assert "Die Garantie (asymptotisch) ist 1.7." in text and "Die Folge nutzt davon 98 %." in text


def test_kern_thresholds_are_one_point_one_and_one_point_five():
    assert ev.verdict_kern(_analysis(q=1.099))[0] == "success"
    assert ev.verdict_kern(_analysis(q=1.1))[0] == "info"
    assert ev.verdict_kern(_analysis(q=1.499))[0] == "info"
    assert ev.verdict_kern(_analysis(q=1.5))[0] == "warning"


def test_kern_next_fit_and_harmonic_wording():
    _, text = ev.verdict_kern(_analysis(regel="Next Fit", q=1.5, bins=300, ref=200))
    assert text.startswith("**Next Fit** braucht 300") and "Die Garantie (asymptotisch) ist 2." in text and "nutzt davon 75 %." in text
    _, text = ev.verdict_kern(_analysis(regel="Harmonic", q=1.7, label="FFD"))
    assert "das FFD 200" in text and "für 6 Klassen aus einer eigenen Herleitung) ist 1.70." in text and "nutzt davon 100 %." in text


def test_guarantee_values():
    assert ev.guarantee("Next Fit") == 2.0 and ev.guarantee("First Fit") == 1.7 and ev.guarantee("Best Fit") == 1.7
    assert abs(ev.guarantee("Harmonic") - 1.7) < 1e-12


def _nf_rows(last_others=(1.0, 1.0, 1.0)):
    row = lambda n, nf: {"Stücke": n, "Next Fit": nf, "First Fit": last_others[0], "Best Fit": last_others[1], "Harmonic": last_others[2]}
    return [row(20, 1.667), row(200, 1.961), row(2000, 1.996)]


def test_nf_names_first_and_last_row_and_the_others():
    kind, text = ev.verdict_nf(_nf_rows())
    assert kind == "warning"
    assert "bei 20 Stücken beim 1.667-Fachen des Optimums, bei 2000 beim **1.996-Fachen**" in text and "alle bei 1.000." in text
    assert "liegen bei 1.000, 1.100 und 1.000." in ev.verdict_nf(_nf_rows((1.0, 1.1, 1.0)))[1]


def _phase_rows(values=(1.0, 1.333, 1.667), same=True):
    rows = []
    for name, v, opt, b in (("nach Gruppe 1", values[0], 100, 100), ("nach Gruppe 2", values[1], 300, 400), ("nach Gruppe 3", values[2], 600, 1000)):
        row = {"Präfix": name, "Optimum": opt, "FFD Behälter": opt}
        for r in ("Next Fit", "First Fit", "Best Fit", "Harmonic"):
            row[r] = v
            row[f"{r} Behälter"] = b
        rows.append(row)
    if not same:
        rows[-1]["Best Fit"] = 1.4
        rows[-1]["Best Fit Behälter"] = 840
    return rows


def test_phasen_all_equal_and_different_wording():
    kind, text = ev.verdict_phasen(_phase_rows())
    assert kind == "warning" and "Alle vier Regeln erreichen auf dem längsten Präfix das **1.667-Fache**" in text and "nach der zweiten Gruppe das 1.333-Fache" in text
    assert "Optimum 600, FFD (offline) 600, Next Fit 1000, First Fit 1000, Best Fit 1000, Harmonic 1000." in text
    _, text = ev.verdict_phasen(_phase_rows(same=False))
    assert "Auf dem längsten Präfix: Next Fit 1.667, First Fit 1.667, Best Fit 1.400, Harmonic 1.667." in text and "Best Fit 840," in text


def _order_rows(harm=(1.667, 1.667, 1.667, 1.667)):
    return [{"Reihenfolge": o, "Next Fit": 1.5, "First Fit": ff, "Best Fit": ff, "Harmonic": h}
            for o, ff, h in zip(("wie erzeugt", "zufällig gemischt", "aufsteigend", "absteigend"), (1.667, 1.017, 1.667, 1.0), harm)]


def test_reihenfolge_names_first_fit_in_three_orders_and_harmonic():
    kind, text = ev.verdict_reihenfolge(_order_rows())
    assert kind == "info"
    assert "gegnerischer Reihenfolge das **1.667-Fache**, zufällig gemischt 1.017, absteigend 1.000 (das ist First Fit Decreasing)." in text
    assert "Harmonic ist reihenfolgeblind: in jeder Reihenfolge 1.667." in text
    assert "Harmonic schwankt nur wenig: 1.600 bis 1.700." in ev.verdict_reihenfolge(_order_rows((1.6, 1.7, 1.65, 1.65)))[1]


def _typical(ff=(1.01, 1.043), bf=(1.01, 1.026), nf=(1.033, 1.372), harm=(1.2, 1.414)):
    return [{"Folge": "A", "Next Fit": nf[0], "First Fit": ff[0], "Best Fit": bf[0], "Harmonic": harm[0]}, {"Folge": "drei Größen", "Next Fit": nf[1], "First Fit": ff[1], "Best Fit": bf[1], "Harmonic": harm[1]}]


def test_typisch_names_maxima_ranges_and_the_worst_harmonic_folge():
    kind, text = ev.verdict_typisch(_typical())
    assert kind == "info"
    assert "auf allen 2 Verteilungen höchstens beim 1.043-Fachen von FFD, Best Fit beim 1.026-Fachen (Garantie je 1,7)" in text
    assert "Next Fit zwischen 1.033 und 1.372 (Garantie 2)" in text and "bei „drei Größen“ beim **1.414-Fachen**" in text


def test_laenge_names_first_and_last_row():
    rows = [{"n": 50, "Next Fit": 1.233, "First Fit": 1.044, "Best Fit": 1.037}, {"n": 4000, "Next Fit": 1.317, "First Fit": 1.028, "Best Fit": 1.017}]
    kind, text = ev.verdict_laenge(rows)
    assert kind == "info"
    assert "Von n = 50 auf n = 4000 Stücke sinkt der Quotient von First Fit von 1.044 auf 1.028, von Best Fit von 1.037 auf 1.017" in text
    assert "Next Fit bleibt bei 1.317 (vorher 1.233)." in text


def test_delta_text_is_mine_minus_reference_with_inverse_colour():
    assert ev.delta_text(1.62, 1.7, "Garantie") == ("-0.08 gegen Garantie", "inverse")
    assert ev.delta_text(1.8, 1.7, "Garantie") == ("+0.10 gegen Garantie", "inverse")
    assert ev.delta_text(1.7, 1.7004, "Garantie") == ("gleich wie Garantie", "off")
