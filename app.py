"""Online-Packen – Frachtstücke ans Tor, ohne die späteren zu kennen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Drittes Stück der Reihe „Online-Algorithmen“: jedes Stück wird sofort und endgültig in einen Behälter gelegt, die späteren sind unbekannt.
Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import onp_algorithm as A
import onp_constants as C
from onp_evaluation import (
    Settings,
    analyse,
    delta_text,
    growth_rows,
    guarantee,
    nf_adversary_rows,
    order_rows,
    phase_rows,
    typical_rows,
    verdict_kern,
    verdict_laenge,
    verdict_nf,
    verdict_phasen,
    verdict_reihenfolge,
    verdict_typisch,
)
from onp_layout import dunkles_design, kopf_css
from onp_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from onp_visualization import build_bins, build_fills, build_growth, build_nf, build_orders, build_phases, build_typical

st.set_page_config(page_title="Online-Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _nf():
    return nf_adversary_rows()


@st.cache_data(show_spinner=False)
def _phases():
    return phase_rows()


@st.cache_data(show_spinner=False)
def _orders():
    return order_rows()


@st.cache_data(show_spinner="Rechne die sieben Verteilungen über zehn Seeds …")
def _typical():
    return typical_rows()


@st.cache_data(show_spinner=False)
def _growth():
    return growth_rows()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in onp_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📦 Online-Packen – Frachtstücke ans Tor, ohne die späteren zu kennen")
st.markdown(
    f"""
**Drittes Stück der Reihe „Online-Algorithmen“** (Entscheiden ohne Kenntnis der Zukunft). Frachtstücke kommen **nacheinander** ans Tor; jedes muss **sofort und endgültig** in einen Lkw oder Container (Fassungsvermögen {C.CAPACITY}) gelegt werden, ohne die späteren zu kennen.
Welche **Regel** braucht am wenigsten Behälter? Gemessen wird am **Optimum mit Vorwissen**, das **Wettbewerbsverhältnis** ist der Quotient der Behälterzahlen.

