"""
p08_mtor.py — Process 8: mTOR-regulated protein synthesis
==========================================================
mTORC1 is the master anabolic switch. It integrates three signals:
  1. ATP/AMP energy status (via AMPK)
  2. Amino acid availability (via Ragulator/Rag GTPases at lysosome)
  3. Growth factors (via PI3K/Akt/TSC axis)

When all three are satisfied, mTORC1 phosphorylates S6K1 and 4E-BP1,
activating ribosome biogenesis and cap-dependent translation.

In this model, mTOR_activity is driven purely by the ATP ratio —
when ATP falls during hypoxia, AMPK activates, suppressing mTORC1.
This creates a direct chain: oxygen crisis → ATP fall → ribosomes stall
→ protein_mass accumulation stops → cell stops growing in AR/VR.

Equations
---------
  mTOR_activity = clamp([ATP] / ATP_normal, 0, 1)
  v_synthesis = Vmax × mTOR × mm([ATP], Km_atp) × mm([AA], Km_aa)
  v_actual    = min(v_synthesis, [ATP]/4, [AA]/1)   ← substrate clamps

Stoichiometry
-------------
  4 ATP  +  1 amino acid  →  1 peptide bond
  ATP          -= 4 × v_actual
  ADP          += 4 × v_actual
  amino_acids  -= 1 × v_actual
  protein_mass += 1 × v_actual
"""

from constants import VMAX_RIBO, KM_ATP_RIBO, KM_AA, ATP_PER_AA, NORMAL_ATP
from helpers import clamp, mm


def compute(s, dt):
    mtor     = clamp(s["ATP"] / NORMAL_ATP, 0.0, 1.0)
    v_theory = VMAX_RIBO * mtor * mm(s["ATP"], KM_ATP_RIBO) * mm(s["amino_acids"], KM_AA) * dt
    v_actual = min(v_theory,
                   s["ATP"] / ATP_PER_AA,
                   s["amino_acids"])
    return {"v_synth": v_actual}


def apply(s, fluxes):
    v = fluxes["v_synth"]
    s["ATP"]          -= ATP_PER_AA * v
    s["ADP"]          += ATP_PER_AA * v
    s["amino_acids"]  -= v
    s["protein_mass"] += v
    return s