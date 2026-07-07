"""
p09_nakpump.py — Process 9: Na+/K+-ATPase pump
===============================================
The Na+/K+-ATPase is the single largest ATP consumer in most mammalian cells
(20–30% of total ATP turnover). It pumps 3 Na+ out and 2 K+ in per ATP,
maintaining the resting membrane potential of ~−70 mV.

When ATP falls during hypoxia, pump slows → Na+ floods in osmotically →
cell swells (cytotoxic oedema). This gives the AR/VR simulation a physically
distinct visual failure mode: the cell visibly swells as Na_cyt rises.

The pump uses Hill kinetics because Na+ (n=3) and K+ (n=2) bind
cooperatively to distinct sites on the alpha subunit.

Equations
---------
  v_pump = Vmax × pump_activity × mm(ATP) × Hill(Na_cyt, Km_Na, 3) × Hill(K_ext, Km_K, 2)
  v_actual = min(v_pump, [ATP]/1, [Na_cyt]/3, [K_ext]/2)

Stoichiometry
-------------
  1 ATP  +  3 Na+_cyt  +  2 K+_ext  →  1 ADP  +  3 Na+_ext  +  2 K+_cyt
  ATP    -= v_actual × 1
  ADP    += v_actual × 1
  Na_cyt -= v_actual × 3
  Na_ext += v_actual × 3
  K_ext  -= v_actual × 2
  K_cyt  += v_actual × 2
"""

from constants import VMAX_PUMP, KM_ATP_PUMP, KM_NA, KM_K
from helpers import mm, hill
import numpy as np


def compute(s, dt, pump_activity=1.0):
    atp_drive = mm(s["ATP"],    KM_ATP_PUMP)
    na_drive  = hill(s["Na_cyt"], KM_NA, 3)
    k_drive   = hill(s["K_ext"],  KM_K,  2)

    v = VMAX_PUMP * pump_activity * atp_drive * na_drive * k_drive * dt
    v = np.minimum.reduce([
        v,
        s["ATP"],
        s["Na_cyt"] / 3.0,
        s["K_ext"]  / 2.0,
    ])
    return {"v_pump": v}


def apply(s, fluxes):
    v = fluxes["v_pump"]
    s["ATP"]    -= v
    s["ADP"]    += v
    s["Na_cyt"] -= 3.0 * v
    s["Na_ext"] += 3.0 * v
    s["K_ext"]  -= 2.0 * v
    s["K_cyt"]  += 2.0 * v
    return s
