"""
helpers.py — shared kinetic math used by every process module.
Works with scalar floats and NumPy arrays.
"""

import numpy as np

def clamp(x, lo, hi):
    """Clamp x to [lo, hi]."""
    return np.clip(x, lo, hi)

def mm(conc, km):
    """Michaelis-Menten saturation: conc / (Km + conc)."""
    return conc / (km + conc)

def hill(conc, km, n):
    """Hill equation: conc^n / (Km^n + conc^n)."""
    cn = conc ** n
    return cn / (km ** n + cn)
