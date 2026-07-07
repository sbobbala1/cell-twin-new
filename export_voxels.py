"""
export_voxels.py — export 3D voxel simulation state for WebGL / Unity.

Run:
  python export_voxels.py
  python export_voxels.py --shape 22,22,22 --scenario hypoxia --format json
"""

import argparse
import json
import os
from datetime import datetime, timezone

import numpy as np

from constants import DT, DURATION
from simulate import run_3d


DEFAULT_FIELDS = [
    "ATP",
    "ADP",
    "AMP",
    "glucose",
    "pyruvate",
    "lactate",
    "O2",
    "amino_acids",
    "protein_mass",
    "Na_cyt",
    "hif1a",
    "Ca_cyt",
]


def parse_shape(value):
    shape = tuple(int(part.strip()) for part in value.split(","))
    if len(shape) != 3 or any(size <= 0 for size in shape):
        raise argparse.ArgumentTypeError("shape must be three positive integers, like 22,22,22")
    return shape


def parse_fields(value):
    return [field.strip() for field in value.split(",") if field.strip()]


def voxel_positions(shape):
    z, y, x = np.indices(shape)
    return np.stack([x.ravel(), y.ravel(), z.ravel()], axis=1)


def flatten_fields(state, fields):
    missing = [field for field in fields if field not in state]
    if missing:
        raise SystemExit(f"Unknown field(s): {', '.join(missing)}")
    return {field: np.asarray(state[field], dtype=float).ravel() for field in fields}


def field_stats(flat_fields):
    stats = {}
    for field, values in flat_fields.items():
        stats[field] = {
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "mean": float(np.mean(values)),
        }
    return stats


def build_payload(scenario, shape, duration, dt, fields, final_state, include_positions):
    flat_fields = flatten_fields(final_state, fields)
    metadata = {
        "project": "human-cell-digital-twin",
        "scenario": scenario,
        "shape_zyx": list(shape),
        "voxel_count": int(np.prod(shape)),
        "duration_min": duration,
        "dt_min": dt,
        "voxel_order": "C-order z,y,x; index = (z * y_size + y) * x_size + x",
        "field_units": {
            "ATP": "mM",
            "ADP": "mM",
            "AMP": "mM",
            "glucose": "mM",
            "pyruvate": "mM",
            "lactate": "mM",
            "O2": "mM",
            "amino_acids": "mM",
            "protein_mass": "mM equivalent",
            "Na_cyt": "mM",
            "hif1a": "a.u.",
            "Ca_cyt": "mM",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    payload = {
        "metadata": metadata,
        "stats": field_stats(flat_fields),
        "fields": {field: values.tolist() for field, values in flat_fields.items()},
    }
    if include_positions:
        payload["positions_xyz"] = voxel_positions(shape).astype(int).tolist()
    return payload


def export_json(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))


def export_npz(path, scenario, shape, duration, dt, fields, final_state, include_positions):
    flat_fields = flatten_fields(final_state, fields)
    arrays = {
        "shape_zyx": np.array(shape, dtype=np.int32),
        "duration_min": np.array(duration, dtype=float),
        "dt_min": np.array(dt, dtype=float),
        "scenario": np.array(scenario),
        "fields": np.array(fields),
    }
    arrays.update(flat_fields)
    if include_positions:
        arrays["positions_xyz"] = voxel_positions(shape).astype(np.int16)
    np.savez_compressed(path, **arrays)


def main():
    parser = argparse.ArgumentParser(description="Export voxel state for WebGL or Unity.")
    parser.add_argument("--shape", type=parse_shape, default=(22, 22, 22), help="voxel shape as z,y,x")
    parser.add_argument("--scenario", default="hypoxia", choices=["normal", "hypoxia", "starvation"])
    parser.add_argument("--duration", type=float, default=DURATION)
    parser.add_argument("--dt", type=float, default=DT)
    parser.add_argument("--format", choices=["json", "npz"], default="json")
    parser.add_argument("--fields", type=parse_fields, default=DEFAULT_FIELDS,
                        help="comma-separated fields to export")
    parser.add_argument("--positions", action="store_true", help="include x,y,z voxel positions")
    parser.add_argument("--out", default=None, help="output file path")
    args = parser.parse_args()

    if args.duration <= 0 or args.dt <= 0:
        raise SystemExit("--duration and --dt must be positive")

    print(f"Running {args.scenario} voxel backend: shape={args.shape}, duration={args.duration:g} min")
    _, _, final_state = run_3d(
        scenario=args.scenario,
        shape=args.shape,
        duration=args.duration,
        dt=args.dt,
    )

    os.makedirs("output/voxels", exist_ok=True)
    if args.out is None:
        shape_name = "x".join(str(size) for size in args.shape)
        args.out = os.path.join("output", "voxels", f"{args.scenario}_{shape_name}.{args.format}")

    if args.format == "json":
        payload = build_payload(
            args.scenario,
            args.shape,
            args.duration,
            args.dt,
            args.fields,
            final_state,
            args.positions,
        )
        export_json(args.out, payload)
    else:
        export_npz(
            args.out,
            args.scenario,
            args.shape,
            args.duration,
            args.dt,
            args.fields,
            final_state,
            args.positions,
        )

    print(f"Saved -> {args.out}")


if __name__ == "__main__":
    main()
