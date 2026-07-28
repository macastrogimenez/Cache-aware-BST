"""Visualization for Query Locality experiment (Part 2).

Creates a 2×2 grid of grouped bar charts showing how different query access patterns
affect performance due to CPU cache behavior.
"""

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from common.files import recreate_directory
from part2.experimentation.query_locality.data_generation import COUNT_QUERIES, N

DATA_PATH = Path(__file__).parent / "generated" / "processed" / "processed.csv"
OUTPUT_DIR = Path(__file__).parent / "generated" / "plots"

# Pattern order from best to worst locality
PATTERN_ORDER = ["sequential", "strided64", "strided_large", "random", "adversarial"]

# Labels for x-axis
PATTERN_LABELS = ["Sequential", "Strided\n(64)", "Strided\n(Large)", "Random", "Adversarial"]

# Colors for each pattern
BAR_COLORS = {
    "sequential": "#4daf4a",  # Green - best locality
    "strided64": "#377eb8",  # Blue
    "strided_large": "#ff7f00",  # Orange
    "random": "#e41a1c",  # Red
    "adversarial": "#984ea3",  # Purple - worst locality
}


@dataclass
class PatternData:
    """Data for a single pattern measurement."""

    avg_ns: float
    stderr_ns: float


def read_processed_data() -> dict[tuple[str, str], dict[str, PatternData]]:
    """Read processed data and organize by (implementation, query_type) and pattern.

    Returns:
        Dict mapping (impl, query_type) -> {pattern: PatternData}
    """
    data: dict[tuple[str, str], dict[str, PatternData]] = defaultdict(dict)

    with DATA_PATH.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            impl = row["implementation"]
            query_type = row["query_type"]
            pattern = row["pattern"]

            key = (impl, query_type)
            data[key][pattern] = PatternData(
                avg_ns=float(row["avg_time_per_query_ns"]),
                stderr_ns=float(row["stderr_ns"]),
            )

    return dict(data)


