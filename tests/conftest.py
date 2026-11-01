"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mini():
    """Vier Stücke 3600, 3000, 2400, 3000, Behälter 6000.

    Handrechnung: Next Fit: 3600 | 3000 passt nicht (6600) → neuer Behälter | 2400 passt (5400) | 3000 passt nicht → dritter Behälter: 3 Behälter.
    First Fit: 3600 | 3000 neu | 2400 passt zu 3600 (6000) | 3000 passt zu 3000 (6000): 2 Behälter. Best Fit: 2400 geht zu 3600 (danach 0 frei, besser
    als 600 frei bei 3000), dann 3000 zu 3000: 2 Behälter. Optimum 2 (3600 + 2400 und 3000 + 3000). Harmonic: 3600 allein, 3000 und 2400 bilden
    Klasse 2 (je zwei Stücke je Behälter), das zweite 3000 öffnet einen neuen Behälter: 3 Behälter."""
    return [3600, 3000, 2400, 3000]
