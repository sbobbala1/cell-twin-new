"""
p02_glycolysis.py — Process 2: Glycolysis
==========================================
Breaks glucose into pyruvate. Produces 2 ATP net per glucose.
Requires no oxygen. Rate is ADP-activated (product demand coupling —
more ADP means more glycolysis, mimicking PFK allosteric regulation).

Equations
---------
  v_glyc = Vmax_glyc × mm([Glc], Km_glc) × mm([ADP], Km_adp)

Stoichiometry
-------------
  glucose  -= v_glyc
  pyruvate += PYR_PER_GLYC × v_glyc    (2 pyruvate per glucose)
  ATP      += ATP_PER_GLYC  × v_glyc   (net +2 ATP per glucose)
  ADP      -= ATP_PER_GLYC  × v_glyc
"""

from constants import (
    VMAX_GLYC, KM_GLYC_GLU, KM_GLYC_ADP,
    ATP_PER_GLYC, PYR_PER_GLYC,
)
from helpers import mm
import numpy as np


def compute(s, dt):
    v_glyc = VMAX_GLYC * mm(s["glucose"], KM_GLYC_GLU) * mm(s["ADP"], KM_GLYC_ADP) * dt
    v_glyc = np.minimum(v_glyc, s["glucose"])   # can't consume more glucose than available
    v_glyc = np.minimum(v_glyc, s["ADP"] / ATP_PER_GLYC)   # ATP production is ADP-limited
    return {"v_glyc": v_glyc}


def apply(s, fluxes):
    v = fluxes["v_glyc"]
    s["glucose"]  -= v
    s["pyruvate"] += PYR_PER_GLYC * v
    s["ATP"]      += ATP_PER_GLYC * v
    s["ADP"]      -= ATP_PER_GLYC * v
    return s
