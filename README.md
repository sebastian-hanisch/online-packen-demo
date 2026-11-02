# Online-Packen – Frachtstücke ans Tor, ohne die späteren zu kennen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-online-packen-demo.streamlit.app/)** -->

Drittes Stück der Reihe **Online-Algorithmen** („Entscheiden ohne Kenntnis der Zukunft“) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, unabhängiger Ast neben [paging-demo](https://github.com/sebastian-hanisch/paging-demo) unter der Wurzel [ski-rental-demo](https://github.com/sebastian-hanisch/ski-rental-demo).
Anders als die Fall-Demos (ein Anwendungsfall, mehrere Verfahren im Vergleich) zeigt diese Demo **ein** Konzept, die **Wettbewerbsanalyse**, an einem wachsenden Beispiel: von vier Stücken zum Nachrechnen über Folgen, die gegen eine Regel gebaut sind, bis zu zufälligen Stücken und der Frage, was allein die Reihenfolge kostet.
Kante zum Vorgänger: Ski-Rental hat **eine** Anschaffung, hier teilen sich **viele Stücke** begrenzten Platz in Behältern.

**Verwandte bestehende Demos:** `freight_demo` (First Fit Decreasing für 1D-Packen im Container, **offline**), `cutting-stock-demo` und `cutting-stock-branch-bound-demo` (FFD als Vergleich), `pack_demo` (3D-Packen, offline), `bahnladeplan-demo` (nennt die Online-Beladung ausdrücklich als nicht modelliert). Keine davon packt die Stücke nacheinander ohne Kenntnis der späteren.

## Warum dieses Problem

Frachtstücke kommen nacheinander ans Tor, und jedes muss sofort in einen Lkw oder Container (Fassungsvermögen 6000 Einheiten) gelegt werden. Wer sortieren kann (First Fit Decreasing), ist fast optimal; wer nicht, hat Regeln. Die Kernfrage: **Was kostet eine Regel im schlimmsten Fall, was bei zufälligen Stücken, und was kostet allein die Reihenfolge?**

## Modell

Behälter der Größe C = 6000, Stücke mit ganzzahligen Größen 1 bis C, die nacheinander kommen; jedes wird sofort und endgültig in einen Behälter gelegt. Kosten = Zahl der geöffneten Behälter. Vier Regeln: **Next Fit** (zuletzt geöffneter Behälter), **First Fit** (erster passender), **Best Fit** (passender, danach am vollsten), **Harmonic** mit sechs Klassen (Klasse j: Größe in (C/(j+1), C/j], j Stücke je Behälter; kleinere Stücke per Next Fit). Referenz: bei den Gegnerfolgen das von Hand bekannte Optimum, sonst **First Fit Decreasing** (offline, eine Obergrenze des Optimums); dazu die Untergrenze ⌈Summe/C⌉. Formeln im 📐-Expander der App.
Zehn Folgen: sieben Zufallsverteilungen (gleich (0, 1], (0, 0,5], (0,2, 0,8], (1/6, 1/2], (0, 0,1], Lognormal um ein Viertel, drei Größen 0,52 / 0,34 / 0,17), die **Dreiphasenfolge** (Stücke 998, 2001, 3001 je n/3 mal; je ein Stück jeder Gruppe füllt einen Behälter genau), **abwechselnd halb und winzig** (3000, 1, 3000, 1, …) und die Handrechnung (3600, 3000, 2400, 3000). Vier Reihenfolgen: wie erzeugt, zufällig gemischt, aufsteigend, absteigend. Die Füllgrad-Karte der App färbt Behälter ab 90 % grün, ab 60 % gelb, darunter rot (nur Darstellung).

## Methodik

| Abschnitt der App | Was gerechnet wird |
|---|---|
| Ergebnis | alle vier Regeln auf der gewählten Folge in der gewählten Reihenfolge; Behälter, Füllgrade, Ablauf der ersten 20 Stücke |
| Experiment 1 | a) Next Fit gegen halb/winzig (20, 200, 2000 Stücke); b) Dreiphasenfolge mit 600 Stücken je Gruppe, Präfixe nach Gruppe 1, 2, 3 |
| Experiment 2 | dieselben 1800 Stücke der Dreiphasenfolge in vier Reihenfolgen |
| Experiment 3 | sieben Zufallsverteilungen mit 2000 Stücken, Mittel über zehn feste Seeds, Quotient zu FFD |
| Experiment 4 | gleich (0, 1] mit 50 bis 4000 Stücken, Mittel über fünf feste Seeds |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen in `tests/test_claims.py` nachgerechnet. „Quotient“ steht für Behälter geteilt durch das Optimum (Gegnerfolgen) beziehungsweise durch FFD.

