"""
simulate.py — main simulation loop
===================================
Imports all 9 process modules, runs them in order each time step,
and records history for plotting and validation.

Process order matters:
  1. p06_hif1a   — must run first (gates p01 and p04)
  2. p01_transport
  3. p02_glycolysis
  4. p03_oxphos
  5. p04_fermentation  (needs v_oxphos from p03 to share pyruvate)
  6. p05_atp_demand
  7. p07_calcium
  8. p08_mtor
  9. p09_nakpump

Run this file directly: python simulate.py
"""

import numpy as np
from constants import DT, DURATION, PRINT_EVERY
from state import initial_state
from helpers import clamp

import p06_hif1a
import p01_transport
import p02_glycolysis
import p03_oxphos
import p04_fermentation
import p05_atp_demand
import p07_calcium
import p08_mtor
import p09_nakpump


def _is_voxel_state(state):
    return np.ndim(next(iter(state.values()))) > 0


def _mean(value):
    return float(np.mean(value))


# ─────────────────────────────────────────────
# SCENARIO CONTROLLER
# Modify this to design new experiments.
# ─────────────────────────────────────────────
def get_scenario_params(t, scenario="hypoxia"):
    """
    Returns time-varying external parameters.

    Scenarios
    ---------
    'normal'     : normoxia throughout
    'hypoxia'    : O2 cut at t=5 min, restored at t=20 min
    'starvation' : glucose cut at t=5 min
    """
    params = {
        "O2_ext":        0.03,   # extracellular O2 (mM)
        "glucose_ext":   5.0,    # extracellular glucose (mM)
        "pump_activity": 1.0,    # Na+/K+ pump scaling (0=blocked, 1=normal)
    }
    if scenario == "hypoxia":
        if 5.0 <= t < 20.0:
            params["O2_ext"] = 0.001   # severe hypoxia (~0.5 mmHg)
    elif scenario == "starvation":
        if t >= 5.0:
            params["glucose_ext"] = 0.0
    return params


# ─────────────────────────────────────────────
# SINGLE STEP
# ─────────────────────────────────────────────
def step(s, dt, t, scenario):
    """Run one time step. Returns updated state."""
    s = dict(s)
    params = get_scenario_params(t, scenario)

    # Clamp negatives before computing fluxes
    for k, v in s.items():
        if k != "hif1a":
            s[k] = np.maximum(v, 0.0)

    # ── P6 first — gates transport and fermentation ──
    f6  = p06_hif1a.compute(s, dt)
    s   = p06_hif1a.apply(s, f6)

    # ── Substrate inputs ──
    f1  = p01_transport.compute(s, dt, params)
    s   = p01_transport.apply(s, f1)

    # ── Energy conversion ──
    f2  = p02_glycolysis.compute(s, dt)
    s   = p02_glycolysis.apply(s, f2)

    f3  = p03_oxphos.compute(s, dt)
    s   = p03_oxphos.apply(s, f3)

    f4  = p04_fermentation.compute(s, dt, f3["v_oxphos"])   # shares pyruvate with p03
    s   = p04_fermentation.apply(s, f4)

    # ── ATP consumers ──
    f5  = p05_atp_demand.compute(s, dt)
    s   = p05_atp_demand.apply(s, f5)

    f7  = p07_calcium.compute(s, dt)
    s   = p07_calcium.apply(s, f7)

    f8  = p08_mtor.compute(s, dt)
    s   = p08_mtor.apply(s, f8)

    f9  = p09_nakpump.compute(s, dt, params["pump_activity"])
    s   = p09_nakpump.apply(s, f9)

    # Final clamps
    for k in s:
        if k != "hif1a":
            s[k] = np.maximum(s[k], 0.0)
    s["ATP"] = clamp(s["ATP"], 0.0, 8.0)
    s["ADP"] = clamp(s["ADP"], 0.0, 5.0)

    return s


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
def run(scenario="hypoxia", duration=DURATION, dt=DT, voxel_shape=None, spatial=False, return_state=False):
    state = initial_state(shape=voxel_shape, spatial=spatial)
    steps = int(duration / dt)
    times = np.linspace(0, duration, steps)
    keys  = list(state.keys())
    voxel_mode = _is_voxel_state(state)
    history = {k: np.zeros(steps) for k in keys}
    """
    history = {
        "ATP": [0, 0, 0, ...],    # cytosolic ATP — homeostatic target
        "ADP": [0, 0, 0, ...],    # cytosolic ADP
        "AMP": [0, 0, 0, ...],    # adenylate pool remainder
        ... (more keys)
    }
    """

    for i in range(steps):
        t = i * dt
        for k in keys:
            history[k][i] = _mean(state[k]) if voxel_mode else state[k]
        state = step(state, dt, t, scenario)
        if i % PRINT_EVERY == 0:
            print(f"  t={t:6.2f} min | ATP={_mean(state['ATP']):.3f} | "
                  f"O2={_mean(state['O2']):.4f} | lac={_mean(state['lactate']):.3f} | "
                  f"HIF={_mean(state['hif1a']):.3f} | Na_cyt={_mean(state['Na_cyt']):.2f}")

    if return_state:
        return times, history, state
    return times, history


def run_3d(scenario="hypoxia", shape=(12, 12, 12), duration=DURATION, dt=DT):
    return run(
        scenario=scenario,
        duration=duration,
        dt=dt,
        voxel_shape=shape,
        spatial=True,
        return_state=True,
    )


if __name__ == "__main__":
    print("Running hypoxia scenario...")
    times, h = run(scenario="hypoxia")
    print("Done. Run validate.py to check results, plot.py to visualise.")
