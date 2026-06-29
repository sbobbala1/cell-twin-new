"""
helpers.py — shared kinetic math used by every process module.
"""

def clamp(x, lo, hi):
    """Clamp x to [lo, hi]."""
    return max(lo, min(hi, x))

def mm(conc, km):
    """Michaelis-Menten saturation: conc / (Km + conc)."""
    return conc / (km + conc)

def hill(conc, km, n):
    """Hill equation: conc^n / (Km^n + conc^n)."""
    cn = conc ** n
    return cn / (km ** n + cn)