"""Visualization for Precomputation experiment (Part 2).

Creates log-log plot of construction time vs input size for each implementation.
"""

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt

from common.files import recreate_directory

DATA_PATH = Path(__file__).parent / "generated" / "processed" / "processed.csv"
OUTPUT_DIR = Path(__file__).parent / "generated" / "plots"

# Line styles and colors for each implementation variant
STYLES = {
    "Naive": {"color": "#e41a1c", "marker": "o", "linestyle": "-"},
    "Lookup": {"color": "#377eb8", "marker": "s", "linestyle": "-"},
    "SpaceEfficient-k1": {"color": "#4daf4a", "marker": "^", "linestyle": "-"},
    "SpaceEfficient-k4": {"color": "#984ea3", "marker": "v", "linestyle": "--"},
    "SpaceEfficient-k16": {"color": "#ff7f00", "marker": "D", "linestyle": ":"},
}


@dataclass
class DataPoint:
    """A single data point for plotting."""

    n: int
    avg_construction_ns: float
    stderr_construction_ns: float


def read_processed_data() -> dict[str, list[DataPoint]]:
    """Read processed data and organize by implementation key.

    Returns:
        Dict mapping impl_key (e.g., "Naive", "SpaceEfficient-k1") to list of DataPoints,
        sorted by n.
    """
    data: dict[str, list[DataPoint]] = defaultdict(list)

    with DATA_PATH.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            impl = row["implementation"]
            k = row["k"]

            # Create implementation key
            impl_key = f"SpaceEfficient-k{k}" if impl == "SpaceEfficient" and k != "-" else impl

            data_point = DataPoint(
                n=int(row["n"]),
                avg_construction_ns=float(row["avg_construction_ns"]),
                stderr_construction_ns=float(row["stderr_ns"]),
            )
            data[impl_key].append(data_point)

    # Sort each list by n
    for impl_key in data:
        data[impl_key].sort(key=lambda dp: dp.n)

    return dict(data)


def visualize() -> None:
    """Create log-log plot of construction time vs input size."""
    print("Reading processed data...")
    data = read_processed_data()

    if not data:
        print("No data found. Run processing phase first.")
        return

    print(f"Found data for implementations: {list(data.keys())}")

    # Create single plot
    fig, ax = plt.subplots(figsize=(10, 6))

    for impl_key, style in STYLES.items():
        if impl_key not in data:
            continue

        impl_data = data[impl_key]
        if not impl_data:
            continue

        ns = [dp.n for dp in impl_data]
        avgs = [dp.avg_construction_ns for dp in impl_data]
        stderrs = [dp.stderr_construction_ns * 1.96 for dp in impl_data]  # 95% CI

        ax.errorbar(
            ns,
            avgs,
            yerr=stderrs,
            label=impl_key,
            color=style["color"],
            marker=style["marker"],
            linestyle=style["linestyle"],
            capsize=3,
            markersize=6,
            linewidth=1.5,
        )

    ax.set_xlabel("Input Size (n)", fontsize=12)
    ax.set_ylabel("Construction Time (ns)", fontsize=12)
    ax.set_title("Precomputation Time vs Input Size", fontsize=14)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.legend(loc="upper left", title="Implementation")
    ax.grid(visible=True, alpha=0.3)

    plt.tight_layout()

    # Save plots
    recreate_directory(OUTPUT_DIR)

    pdf_path = OUTPUT_DIR / "precomputation.pdf"
    svg_path = OUTPUT_DIR / "precomputation.svg"

    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(svg_path, format="svg", bbox_inches="tight")

    plt.close(fig)

    print("Plots saved to:")
    print(f"  - {pdf_path}")
    print(f"  - {svg_path}")
