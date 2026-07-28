"""Processing for Precomputation experiment (Part 2).

Aggregates construction time measurements and computes statistics for visualization.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from common.files import recreate_directory

MEASUREMENTS_PATH = Path(__file__).parent / "generated" / "measurements" / "measurements.csv"


@dataclass
class Aggregate:
    """Aggregated statistics for a single configuration."""

    implementation: str
    k: str  # "-" for Naive and Lookup
    n: int
    avg_construction_ns: float
    std_construction_ns: float
    stderr_construction_ns: float
    trial_count: int


def process() -> None:
    """Main entry point for processing phase."""
    aggregated = read_and_aggregate()
    write_processing_output(aggregated)
    print("Processing complete.")


def read_and_aggregate() -> list[Aggregate]:
    """Read measurements and aggregate across trials."""
    print("Reading measurements...")
    df = pd.read_csv(
        MEASUREMENTS_PATH,
        dtype={
            "implementation": "category",
            "k": "str",
            "n": "int64",
            "trial": "int64",
            "construction_time_ns": "int64",
        },
    )

    # Fill empty k values with "-" for Naive/Lookup
    df["k"] = df["k"].fillna("-")

    # Group and aggregate
    print("Aggregating across trials...")
    grouped = (
        df.groupby(["implementation", "k", "n"], observed=True)["construction_time_ns"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    grouped["stderr"] = grouped["std"] / np.sqrt(grouped["count"])

    # Convert to list of Aggregate objects
    results = []
    for _, row in grouped.iterrows():
        results.append(
            Aggregate(
                implementation=row["implementation"],
                k=row["k"],
                n=int(row["n"]),
                avg_construction_ns=row["mean"],
                std_construction_ns=row["std"] if not np.isnan(row["std"]) else 0.0,
                stderr_construction_ns=row["stderr"] if not np.isnan(row["stderr"]) else 0.0,
                trial_count=int(row["count"]),
            )
        )

    print(f"Aggregated {len(results)} configurations.")
    return results


def write_processing_output(data: list[Aggregate]) -> None:
    """Write aggregated data to CSV."""
    processing_dir = Path(__file__).parent / "generated" / "processed"
    recreate_directory(processing_dir)

    output_path = processing_dir / "processed.csv"
    print(f"Writing to {output_path}...")

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "implementation",
                "k",
                "n",
                "avg_construction_ns",
                "std_ns",
                "stderr_ns",
                "trials",
            ],
        )
        writer.writeheader()

        for agg in data:
            writer.writerow(
                {
                    "implementation": agg.implementation,
                    "k": agg.k,
                    "n": agg.n,
                    "avg_construction_ns": agg.avg_construction_ns,
                    "std_ns": agg.std_construction_ns,
                    "stderr_ns": agg.stderr_construction_ns,
                    "trials": agg.trial_count,
                }
            )

    print(f"Wrote {len(data)} rows.")
