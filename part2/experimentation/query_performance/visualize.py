"""Visualization for Query Performance experiment (Part 2).

Creates plots comparing query performance across implementations and input sizes.
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
    avg_per_query_ns: float
    stderr_per_query_ns: float


def read_processed_data() -> dict[str, dict[str, list[DataPoint]]]:
    """Read processed data and organize by implementation key and query type.

    Returns:
        Nested dict: {impl_key: {query_type: [DataPoint, ...]}}
        where impl_key is like "Naive", "Lookup", "SpaceEfficient-k1", etc.
    """
    # Structure: {impl_key: {query_type: [DataPoint, ...]}}
    data: dict[str, dict[str, list[DataPoint]]] = defaultdict(lambda: defaultdict(list))

    with DATA_PATH.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            impl = row["implementation"]
            k = row["k"]
            query_type = row["query_type"]

            # Create implementation key
            impl_key = f"SpaceEfficient-k{k}" if impl == "SpaceEfficient" and k != "-" else impl

            data_point = DataPoint(
                n=int(row["n"]),
                avg_per_query_ns=float(row["avg_time_per_query_ns"]),
                stderr_per_query_ns=float(row["stderr_ns"]),
            )
            data[impl_key][query_type].append(data_point)

    # Sort each list by n
    for impl_key in data:
        for query_type in data[impl_key]:
            data[impl_key][query_type].sort(key=lambda dp: dp.n)

    return dict(data)


def plot_query_type(
    ax: plt.Axes,
    data: dict[str, dict[str, list[DataPoint]]],
    query_type: str,
    title: str,
) -> None:
    """Plot query performance for a specific query type.

    Args:
        ax: Matplotlib axes to plot on.
        data: Nested data structure from read_processed_data().
        query_type: Either "rank" or "select".
        title: Title for the subplot.
    """
    for impl_key, style in STYLES.items():
        if impl_key not in data or query_type not in data[impl_key]:
            continue

        impl_data = data[impl_key][query_type]
        if not impl_data:
            continue

        ns = [dp.n for dp in impl_data]
        avgs = [dp.avg_per_query_ns for dp in impl_data]
        stderrs = [dp.stderr_per_query_ns * 1.96 for dp in impl_data]  # 95% CI

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
    ax.set_ylabel("Time per Query (ns)", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.legend(loc="upper left")
    ax.grid(visible=True, alpha=0.3)


def visualize() -> None:
    """Create plots comparing query performance across implementations."""
    print("Reading processed data...")
    data = read_processed_data()

    if not data:
        print("No data found. Run processing phase first.")
        return

    print(f"Found data for implementations: {list(data.keys())}")

    # Create 1x2 grid: Rank on left, Select on right
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    plot_query_type(axes[0], data, "rank", "RANK Query Time vs Input Size")
    plot_query_type(axes[1], data, "select", "SELECT Query Time vs Input Size")

    plt.tight_layout()

    # Save plots
    recreate_directory(OUTPUT_DIR)

    pdf_path = OUTPUT_DIR / "query_performance.pdf"
    svg_path = OUTPUT_DIR / "query_performance.svg"

    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(svg_path, format="svg", bbox_inches="tight")

    plt.close(fig)

    print("Plots saved to:")
    print(f"  - {pdf_path}")
    print(f"  - {svg_path}")


if __name__ == "__main__":
    visualize()