def plot_subplot(
    ax: plt.Axes,
    data: dict[tuple[str, str], dict[str, PatternData]],
    impl: str,
    query_type: str,
    title: str,
) -> None:
    """Plot a single subplot with grouped bars for each pattern.

    Args:
        ax: Matplotlib axes to plot on.
        data: Data structure from read_processed_data().
        impl: Implementation name ("Lookup" or "SpaceEfficient").
        query_type: Either "rank" or "select".
        title: Title for the subplot.
    """
    key = (impl, query_type)
    if key not in data:
        ax.set_title(f"{title}\n(No Data)", fontsize=12)
        ax.set_xticks([])
        return

    pattern_data = data[key]

    x = np.arange(len(PATTERN_ORDER))
    avgs = [pattern_data.get(p, PatternData(0, 0)).avg_ns for p in PATTERN_ORDER]
    stderrs = [
        pattern_data.get(p, PatternData(0, 0)).stderr_ns * 1.96 for p in PATTERN_ORDER
    ]  # 95% CI
    colors = [BAR_COLORS[p] for p in PATTERN_ORDER]

    bars = ax.bar(
        x,
        avgs,
        yerr=stderrs,
        color=colors,
        capsize=4,
        edgecolor="black",
        linewidth=0.5,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(PATTERN_LABELS, fontsize=9)
    ax.set_ylabel("Time per Query (ns)", fontsize=10)
    ax.set_title(title, fontsize=12)
    ax.grid(visible=True, alpha=0.3, axis="y")

    # Add value labels on top of bars
    for bar, avg in zip(bars, avgs):
        if avg > 0:
            height = bar.get_height()
            ax.annotate(
                f"{avg:.1f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )


def visualize() -> None:
    """Create 2×2 grid of bar charts comparing query locality patterns."""
    print("Reading processed data...")
    data = read_processed_data()

    if not data:
        print("No data found. Run processing phase first.")
        return

    print(f"Found data for configurations: {list(data.keys())}")

    # Create 2×2 grid: rows = query_type (rank/select), cols = implementation
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    plot_subplot(axes[0, 0], data, "Lookup", "rank", "RANK - Lookup")
    plot_subplot(axes[0, 1], data, "SpaceEfficient", "rank", "RANK - SpaceEfficient (k=4)")
    plot_subplot(axes[1, 0], data, "Lookup", "select", "SELECT - Lookup")
    plot_subplot(axes[1, 1], data, "SpaceEfficient", "select", "SELECT - SpaceEfficient (k=4)")

    # Add overall title
    fig.suptitle(
        f"Query Locality vs Performance\n(n = {N:,}, queries = {COUNT_QUERIES:,})",
        fontsize=14,
        y=1.02,
    )

    plt.tight_layout()

    # Save plots
    recreate_directory(OUTPUT_DIR)

    pdf_path = OUTPUT_DIR / "query_locality.pdf"
    svg_path = OUTPUT_DIR / "query_locality.svg"

    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(svg_path, format="svg", bbox_inches="tight")

    print(f"Saved plots to {pdf_path} and {svg_path}")

    plt.close(fig)

    # Create normalized slowdown chart
    create_slowdown_chart(data)


def create_slowdown_chart(data: dict[tuple[str, str], dict[str, PatternData]]) -> None:
    """Create a chart showing slowdown factors relative to sequential pattern.

    This visualization normalizes all times to the sequential baseline (1.0),
    making it easy to compare the "locality penalty" across implementations
    and query types.
    """
    # Skip sequential in the comparison (it's the baseline)
    patterns_to_show = ["strided64", "strided_large", "random", "adversarial"]
    pattern_labels = ["Strided\n(64)", "Strided\n(Large)", "Random", "Adversarial"]

    # Configuration keys in display order
    configs = [
        (("Lookup", "rank"), "Lookup\nRank"),
        (("SpaceEfficient", "rank"), "SpaceEfficient\nRank"),
        (("Lookup", "select"), "Lookup\nSelect"),
        (("SpaceEfficient", "select"), "SpaceEfficient\nSelect"),
    ]

    # Calculate slowdown factors
    slowdowns: dict[tuple[str, str], dict[str, float]] = {}
    for key, _ in configs:
        if key not in data:
            continue
        pattern_data = data[key]
        seq_time = pattern_data.get("sequential", PatternData(1, 0)).avg_ns
        if seq_time == 0:
            continue
        slowdowns[key] = {
            p: pattern_data.get(p, PatternData(0, 0)).avg_ns / seq_time for p in patterns_to_show
        }

    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 7))

    x = np.arange(len(configs))
    width = 0.18  # Width of each bar
    offsets = np.arange(len(patterns_to_show)) - (len(patterns_to_show) - 1) / 2

    for i, pattern in enumerate(patterns_to_show):
        values = []
        for key, _ in configs:
            if key in slowdowns:
                values.append(slowdowns[key].get(pattern, 0))
            else:
                values.append(0)

        bars = ax.bar(
            x + offsets[i] * width,
            values,
            width,
            label=pattern_labels[i],
            color=BAR_COLORS[pattern],
            edgecolor="black",
            linewidth=0.5,
        )

        # Add value labels on bars
        for bar, val in zip(bars, values):
            if val > 0:
                ax.annotate(
                    f"{val:.1f}×",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    fontweight="bold",
                )

    # Add baseline reference line
    ax.axhline(y=1.0, color="green", linestyle="--", linewidth=2, label="Sequential (baseline)")

    ax.set_xlabel("Implementation & Query Type", fontsize=12)
    ax.set_ylabel("Slowdown Factor (× sequential time)", fontsize=12)
    ax.set_title(
        f"Query Locality Penalty: Slowdown Relative to Sequential Access\n(n = {N:,}, queries = {COUNT_QUERIES:,})",
        fontsize=14,
    )
    ax.set_xticks(x)
    ax.set_xticklabels([label for _, label in configs], fontsize=10)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(visible=True, alpha=0.3, axis="y")

    # Set y-axis to start at 0
    ax.set_ylim(bottom=0)

    plt.tight_layout()

    # Save
    pdf_path = OUTPUT_DIR / "query_locality_slowdown.pdf"
    svg_path = OUTPUT_DIR / "query_locality_slowdown.svg"

    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(svg_path, format="svg", bbox_inches="tight")

    print(f"Saved slowdown chart to {pdf_path} and {svg_path}")

    plt.close(fig)
