"""
plot.py — time-series visualisation
=====================================
Run: python plot.py
Outputs: cell_simulation.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from simulate import run


def plot(scenario="hypoxia", label="Hypoxia (O₂ cut t=5–20 min)"):
    times, h = run(scenario=scenario)

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(f"Human Cell Digital Twin — {label}", fontsize=14, fontweight="bold")
    gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38)

    def shade(ax):
        if scenario == "hypoxia":
            ax.axvspan(5, 20, alpha=0.07, color="red")
            ymax = ax.get_ylim()[1]
            ax.text(12.5, ymax * 0.92, "hypoxia", fontsize=7, ha="center", color="red", alpha=0.7)

    sty = dict(linewidth=1.8)

    panels = [
        (gs[0, 0], "ATP (mM)",           h["ATP"],          "#1a7abf"),
        (gs[0, 1], "O₂ (mM)",            h["O2"],            "#2ca02c"),
        (gs[0, 2], "Lactate (mM)",       h["lactate"],       "#d62728"),
        (gs[1, 0], "HIF-1α (a.u.)",      h["hif1a"],         "#9467bd"),
        (gs[1, 1], "Pyruvate (mM)",      h["pyruvate"],      "#ff7f0e"),
        (gs[1, 2], "Glucose (mM)",       h["glucose"],       "#8c564b"),
        (gs[2, 0], "Na⁺ cyt (mM)",       h["Na_cyt"],        "#e377c2"),
        (gs[2, 1], "Protein mass (mM)", h["protein_mass"],  "#17becf"),
        (gs[2, 2], "ADP (mM)",           h["ADP"],           "#bcbd22"),
    ]

    for spec, title, data, color in panels:
        ax = fig.add_subplot(spec)
        ax.plot(times, data, color=color, **sty)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("time (min)", fontsize=8)
        ax.tick_params(labelsize=7)
        shade(ax)

    out = "cell_simulation.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close()


if __name__ == "__main__":
    plot()