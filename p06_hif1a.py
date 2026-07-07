"""
p06_hif1a.py — Process 6: HIF-1α oxygen sensing
=================================================
HIF-1α (Hypoxia-Inducible Factor 1-alpha) is the master hypoxia switch.
Under normoxia, prolyl hydroxylases (PHDs) continuously tag HIF-1α for
proteasomal degradation — it stays near zero.
Under hypoxia (O2 < ~5 mmHg), PHDs stall, HIF-1α accumulates and enters
the nucleus, where it transcribes genes for GLUT1/3 transporters,
glycolytic enzymes, and VEGF (angiogenesis).

This is what makes the parameters coupled: you cannot have low O2 without
eventually getting upregulated glucose import and fermentation capacity.

Equations
---------
  If O2 < HIF_O2_THRESH:   dHIF/dt =  k_rise × (1 − HIF)   [activation]
  Else:                      dHIF/dt = −k_fall × HIF          [degradation]
  HIF is clamped to [0, 1].

Downstream effects (used by p01 and p04):
  glut_scale = 1 + (HIF_MAX_GLUT − 1) × hif1a
  ferm_scale = 1 + (HIF_MAX_FERM − 1) × hif1a

NOTE: This module must be called FIRST each step because its output
(hif1a) gates p01 and p04.
"""

from constants import HIF_RISE_RATE, HIF_FALL_RATE, HIF_O2_THRESH
from helpers import clamp
import numpy as np


def compute(s, dt):
    low_o2 = s["O2"] < HIF_O2_THRESH
    rise = HIF_RISE_RATE * (1.0 - s["hif1a"]) * dt
    fall = -HIF_FALL_RATE * s["hif1a"] * dt
    delta = np.where(low_o2, rise, fall)
    new_hif = clamp(s["hif1a"] + delta, 0.0, 1.0)
    return {"hif1a": new_hif}


def apply(s, fluxes):
    s["hif1a"] = fluxes["hif1a"]
    return s
