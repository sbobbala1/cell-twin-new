"""
p01_transport.py — Process 1: Membrane transport
=================================================
Glucose exchange via reversible GLUT transporters.
O2 import via passive diffusion.
Passive Na+ leak (drives Na+/K+ pump in p09).

Equations
---------
  v_glut = Vmax_glut × glut_scale × (mm([Glc_ext]) - mm([Glc_cyt]))
  v_o2   = Vmax_o2   × [O2_ext]  / (Km_o2   + [O2_ext])
  v_na   = Na_leak_rate   (constant passive leak)

  glut_scale = 1 + (HIF_MAX_GLUT − 1) × hif1a_activity
  (HIF-1α upregulates GLUT 1 → 3× under hypoxia)

Stoichiometry
-------------
  glucose_cyt  += v_glut    (positive = import, negative = export)
  O2_cyt       += v_o2
  Na_cyt       += v_na    (Na+ leaks in)
  Na_ext       -= v_na
"""

from constants import (
    VMAX_GLUT, KM_GLUT_GLU,
    VMAX_O2_IMPORT, KM_O2_EXT,
    NA_LEAK_RATE, HIF_MAX_GLUT,
)
from helpers import mm
import numpy as np


def compute(s, dt, params):
    """
    Parameters
    ----------
    s      : state dict
    dt     : time step (minutes)
    params : scenario dict with keys 'glucose_ext', 'O2_ext'

    Returns
    -------
    fluxes : dict of (flux_name -> value) — NOT yet applied to state.
    """
    hif       = s["hif1a"]
    glut_scale = 1.0 + (HIF_MAX_GLUT - 1.0) * hif

    ext_drive = mm(params["glucose_ext"], KM_GLUT_GLU)
    cyt_drive = mm(s["glucose"], KM_GLUT_GLU)
    v_glut = VMAX_GLUT * glut_scale * (ext_drive - cyt_drive) * dt
    # GLUT is reversible: positive flux imports, negative flux exports.
    v_glut = np.minimum(v_glut, np.maximum(params["glucose_ext"], 0.0))
    v_glut = np.maximum(v_glut, -s["glucose"])

    v_o2   = VMAX_O2_IMPORT * mm(params["O2_ext"], KM_O2_EXT) * dt

    v_na   = NA_LEAK_RATE * dt

    return {
        "v_glut": v_glut,
        "v_o2":   v_o2,
        "v_na_leak": v_na,
    }


def apply(s, fluxes):
    """Commit transport fluxes to state."""
    s["glucose"] += fluxes["v_glut"]
    s["O2"]      += fluxes["v_o2"]
    s["Na_cyt"]  += fluxes["v_na_leak"]
    s["Na_ext"]  -= fluxes["v_na_leak"]
    return s