Weiter unten: die **Kernfrage**, vier Experimente (**die Folge gegen die Regel**, **dieselben Stücke in anderer Reihenfolge**, **typische Stücke**, **wachsende Länge**), **🚧 Wo die Annahmen enden**, **⚠️ Annahmen, Grenzen und bekannte Probleme** und **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Online-Packen", expanded=True):
    st.markdown(
        """
1. **Next Fit** legt das Stück in den zuletzt geöffneten Behälter und öffnet einen neuen, wenn es nicht passt: schnell, aber ältere Behälter bleiben ungenutzt.
2. **First Fit** legt es in den ersten Behälter, in den es passt; **Best Fit** in den passenden Behälter, der danach am vollsten ist.
3. **Harmonic** teilt die Stücke nach Größe in Klassen und packt jede Klasse für sich (j Stücke der Klasse j je Behälter): schlechter im Durchschnitt, bei gleich hoher Garantie (1,70 für sechs Klassen), dafür unabhängig von der Reihenfolge der größeren Stücke.
4. **Die Referenz** kennt alle Stücke vorher: **First Fit Decreasing** sortiert absteigend und ist meist optimal oder einen Behälter darüber (Obergrenze des Optimums). Für die Gegnerfolgen ist das Optimum von Hand bekannt.
5. **Garantie ist nicht Alltag:** die Garantien (Next Fit 2, First Fit und Best Fit 1,7) werden von zufälligen Stücken weit unterschritten; angenähert werden sie von gegen die Regel gebauten Folgen; was zufällige Stücke und die Reihenfolge ausmachen, zeigen die Experimente.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Regel**")
    regel = st.selectbox("Regel (hervorgehoben)", C.REGELN, key="regel_select", help="Alle Regeln laufen mit; die gewählte steht im Ergebnis und im Verdikt.")
    st.caption(C.REGEL_HILFE[regel])
    st.markdown("**Stücke**")
    folge = st.selectbox("Folge", C.FOLGEN, key="folge_select", help="Wie die Größen der Stücke entstehen; die Regeln kennen sie nicht.")
    st.caption(C.FOLGEN_HILFE[folge])
    ordnung = st.selectbox("Reihenfolge", C.ORDNUNGEN, key="ordnung_select", help="Dieselben Stücke in anderer Reihenfolge: das ist der Kern des Stücks.")
    st.caption(C.ORDNUNG_HILFE[ordnung])
    n = st.select_slider("Zahl der Stücke n", options=C.N_OPTIONS, key="n_select")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Stücke ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"regel_select": regel, "folge_select": folge, "ordnung_select": ordnung, "n_select": int(n), "seed_input": int(seed)})

settings = Settings(regel, folge, ordnung, int(n), int(seed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.caption(f"{a.count} Stücke „{folge}“, Reihenfolge „{ordnung}“ · Behälter fassen {C.CAPACITY} · hervorgehoben: {regel}")
q = a.ratios[regel]
g = guarantee(regel)
m1, m2, m3, m4 = st.columns(4)
diff = a.bins[regel] - a.ref
d1, c1 = ("gleich wie " + a.ref_label, "off") if diff == 0 else (f"{diff:+d} gegen {a.ref_label}", "inverse")
m1.metric("Behälter der Regel", f"{a.bins[regel]}", delta=d1, delta_color=c1, help=f"Zahl der Behälter, die {regel} öffnet.")
m2.metric(f"Referenz: {a.ref_label}", f"{a.ref}", delta="Referenz", delta_color="off",
          help="Bei den Gegnerfolgen das von Hand bekannte Optimum, sonst First Fit Decreasing (eine Obergrenze des Optimums).")
d3, c3 = delta_text(q, g, "Garantie")
m3.metric("Quotient", f"{q:.3f}", delta=d3, delta_color=c3, help="Behälter der Regel geteilt durch die Referenz.")
m4.metric("Untergrenze", f"{a.lower}", delta=f"FFD braucht {a.ffd}", delta_color="off", help="Summe aller Stücke geteilt durch das Fassungsvermögen, aufgerundet: weniger Behälter gibt es nie.")
st.plotly_chart(build_bins(a.bins, a.ref, a.ref_label, a.ffd, a.lower, regel), width="stretch", key="bins_chart")
st.caption("Behälter je Regel (hervorgehoben: die gewählte). Gestrichelt: die Referenz; gepunktet: FFD und die Untergrenze aus der Gesamtgröße.")
st.plotly_chart(build_fills(a.fills), width="stretch", key="fills_chart")
st.caption(f"Füllgrad der ersten Behälter von {regel} (grün: mindestens 90 %, gelb: mindestens 60 %, rot: darunter). Je leerer, desto mehr Verschnitt.")
with st.expander(f"Ablauf der ersten {C.TRACE_LEN} Stücke: in welchen Behälter jede Regel legt"):
    st.caption("Behälternummern ab 1, in der Reihenfolge ihrer Öffnung; gleiche Stückzahl, gleiche Größen, jede Regel entscheidet für sich.")
    st.dataframe(pd.DataFrame(a.trace), hide_index=True, width="stretch")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was kostet die Regel gegenüber der Referenz?")
kind, text = verdict_kern(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Die Folge, die gegen die Regel gebaut ist")
st.markdown("**a) Halb und winzig im Wechsel** (Stücke 3000 und 1): Next Fit öffnet für jedes halbe Stück einen neuen Behälter, First Fit legt alle winzigen in den ersten.")
rows_nf = _nf()
st.plotly_chart(build_nf(rows_nf), width="stretch", key="nf_chart")
kind, text = verdict_nf(rows_nf)
getattr(st, kind)(text)
st.markdown(f"**b) Die Dreiphasenfolge** ({C.PHASES_N} Stücke je Gruppe von etwa einem Sechstel, einem Drittel und der Hälfte; je ein Stück jeder Gruppe füllt einen Behälter genau): Präfixe nach der ersten, zweiten und dritten Gruppe.")
rows_ph = _phases()
st.plotly_chart(build_phases(rows_ph), width="stretch", key="phases_chart")
kind, text = verdict_phasen(rows_ph)
getattr(st, kind)(text)
with st.expander("Tabelle zum Diagramm"):
    st.dataframe(pd.DataFrame(rows_ph), hide_index=True, width="stretch")

st.markdown("---")

st.subheader("🔬 Experiment 2: Dieselben Stücke, andere Reihenfolge")
st.caption(f"Die Dreiphasenfolge mit {3 * C.ORDER_NS[-1]} Stücken; das Optimum ist {C.ORDER_NS[-1]} Behälter, in jeder Reihenfolge. Nur die Reihenfolge ändert sich; die gegnerische ist zugleich die aufsteigende. "
    "Harmonic ist hier reihenfolgeblind, weil es die Stücke nur nach Größenklassen zählt (nur Stücke bis ein Sechstel würden die Reihenfolge spüren).")
rows_or = _orders()
st.plotly_chart(build_orders(rows_or), width="stretch", key="orders_chart")
kind, text = verdict_reihenfolge(rows_or)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Experiment 3: Und bei zufälligen Stücken?")
rows_ty = _typical()
st.caption(f"Sieben Verteilungen mit {C.SWEEP_N} Stücken, Mittel über {len(C.SWEEP_SEEDS)} feste Seeds; Quotient zu First Fit Decreasing. Garantien: Next Fit 2, First Fit und Best Fit 1,7, Harmonic {guarantee('Harmonic'):.2f}.")
st.plotly_chart(build_typical(rows_ty), width="stretch", key="typical_chart")
kind, text = verdict_typisch(rows_ty)
getattr(st, kind)(text)
with st.expander("Tabelle zum Diagramm"):
    st.dataframe(pd.DataFrame(rows_ty), hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(format="%.3f") for c in ("FFD / Summe", *C.REGELN)})

st.markdown("---")

st.subheader("🔬 Experiment 4: Wächst die Länge?")
rows_gr = _growth()
st.caption(f"Gleichverteilte Größen (0, 1], Mittel über {len(C.GROWTH_SEEDS)} feste Seeds; Quotient zu First Fit Decreasing.")
st.plotly_chart(build_growth(rows_gr), width="stretch", key="growth_chart")
kind, text = verdict_laenge(rows_gr)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Jedes Stück wird sofort und endgültig platziert** | Darf man umpacken oder kurz warten, ändert sich das Problem; nicht modelliert. | – |
| **Die Stückgrößen sind vorab ganz unbekannt** | Eine Vorhersage über die kommenden Größen lässt sich nutzen, darf aber nicht blind gelten; Experiment 2 zeigt, wie viel an der Reihenfolge hängt. | Vorhersagen |
| **Eine Dimension, gleich große Behälter** | Gewicht und Volumen zugleich, verschiedene Behältertypen und Entladereihenfolgen fehlen. | – |
| **Alle Stücke gleich wichtig** | Hat jedes Stück einen Wert und die Kapazität reicht nicht für alle, wird aus dem Packen eine Annahmeentscheidung. | Online-Allokation |
| **Die Verteilungen sind erfunden** | Gleichverteilung, Lognormal und drei Größen sind Modelle, keine Messung echter Fracht. | – |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(
        f"""
**Annahmen.** Behälter fassen {C.CAPACITY} Einheiten, Stückgrößen sind ganze Zahlen von 1 bis {C.CAPACITY}. Die Referenz ist bei den Gegnerfolgen das von Hand bekannte Optimum, sonst First Fit Decreasing (offline); FFD ist eine **Obergrenze** des Optimums, nicht das Optimum selbst. Die Quotienten zu FFD sind deshalb untere Schranken der wahren Quotienten, sofern FFD nicht optimal ist.

**Grenzen.** Die Demo ist nur an erfundenen Folgen geprüft. Die Garantien sind **asymptotisch** (ohne additive Konstante); bei wenigen Stücken können Quotienten abweichen. Die Garantie von Harmonic mit {C.HARMONIC_M} Klassen ist eine eigene Herleitung über eine Gewichtsfunktion; ihr Grenzwert für viele Klassen stimmt mit dem Literaturwert 1,69103 überein, die Quelle selbst wurde nicht eingesehen. Next Fit 2 und Best Fit 1,7 stützen sich auf Vorlesungsfolien beziehungsweise einen Eintragsvermerk. Advanced Harmonic (beste bekannte Obergrenze 1,57829) und Super Harmonic sind nicht umgesetzt.

**Bekannte Probleme und Unsicherheiten.** Die Zahl der Stücke wird bei den Gegnerfolgen auf ein Vielfaches von 3 (Dreiphasenfolge), 2 (abwechselnd) oder 4 (von Hand) abgerundet. Bei der Dreiphasenfolge ist der Quotient 5/3 erreicht, wenn die Gruppengröße durch 6 teilbar ist; sonst liegt er knapp darunter. Bei „abwechselnd halb und winzig“ passen alle winzigen Stücke in den Platz neben den halben Stücken oder in einen weiteren Behälter (n höchstens 5000).
        """
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        rf"""
**Lesehilfe.** Gegeben sind Behälter der Größe $C = {C.CAPACITY}$ und Stücke $s_1, s_2, \dots$ mit $0 < s_i \le C$, die nacheinander kommen; jedes wird sofort in einen Behälter gelegt, ohne Umpacken. Gesucht ist die Zahl der Behälter, möglichst nahe an der kleinsten möglichen.

| Symbol | Bedeutung |
|---|---|
| $C$ | Fassungsvermögen eines Behälters |
| $s_i$ | Größe des $i$-ten Stücks |
| $A(\sigma)$ | Zahl der Behälter der Regel $A$ auf der Folge $\sigma$ |
| $\mathrm{{OPT}}(\sigma)$ | kleinste mögliche Zahl der Behälter für dieselben Stücke |
| $\lceil \sum s_i / C \rceil$ | Untergrenze: weniger Behälter gibt es nie |

**Wettbewerbsverhältnis (asymptotisch).** $\limsup_{{\mathrm{{OPT}} \to \infty}} \max_\sigma A(\sigma)/\mathrm{{OPT}}(\sigma)$. Für Next Fit ist es 2, für First Fit und Best Fit 1,7; kein Online-Verfahren kommt unter 1,5 (Yao), die besten bekannten Schranken liegen bei 1,54278 (unten) und 1,57829 (oben).

**Dreiphasenfolge.** Je $N$ Stücke der Größen 998, 2001 und 3001 (ungefähr $\tfrac16$, $\tfrac13$, $\tfrac12$ von $C$): ein Stück jeder Gruppe füllt einen Behälter genau, also $\mathrm{{OPT}} = N$. First Fit packt die erste Gruppe zu sechst ($N/6$ Behälter), die zweite zu zweit ($N/2$) und die dritte allein ($N$): zusammen $\tfrac53 N$.

**Harmonic.** Ein Stück mit $C/(j+1) < s \le C/j$ gehört zur Klasse $j$ ($j = 1, \dots, M-1$), je $j$ Stücke teilen sich einen Behälter; Stücke mit $s \le C/M$ gehen per Next Fit in eigene Behälter. Gewichte: Klasse $j$ zählt $1/j$, ein kleines Stück $\tfrac{{M}}{{M-1}} \cdot s/C$. Ein Behälter der Optimallösung trägt höchstens das Gewicht $w_M$, und das ist die Garantie: für $M = {C.HARMONIC_M}$ ist $w_M = {guarantee('Harmonic'):.2f}$, für $M \to \infty$ strebt $w_M$ gegen $\sum_i 1/(t_i - 1) \approx 1{{,}}691$ mit $t_1 = 2$, $t_{{i+1}} = t_i(t_i - 1) + 1$.

**Referenz.** First Fit Decreasing sortiert die Stücke absteigend und wendet First Fit an; sie ist offline und meist optimal oder einen Behälter darüber.

**Literatur (nicht nachgebaut; Auszüge per Websuche gesehen, Volltexte nicht eingesehen).** G. Dósa, J. Sgall (2013): First Fit 1,7. C. C. Lee, D. T. Lee (1985): Harmonic, Grenzwert 1,69103. A. C. Yao (1980): untere Schranke 1,5. J. Balogh, J. Békési, G. Dósa, L. Epstein, A. Levin (2018, 2021): Obergrenze 1,57829, untere Schranke 1,54278. Hier belegt sind die Zahlen durch vollständiges Durchrechnen der Folgen.
        """
    )

st.markdown("---")
st.caption(
    "Verwandte Demos: [Ski-Rental](https://github.com/sebastian-hanisch/ski-rental-demo) und [Paging](https://github.com/sebastian-hanisch/paging-demo) (Stücke 1 und 2 der Reihe), "
    "[Online-Matching](https://sebastianhanisch-online-matching-demo.streamlit.app/) (Zuordnen ohne Kenntnis der Zukunft), "
    "Fracht im Container (`freight_demo`) und Zuschnitt (`cutting-stock-demo`) packen **offline** mit First Fit Decreasing, die 3D-Packung (`pack_demo`) ebenso."
)
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Online-Algorithmen: Entscheiden ohne Zukunft](https://sebastianhanisch.net/konzepte-online-algorithmen.html)."
)
