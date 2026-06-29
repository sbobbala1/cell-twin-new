"""
constants.py — all kinetic parameters in one place.
Every process module imports from here. Change a value once, it applies everywhere.
"""

# ── Simulation ────────────────────────────────────────────
DT          = 0.001   # time step (minutes)
DURATION    = 30.0    # total run time (minutes)
PRINT_EVERY = 1000    # console heartbeat interval (steps)

# ── P1: Membrane transport ────────────────────────────────
VMAX_GLUT       = 1.2    # max glucose import (mM/min)
KM_GLUT_GLU     = 1.0    # glucose half-sat for GLUT (mM)
VMAX_O2_IMPORT  = 0.5    # max O2 import (mM/min)
KM_O2_EXT       = 0.01   # O2 import half-sat (mM)
O2_EXTERNAL     = 0.03   # normoxic extracellular O2 (~15 mmHg, 0.03 mM)
NA_LEAK_RATE    = 0.08   # passive Na+ leak into cytosol (mM/min)

# ── P2: Glycolysis ────────────────────────────────────────
VMAX_GLYC       = 2.5    # max glycolytic flux (mM/min)
KM_GLYC_GLU     = 0.5    # glucose half-sat (mM)
KM_GLYC_ADP     = 0.3    # ADP activation of PFK (mM)
ATP_PER_GLYC    = 2.0    # net ATP produced per glucose
PYR_PER_GLYC    = 2.0    # pyruvate produced per glucose

# ── P3: Oxidative phosphorylation ─────────────────────────
VMAX_OXPHOS     = 1.0    # max OxPhos rate (mM/min)
KM_OXPHOS_PYR   = 0.1    # pyruvate half-sat (mM)
KM_OXPHOS_O2    = 0.005  # O2 half-sat — cytochrome c oxidase Km ~0.5 µM
ATP_PER_OXPHOS  = 30.0   # net ATP per pyruvate oxidised
O2_PER_OXPHOS   = 3.0    # O2 consumed per pyruvate

# ── P4: Fermentation ──────────────────────────────────────
VMAX_FERM       = 2.0    # max fermentation rate (mM/min)
KM_FERM_PYR     = 0.2    # pyruvate half-sat (mM)
KM_FERM_O2_INH  = 0.01   # O2 at which fermentation is half-inhibited (Pasteur)

# ── P5: Baseline ATP demand ───────────────────────────────
ATP_DEMAND_BASE = 4.0    # housekeeping ATPase rate (mM/min)
KM_DEMAND_ATP   = 0.5    # half-sat for demand (mM)

# ── P6: HIF-1α signalling ─────────────────────────────────
HIF_RISE_RATE   = 1.0    # HIF-1α activation rate when O2 low (1/min)
HIF_FALL_RATE   = 0.5    # HIF-1α deactivation rate when O2 returns (1/min)
HIF_O2_THRESH   = 0.01   # O2 threshold for HIF-1α stabilisation (mM, ~5 mmHg)
HIF_MAX_GLUT    = 3.0    # max GLUT upregulation fold by HIF-1α
HIF_MAX_FERM    = 2.5    # max fermentation upregulation fold by HIF-1α

# ── P7: Calcium signalling ────────────────────────────────
CA_LEAK_RATE    = 0.001  # resting Ca2+ leak into cytosol (mM/min)
CA_PUMP_RATE    = 10.0   # SERCA/PMCA pump rate (1/min)
CA_REST         = 0.0001 # resting cytosolic Ca2+ target (mM = 100 nM)

# ── P8: mTOR / protein synthesis ──────────────────────────
VMAX_RIBO       = 2.0    # max ribosomal synthesis rate (mM/min)
KM_ATP_RIBO     = 0.5    # ATP half-sat for ribosomes (mM)
KM_AA           = 0.1    # amino acid half-sat (mM)
ATP_PER_AA      = 4.0    # ATP cost per peptide bond
NORMAL_ATP      = 4.0    # homeostatic ATP reference (mM)

# ── P9: Na+/K+-ATPase ─────────────────────────────────────
VMAX_PUMP       = 3.0    # max pump velocity (mM/min)
KM_ATP_PUMP     = 0.5    # ATP half-sat for pump (mM)
KM_NA           = 10.0   # cytosolic Na+ half-sat (mM)
KM_K            = 1.5    # extracellular K+ half-sat (mM)