| Frage | Befund |
|---|---|
| Mini-Instanz von Hand (3600, 3000, 2400, 3000)? | Next Fit 3 Behälter, First Fit 2, Best Fit 2, Harmonic 3, Optimum 2. |
| Next Fit gegen halb und winzig? | Quotient 1,667 / 1,961 / **1,996** bei 20 / 200 / 2000 Stücken: nähert sich 2. First Fit, Best Fit und Harmonic liegen bei **1,000**: First Fit legt alle winzigen Stücke in den ersten Behälter. |
| Dreiphasenfolge (600 Stücke je Gruppe)? | **Alle vier Regeln** brauchen 100, 400 und 1000 Behälter nach Gruppe 1, 2, 3 gegen das Optimum 100, 300, 600: Quotient 1,000, 1,333 und **1,667**. FFD (offline) braucht 100, 300 und 600. |
| Dieselben 1800 Stücke gemischt? | First Fit und Best Fit **1,017** (610 Behälter), Next Fit 1,267, Harmonic bleibt bei **1,667**; das gilt für die eine Mischung mit Seed 7, bei 40 anderen Mischungen liegt First Fit zwischen 1,007 und 1,052, Next Fit zwischen 1,25 und 1,28, Harmonic bei 1,667. In absteigender Reihenfolge: First Fit und Best Fit 1,000 (das ist FFD), Next Fit und Harmonic 1,667. Die gegnerische Reihenfolge ist zugleich die aufsteigende. Bei Gruppengröße 60 liegt First Fit gemischt bei 1,050 (Seed 7; bei 40 anderen Mischungen zwischen 1,017 und 1,133). |
| Alltag, sieben Verteilungen (2000 Stücke, zehn Seeds)? | First Fit **1,001 bis 1,043**, Best Fit **1,001 bis 1,026**, Next Fit 1,033 bis 1,372, Harmonic 1,033 bis 1,414. Garantien: First Fit und Best Fit 1,7, Next Fit 2. |
| Wo ist Harmonic am schlechtesten? | Bei „drei Größen“ **1,414** gegen First Fit 1,001; bei (0,2, 0,8] 1,390 gegen 1,043. Harmonic hat dieselbe Garantie wie First Fit (1,70 für sechs Klassen) und ist im Alltag deutlich schlechter. |
| Wächst die Länge (gleich (0, 1])? | First Fit 1,044 / 1,049 / 1,041 / **1,028** und Best Fit 1,037 / 1,037 / 1,027 / **1,017** bei 50 / 200 / 1000 / 4000 Stücken; Next Fit 1,233 / 1,280 / 1,318 / 1,317. |
| Einzelne Presets (n = 1200, gleich (0, 1])? | First Fit 644 Behälter, Best Fit 636, Next Fit 809, Harmonic 781 gegen FFD 619 und Untergrenze 607. |
| Garantie von Harmonic als Gewichtswert (eigene Herleitung)? | Für 2, 3, 4, 5, 6, 8, 10, 12 Klassen: 2,0000 / 1,7500 / 1,7222 / 1,7083 / **1,7000** / 1,6939 / 1,6931 / 1,6926; Grenzwert Σ 1/(tᵢ − 1) = **1,69103**, gleich dem Literaturwert. |
| Wie weit liegt FFD von der Untergrenze? | FFD/Summe 1,000 bis 1,050; bei „drei Größen“ **1,165**, weil Stücke von 0,52 nie zu zweit passen: dort sagt die Untergrenze wenig, FFD ist die engere Referenz. |

## Ehrliche Grenzen

- Die Demo ist **nur an erfundenen Folgen** geprüft; die Verteilungen sind Modelle, keine Messung echter Fracht.
- Die Referenz FFD ist eine **Obergrenze** des Optimums, nicht das Optimum. Die Quotienten zu FFD sind untere Schranken der wahren Quotienten, sofern FFD nicht optimal ist. Das Optimum wird nur bei den Gegnerfolgen (von Hand) und im Test (CP-SAT, kleine Instanzen) exakt bestimmt.
- Die Garantien (Next Fit 2, First Fit und Best Fit 1,7) sind asymptotisch (ohne additive Konstante). **Quellenlage:** First Fit 1,7 und Harmonic 1,69103 sind per Auszug bestätigt, Next Fit 2 stützt sich auf Vorlesungsfolien, Best Fit 1,7 auf einen Eintragsvermerk; die Primärquellen wurden nicht eingesehen (**offen**).
- Die Garantie von Harmonic mit sechs Klassen (1,70) ist eine **eigene Herleitung** über eine Gewichtsfunktion im Stil von Lee/Lee; ihr Grenzwert stimmt mit dem Literaturwert überein, die Quelle selbst wurde nicht eingesehen.
- Harmonic ist nur gegenüber den größeren Stücken reihenfolgeblind; die kleinen (höchstens ein Sechstel) packt es per Next Fit und spürt die Reihenfolge dort.
- Advanced Harmonic (beste bekannte Obergrenze 1,57829) und Super Harmonic sind nicht umgesetzt; die untere Schranke 1,54278 wird genannt, nicht gezeigt.
- Bei der Dreiphasenfolge ist der Quotient 5/3 nur bei durch 6 teilbarer Gruppengröße exakt; bei 200 Stücken je Gruppe liegt First Fit bei 333 gegen 200 Behälter.

