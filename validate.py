"""
validate.py — biological sanity checks
=======================================
Run: python validate.py
Prints PASS/FAIL for each expected behaviour.
"""

from constants import DT
from simulate import run
import numpy as np

class State:

    def __init__(self, shape=(10, 10, 10), initial={}, scenario="hypoxia"):
        self.scenario = scenario
        self.shape = shape
        self.o2 = np.zeros(shape)
        self.atp = np.zeros(shape)
        

    def update(self):
        self.update_atp()
        ...
        
    def update_atp(self):
        grid = np.array
    


def check(results, name, condition, got, expected_str):
    status = "PASS" if condition else "FAIL"
    results.append(condition)
    print(f"  [{status}] {name}")
    if not condition:
        print(f"         got {got:.4f}, expected {expected_str}")


def run_validation():
    print("\n" + "="*60)
    print("VALIDATION — biological sanity checks")
    print("="*60)
    results = []

    # ── Test 1: Normoxic steady state ──────────────────────
    print("\n[1] Normoxic steady state (30 min):")
    _, h = run(scenario="normal", duration=30.0)
    check(results, "ATP in physiological range (3–6 mM)", 3.0 < h["ATP"][-1] < 6.0,    h["ATP"][-1],    "3–6 mM")
    check(results, "HIF-1α stays near 0",                  h["hif1a"][-1] < 0.05,        h["hif1a"][-1],  "~0")
    check(results, "Na+ cytosolic in range (3–15 mM)",     3.0 < h["Na_cyt"][-1] < 15.0, h["Na_cyt"][-1], "3–15 mM")

    # ── Test 2: Hypoxia response ────────────────────────────
    print("\n[2] Hypoxia scenario (O2 cut t=5–20 min):")
    _, h = run(scenario="hypoxia", duration=30.0)
    i_hyp = int(12.0 / DT)   # t=12 min — 7 min into hypoxia
    i_rec = int(25.0 / DT)   # t=25 min — 5 min after O2 returns

    check(results, "O2 near zero during hypoxia (<0.005 mM)",  h["O2"][i_hyp] < 0.005,                     h["O2"][i_hyp],      "<0.005 mM")
    check(results, "HIF-1α activates (>0.5)",                  h["hif1a"][i_hyp] > 0.5,                     h["hif1a"][i_hyp],   ">0.5")
    check(results, "Lactate rises during hypoxia (>2 mM)",     h["lactate"][i_hyp] > 2.0,                   h["lactate"][i_hyp], ">2 mM")
    check(results, "ATP recovers after O2 return",             h["ATP"][i_rec] > h["ATP"][i_hyp],           h["ATP"][i_rec],     f">{h['ATP'][i_hyp]:.3f}")
    check(results, "HIF-1α falls after O2 return",            h["hif1a"][i_rec] < h["hif1a"][i_hyp],       h["hif1a"][i_rec],   f"<{h['hif1a'][i_hyp]:.3f}")

    # ── Test 3: Starvation ──────────────────────────────────
    print("\n[3] Glucose starvation (glucose cut at t=5 min):")
    _, h = run(scenario="starvation", duration=30.0)
    i_starve = int(20.0 / DT)
    check(results, "Glucose depletes during starvation (<0.5 mM)", h["glucose"][i_starve] < 0.5, h["glucose"][i_starve], "<0.5 mM")
    check(results, "ATP falls during starvation (<3.5 mM)",        h["ATP"][i_starve] < 3.5,     h["ATP"][i_starve],     "<3.5 mM")

    passed = sum(results)
    total  = len(results)
    print(f"\n  {passed}/{total} tests passed.")
    print("="*60 + "\n")
    return passed, total


if __name__ == "__main__":
    run_validation()