"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

CAPACITY = 6000                                  # Fassungsvermögen eines Behälters (ganzzahlig, damit die Gegnerfolgen exakt aufgehen)
N_MIN, N_MAX, DEFAULT_N = 4, 5000, 1800
N_OPTIONS = (4, 12, 24, 60, 120, 300, 600, 1200, 1800, 2400, 5000)
SEED_MAX, DEFAULT_SEED = 999999, 7

REGELN = ("Next Fit", "First Fit", "Best Fit", "Harmonic")
DEFAULT_REGEL = "First Fit"
REGEL_HILFE = {
    "Next Fit": "Legt das Stück in den zuletzt geöffneten Behälter, passt es nicht, wird ein neuer geöffnet. Frühere Behälter bleiben unbeachtet.",
    "First Fit": "Legt das Stück in den ersten Behälter (nach Öffnungsreihenfolge), in den es passt.",
    "Best Fit": "Legt das Stück in den Behälter, in den es passt und der danach am vollsten ist.",
    "Harmonic": "Sortiert die Stücke nach Größenklassen (Klasse j: Größe zwischen 1/(j+1) und 1/j, bis j = 5; kleiner als 1/6 ist die letzte Klasse) und packt jede Klasse für sich: j Stücke der Klasse j je Behälter.",
}
HARMONIC_M = 6                                   # Zahl der Klassen von Harmonic

FOLGEN = (
    "gleich (0, 1]", "gleich (0, 0,5]", "gleich (0,2, 0,8]", "gleich (1/6, 1/2]", "gleich (0, 0,1]", "Lognormal (Paletten)", "drei Größen",
    "Dreiphasenfolge (Gegner)", "abwechselnd halb und winzig (Gegner)", "von Hand (4 Stücke, wiederholt)",
)
DEFAULT_FOLGE = "Dreiphasenfolge (Gegner)"
FOLGEN_HILFE = {
    "gleich (0, 1]": "Jede Größe von 1 bis zur vollen Behälterfüllung ist gleich wahrscheinlich.",
    "gleich (0, 0,5]": "Gleichverteilt bis zur halben Behälterfüllung: Stücke passen oft zu mehreren.",
    "gleich (0,2, 0,8]": "Gleichverteilt zwischen einem Fünftel und vier Fünfteln: viele Stücke passen nur zu zweit.",
    "gleich (1/6, 1/2]": "Gleichverteilt zwischen einem Sechstel und der Hälfte: zwei bis fünf Stücke je Behälter.",
    "gleich (0, 0,1]": "Gleichverteilt bis zu einem Zehntel: viele kleine Stücke, der Behälter wird fast voll.",
    "Lognormal (Paletten)": "Lognormal um ein Viertel der Behälterfüllung (Streuung 0,5): wenige große, viele mittlere Stücke.",
    "drei Größen": "Nur drei Größen (0,52, 0,34 und 0,17 der Behälterfüllung), gleich wahrscheinlich; 0,52 passt nie zu zweit.",
    "Dreiphasenfolge (Gegner)": "Erst n/3 Stücke von etwa einem Sechstel, dann n/3 von einem Drittel, dann n/3 von der Hälfte (je ein Stück jeder Gruppe füllt einen Behälter ganz).",
    "abwechselnd halb und winzig (Gegner)": "Ein halber Behälter, ein winziges Stück, immer im Wechsel: die Folge, die Next Fit verdoppelt.",
    "von Hand (4 Stücke, wiederholt)": "Die Stücke 3600, 3000, 2400, 3000 der Reihe nach, bei n = 4 genau die Handrechnung.",
}
ORDNUNGEN = ("wie erzeugt", "zufällig gemischt", "aufsteigend", "absteigend")
DEFAULT_ORDNUNG = "wie erzeugt"
ORDNUNG_HILFE = {
    "wie erzeugt": "Die Folge so, wie sie entsteht (bei den Gegnerfolgen die gegnerische Reihenfolge).",
    "zufällig gemischt": "Dieselben Stücke in zufälliger Reihenfolge.",
    "aufsteigend": "Dieselben Stücke, die kleinsten zuerst.",
    "absteigend": "Dieselben Stücke, die größten zuerst (First Fit wird damit zu First Fit Decreasing).",
}
LOGNORMAL_MEDIAN, LOGNORMAL_SIGMA = 0.25, 0.5
THREE_SIZES = (3120, 2040, 1020)
PHASE_SIZES = (998, 2001, 3001)                  # etwa 1/6, 1/3, 1/2 der Behälterfüllung; je ein Stück jeder Gruppe füllt einen Behälter ganz
HAND_ITEMS = (3600, 3000, 2400, 3000)
HALF, TINY = 3000, 1
TRACE_LEN = 20

