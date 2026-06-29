"""
state.py — defines the cell's initial state.
All concentrations in mM unless noted.
"""

def initial_state():
    return {
        # ── Energy ──────────────────────────────────────────
        "ATP":          4.0,    # cytosolic ATP — homeostatic target
        "ADP":          0.5,    # cytosolic ADP
        "AMP":          0.1,    # adenylate pool remainder

        # ── Carbon substrates ────────────────────────────────
        "glucose":      5.0,    # cytosolic glucose (~blood glucose level)
        "pyruvate":     0.15,   # pyruvate pool
        "lactate":      1.0,    # resting lactate

        # ── Oxygen ──────────────────────────────────────────
        "O2":           0.03,   # dissolved O2 (~15 mmHg, normoxic tissue)

        # ── Amino acids & protein ────────────────────────────
        "amino_acids":  2.0,    # free amino acid pool
        "protein_mass": 0.0,    # accumulated protein (drives cell volume in VR)

        # ── Ions ────────────────────────────────────────────
        "Na_cyt":       10.0,   # cytosolic Na+  (resting ~10 mM)
        "Na_ext":       145.0,  # extracellular Na+ (resting ~145 mM)
        "K_cyt":        140.0,  # cytosolic K+   (resting ~140 mM)
        "K_ext":        5.0,    # extracellular K+ (resting ~5 mM)

        # ── Signalling ──────────────────────────────────────
        "hif1a":        0.0,    # HIF-1α activity (0 = off, 1 = fully active)
        "Ca_cyt":       0.0001, # cytosolic Ca2+ (resting ~100 nM = 0.0001 mM)
    }