"""Processing for Query Locality experiment (Part 2).

Aggregates measurements and computes statistics for visualization.
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
    k: str  # Empty string for Lookup
    query_type: str
    pattern: str
    avg_per_query_ns: float
    std_per_query_ns: float
    stderr_per_query_ns: float
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
            "query_type": "category",
            "pattern": "category",
            "trial": "int64",
            "total_time_ns": "int64",
            "query_count": "int64",
        },
    )

    # Fill empty k values with "-" for Lookup
    df["k"] = df["k"].fillna("-")

    # Compute per-query time
    print("Computing per-query times...")
    df["time_per_query_ns"] = df["total_time_ns"] / df["query_count"]

    # Group and aggregate
    print("Aggregating across trials...")
    grouped = (
        df.groupby(["implementation", "k", "query_type", "pattern"], observed=True)[
            "time_per_query_ns"
        ]
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
                query_type=row["query_type"],
                pattern=row["pattern"],
                avg_per_query_ns=row["mean"],
                std_per_query_ns=row["std"] if not np.isnan(row["std"]) else 0.0,
                stderr_per_query_ns=row["stderr"] if not np.isnan(row["stderr"]) else 0.0,
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
                "query_type",
                "pattern",
                "avg_time_per_query_ns",
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
                    "query_type": agg.query_type,
                    "pattern": agg.pattern,
                    "avg_time_per_query_ns": agg.avg_per_query_ns,
                    "std_ns": agg.std_per_query_ns,
                    "stderr_ns": agg.stderr_per_query_ns,
                    "trials": agg.trial_count,
                }
            )

    print(f"Wrote {len(data)} rows.")