# feste Experimente (nie ein einzelner Seed als Befund)
SWEEP_SEEDS = tuple(range(100, 110))
SWEEP_N = 2000
GROWTH_SEEDS = tuple(range(200, 205))
GROWTH_NS = (50, 200, 1000, 4000)
NF_ADVERSARY_NS = (20, 200, 2000)
PHASES_N = 600                                   # Stücke je Gruppe bei der Dreiphasenfolge in Experiment 1
ORDER_NS = (60, 600)
TYPICAL_FOLGEN = FOLGEN[:7]

GUARANTEES = {"Next Fit": 2.0, "First Fit": 1.7, "Best Fit": 1.7}   # Harmonic: aus der Gewichtsfunktion, siehe onp_algorithm.harmonic_guarantee

COLOR_NF = "#c0392b"
COLOR_FF = "#2F6B65"
COLOR_BF = "#4c78a8"
COLOR_HARMONIC = "#7c3aed"
COLOR_REF = "rgba(150,150,150,0.8)"
COLOR_GUARANTEE = "#d97706"
COLORS = {"Next Fit": COLOR_NF, "First Fit": COLOR_FF, "Best Fit": COLOR_BF, "Harmonic": COLOR_HARMONIC}

PRESETS = {
    "Dreiphasenfolge (Gegner)": {"regel": "First Fit", "folge": "Dreiphasenfolge (Gegner)", "ordnung": "wie erzeugt", "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "Dieselben Stücke, zufällig gemischt": {"regel": "First Fit", "folge": "Dreiphasenfolge (Gegner)", "ordnung": "zufällig gemischt", "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "Mini-Instanz von Hand": {"regel": "Next Fit", "folge": "von Hand (4 Stücke, wiederholt)", "ordnung": "wie erzeugt", "n": 4, "seed": DEFAULT_SEED},
    "Next-Fit-Gegner: halb und winzig": {"regel": "Next Fit", "folge": "abwechselnd halb und winzig (Gegner)", "ordnung": "wie erzeugt", "n": 1200, "seed": DEFAULT_SEED},
    "Alltag: gleich (0, 1]": {"regel": "First Fit", "folge": "gleich (0, 1]", "ordnung": "wie erzeugt", "n": 1200, "seed": DEFAULT_SEED},
    "Harmonic im Alltag: drei Größen": {"regel": "Harmonic", "folge": "drei Größen", "ordnung": "wie erzeugt", "n": 1200, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Dreiphasenfolge (Gegner)": "Erst kleine, dann mittlere, dann große Stücke: First Fit braucht zwei Drittel mehr Behälter als nötig, die drei anderen Online-Regeln auch (die Referenz FFD nicht).",
    "Dieselben Stücke, zufällig gemischt": "Genau dieselben Stücke wie im ersten Preset, nur gemischt: First Fit liegt dicht am Optimum.",
    "Mini-Instanz von Hand": "Vier Stücke 3600, 3000, 2400, 3000: Next Fit braucht drei Behälter, First Fit und Best Fit zwei. Zum Nachrechnen.",
    "Next-Fit-Gegner: halb und winzig": "Halber Behälter, winziges Stück, im Wechsel: Next Fit verbraucht fast das Doppelte, First Fit legt die winzigen Stücke in den ersten Behälter.",
    "Alltag: gleich (0, 1]": "Zufällige Größen, wie sie im Alltag eher vorkommen: First Fit liegt wenige Prozent über dem Optimum, weit unter der Garantie.",
    "Harmonic im Alltag: drei Größen": "Dieselbe Garantie wie First Fit, im Alltag deutlich schlechter: Harmonic packt jede Größenklasse für sich.",
}