## Verifikation

- **Umfang:** 207 Tests (siehe `pytest --collect-only -q tests`), rund 100 Sekunden lokal (gemessen: 96 Sekunden).
- **Kern:** Zuordnungen gegen Handrechnung auf der Mini-Instanz, auf den Gegnerfolgen mit sechs Stücken je Gruppe und auf kleinen Folgen; Randfälle (ein Stück, volles Stück, leere Folge).
- **Orakel** (`tests/test_oracle_online_packen.py`): das Optimum exakt per CP-SAT gegen die **Aufzählung aller Zuordnungen**; das von Hand bekannte Optimum der Gegnerfolgen gegen CP-SAT; First Fit, Best Fit und Harmonic gegen zweite, plumpere Fassungen; FFD nie besser als das Optimum, Untergrenze nie darüber.
- **Eigenschaften** (`tests/test_eigenschaften_online_packen.py`): kein Behälter überfüllt (unabhängiger Prüfer); Online-Eigenschaft (Präfix); Skalierung von Stücken und Behälter ändert nichts; Next Fit höchstens das Doppelte der Untergrenze; First Fit höchstens ⌊1,7 · FFD⌋; First Fit auf absteigender Folge gleich FFD; Harmonic ohne kleine Stücke reihenfolgeblind.
- **Literatur:** kein Referenzwert-Test. Die Schranken 1,7, 1,69103, 1,5, 1,54278 und 1,57829 stammen aus Auszügen (Dósa/Sgall, Lee/Lee, Yao, Balogh u. a.), die Volltexte wurden **nicht eingesehen** (**offen**).
- **Verdikte** (`tests/test_verdicts.py`): jede Zahl und jede Verzweigung der Texte. **Claims** (`tests/test_claims.py`): jede Zahl dieser README.
- **Presets, Layout, Oberfläche:** vollständig, Werte in den Reglergrenzen; Schnellstart oben in der Seitenleiste, aktives Preset hervorgehoben; AppTest-Rauchtest (jeder Button, jeder Regler an beiden Grenzen, jede Auswahl jedes Auswahlfelds); Footer; Laufzeit-Importe.
- **Browser:** im Desktop-Browser durchgeklickt (alle sechs Presets, Seitenleiste, Diagramme). Nicht mit echtem Touch-Gerät getestet.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, vier Experimente, Grenzen, Formeln |
| `requirements-dev.txt` | Laufzeit plus pytest und ortools (nur für das Orakel) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `onp_algorithm.py` | Kern: Next Fit, First Fit, Best Fit, Harmonic, FFD, Prüfer, Garantie von Harmonic |
| `onp_constants.py` | Regler-Grenzen, Folgenparameter, feste Experimente, Farben, Presets |
| `onp_evaluation.py` | Kennzahlen, Experimente, Ablauftabelle, Verdikte |
| `onp_layout.py` | Fester Kopf (Stylesheet) |
| `onp_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `onp_scenario.py` | Die zehn Folgen, die vier Reihenfolgen, das bekannte Optimum der Gegnerfolgen |
| `onp_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Kern, Randfälle, Orakel, Eigenschaften, Verdikte, Claims, Presets, Layout, Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Advanced Harmonic und Super Harmonic**, Verfahren mit Zufall und mit Umpacken.
- **Mehrdimensionales Packen**, Gewicht und Volumen zugleich, verschiedene Behältertypen: `pack_demo` und die Seefracht-Demos.
- **Annahmeentscheidungen** (nicht jedes Stück wird gebraucht): Online-Allokation, ein eigenes Stück der Reihe.
- **Vorhersagen** über die Stückgrößen: ein eigenes Stück der Reihe.
- **Echte Frachtdaten** und PDF-Export.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
