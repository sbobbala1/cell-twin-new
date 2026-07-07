"""
plot.py — time-series visualisation
=====================================
Run: python3 plot.py
Outputs: cell_simulation.png
"""

import os
import sys
import argparse

os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.path.dirname(__file__), ".matplotlib"))

try:
    import matplotlib
except ModuleNotFoundError as exc:
    if exc.name != "matplotlib":
        raise
    print(
        "Missing dependency: matplotlib\n"
        "Run this from the project folder instead:\n"
        "  .venv/bin/python plot.py\n\n"
        "Or install the project requirements into your active Python:\n"
        "  python3 -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from simulate import run, run_3d


def plot(scenario="hypoxia", label="Hypoxia (O₂ cut t=5–20 min)", duration=30.0):
    times, h = run(scenario=scenario, duration=duration)

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


def plot_3d(scenario="hypoxia", shape=(12, 12, 12), duration=30.0):
    times, h, final_state = run_3d(scenario=scenario, shape=shape, duration=duration)

    o2 = final_state["O2"]
    atp = final_state["ATP"]
    hif = final_state["hif1a"]
    z, y, x = np.indices(shape)

    colors = hif.ravel()
    sizes = 18.0 + 32.0 * (atp.ravel() / max(float(atp.max()), 1e-9))

    fig = plt.figure(figsize=(14, 8))
    fig.suptitle(f"Human Cell Digital Twin — 3D voxel snapshot ({scenario}, t={times[-1]:.1f} min)",
                 fontsize=13, fontweight="bold")

    ax = fig.add_subplot(1, 2, 1, projection="3d")
    sc = ax.scatter(x.ravel(), y.ravel(), z.ravel(), c=colors, s=sizes, cmap="magma", alpha=0.72)
    ax.set_title("HIF-1α voxel activation")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_box_aspect(shape[::-1])
    fig.colorbar(sc, ax=ax, shrink=0.72, label="HIF-1α")

    ax2 = fig.add_subplot(1, 2, 2)
    mid_z = shape[0] // 2
    im = ax2.imshow(o2[mid_z], cmap="viridis", origin="lower")
    ax2.set_title(f"O₂ middle slice z={mid_z}")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    fig.colorbar(im, ax=ax2, shrink=0.82, label="O₂ (mM)")

    out = "cell_simulation_3d.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot the human cell digital twin simulation.")
    parser.add_argument("--3d", action="store_true", dest="plot_3d", help="save a voxel snapshot")
    parser.add_argument("--scenario", default="hypoxia", choices=["normal", "hypoxia", "starvation"])
    parser.add_argument("--shape", default="12,12,12", help="3D voxel shape as z,y,x")
    parser.add_argument("--duration", type=float, default=30.0)
    args = parser.parse_args()

    if args.plot_3d:
        shape = tuple(int(part.strip()) for part in args.shape.split(","))
        if len(shape) != 3:
            raise SystemExit("--shape must have three integers, like 12,12,12")
        plot_3d(scenario=args.scenario, shape=shape, duration=args.duration)
    else:
        labels = {
            "normal": "Normoxia",
            "hypoxia": "Hypoxia (O₂ cut t=5–20 min)",
            "starvation": "Glucose starvation",
        }
        plot(scenario=args.scenario, label=labels[args.scenario], duration=args.duration)


if __name__ == "__main__":
    main()
