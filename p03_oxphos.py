"""
p03_oxphos.py — Process 3: Oxidative phosphorylation (mitochondria)
====================================================================
Oxidises pyruvate in the presence of O2 to produce ~30 ATP per pyruvate.
This is the cell's main energy source under normoxic conditions.
Cytochrome c oxidase has an extremely high O2 affinity (Km ~0.5 µM),
so even low O2 levels sustain OxPhos — until they don't.

Equations
---------
  v_oxphos = Vmax × mm([Pyr], Km_pyr) × mm([O2], Km_o2)
  (double Michaelis-Menten: limited by both pyruvate and O2)

Stoichiometry
-------------
  pyruvate -= v_oxphos
  O2       -= O2_PER_OXPHOS × v_oxphos   (3 O2 per pyruvate)
  ATP      += ATP_PER_OXPHOS × v_oxphos  (30 ATP per pyruvate)
  ADP      -= ATP_PER_OXPHOS × v_oxphos
"""

from constants import (
    VMAX_OXPHOS, KM_OXPHOS_PYR, KM_OXPHOS_O2,
    ATP_PER_OXPHOS, O2_PER_OXPHOS,
)
from helpers import mm
import numpy as np


def compute(s, dt):
    v = VMAX_OXPHOS * mm(s["pyruvate"], KM_OXPHOS_PYR) * mm(s["O2"], KM_OXPHOS_O2) * dt
    # Substrate clamps — cannot consume more than available
    v = np.minimum(v, s["pyruvate"])
    v = np.minimum(v, s["O2"] / max(O2_PER_OXPHOS, 1e-9))
    v = np.minimum(v, s["ADP"] / max(ATP_PER_OXPHOS, 1e-9))
    return {"v_oxphos": v}


def apply(s, fluxes):
    v = fluxes["v_oxphos"]
    s["pyruvate"] -= v
    s["O2"]       -= O2_PER_OXPHOS * v
    s["ATP"]      += ATP_PER_OXPHOS * v
    s["ADP"]      -= ATP_PER_OXPHOS * v
    return s
