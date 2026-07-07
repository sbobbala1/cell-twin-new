"""
p04_fermentation.py — Process 4: Fermentation (lactate dehydrogenase)
======================================================================
Converts pyruvate to lactate when O2 is low. Produces no extra ATP but
regenerates NAD+ so glycolysis can keep running. This is the Pasteur effect:
fermentation is inhibited by O2 (aerobic respiration wins when O2 is present).
Under hypoxia, HIF-1α upregulates this process up to 2.5×.

Equations
---------
  o2_inhibition = 1 − mm([O2], Km_o2_inh)    (Pasteur: less O2 = more fermentation)
  v_ferm = Vmax × ferm_scale × mm([Pyr], Km_pyr) × o2_inhibition

  ferm_scale = 1 + (HIF_MAX_FERM − 1) × hif1a_activity

Stoichiometry
-------------
  pyruvate -= v_ferm
  lactate  += v_ferm
  (no ATP change — fermentation is ATP-neutral at this step)
"""

from constants import (
    VMAX_FERM, KM_FERM_PYR, KM_FERM_O2_INH, HIF_MAX_FERM,
)
from helpers import mm
import numpy as np


def compute(s, dt, v_oxphos):
    """
    v_oxphos is passed in so fermentation and OxPhos share pyruvate fairly.
    """
    ferm_scale    = 1.0 + (HIF_MAX_FERM - 1.0) * s["hif1a"]
    o2_inhibition = 1.0 - mm(s["O2"], KM_FERM_O2_INH)

    v = VMAX_FERM * ferm_scale * mm(s["pyruvate"], KM_FERM_PYR) * o2_inhibition * dt
    # Pyruvate remaining after OxPhos
    v = np.minimum(v, np.maximum(s["pyruvate"] - v_oxphos, 0.0))
    return {"v_ferm": v}


def apply(s, fluxes):
    v = fluxes["v_ferm"]
    s["pyruvate"] -= v
    s["lactate"]  += v
    return s
