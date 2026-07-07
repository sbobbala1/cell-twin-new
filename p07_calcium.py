"""
p07_calcium.py — Process 7: Calcium signalling
===============================================
Cytosolic Ca2+ is kept near 100 nM at rest by SERCA (ER pump) and PMCA
(plasma membrane pump). A constant passive leak from ER / extracellular space
opposes the pumps. The net result is a tight homeostatic clamp around CA_REST.

In a future version, a Ca2+ spike (triggered by IP3) would transiently raise
[Ca2+] 100×, activating calmodulin and downstream kinases — giving the AR/VR
demo a visible signalling event to trigger interactively.

Equations
---------
  v_leak = CA_LEAK_RATE × dt          (passive influx, constant)
  v_pump = CA_PUMP_RATE × ([Ca] − CA_REST) × dt   (active efflux)

Stoichiometry
-------------
  Ca_cyt += v_leak − v_pump
"""

from constants import CA_LEAK_RATE, CA_PUMP_RATE, CA_REST
import numpy as np


def compute(s, dt):
    v_leak = CA_LEAK_RATE * dt
    v_pump = CA_PUMP_RATE * np.maximum(s["Ca_cyt"] - CA_REST, 0.0) * dt
    v_pump = np.minimum(v_pump, s["Ca_cyt"])
    return {"v_ca_leak": v_leak, "v_ca_pump": v_pump}


def apply(s, fluxes):
    s["Ca_cyt"] += fluxes["v_ca_leak"] - fluxes["v_ca_pump"]
    s["Ca_cyt"]  = np.maximum(s["Ca_cyt"], 0.0)
    return s
