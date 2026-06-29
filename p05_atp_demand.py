"""
p05_atp_demand.py — Process 5: Baseline ATP demand
===================================================
Represents all housekeeping ATP consumption not modelled explicitly —
cytoskeletal dynamics, vesicle trafficking, DNA repair, etc.
Scales with ATP availability (cells slow housekeeping when ATP is low).

Equation
--------
  v_demand = ATP_demand_base × mm([ATP], Km_demand)

Stoichiometry
-------------
  ATP -= v_demand
  ADP += v_demand
"""

from constants import ATP_DEMAND_BASE, KM_DEMAND_ATP
from helpers import mm


def compute(s, dt):
    v = ATP_DEMAND_BASE * mm(s["ATP"], KM_DEMAND_ATP) * dt
    v = min(v, s["ATP"])
    return {"v_demand": v}


def apply(s, fluxes):
    v = fluxes["v_demand"]
    s["ATP"] -= v
    s["ADP"] += v
    return s