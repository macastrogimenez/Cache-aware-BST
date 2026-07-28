import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from common.files import recreate_directory

DATA_PATH = Path(__file__).parent / "generated" / "processed" / "processed.csv"
OUTPUT_DIR = Path(__file__).parent / "generated" / "plots"


def read_data() -> dict[str, dict[str, dict[str, float]]]:
    """Read processed data and organize by implementation and query distribution."""
    data: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))

    with DATA_PATH.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            impl = row["implementation"]
            query_dist = row["query distribution"]
            data[impl][query_dist] = {
                "avg": float(row["avg time per query (ns)"]),
                "stderr": float(row["stderr (ns)"]),
            }

    return dict(data)


def visualize() -> None:
    """Create grouped bar chart for query locality analysis."""
    data = read_data()

    # Define the order of query distributions
    distributions = [
        "high_locality",
        "medium_locality",
        "in_range",
        "low_locality",
        "adversarial_locality",
    ]
    distribution_labels = [
        "High\nLocality",
        "Medium\nLocality",
        "Uniform",
        "Low\nLocality",
        "Adversarial\nLocality",
    ]

    # Define implementations and their styles
    implementations = ["SortedArray", "SearchTree", "OtherArray"]
    styles = {
        "SortedArray": {"color": "#1f77b4"},
        "SearchTree": {"color": "#ff7f0e"},
        "OtherArray": {"color": "#2ca02c"},
    }

    # Prepare data for plotting
    x = np.arange(len(distributions))
    width = 0.25  # Width of each bar

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot bars for each implementation
    for i, impl in enumerate(implementations):
        averages = []
        errors = []
        for dist in distributions:
            if dist in data[impl]:
                averages.append(data[impl][dist]["avg"])
                errors.append(data[impl][dist]["stderr"] * 1.96)  # 95% CI
            else:
                averages.append(0)
                errors.append(0)

        offset = (i - 1) * width
        ax.bar(
            x + offset,
            averages,
            width,
            yerr=errors,
            label=impl,
            color=styles[impl]["color"],
            capsize=3,
            error_kw={"elinewidth": 1, "capthick": 1},
        )

    ax.set_xlabel("Query Locality Pattern", fontsize=12)
    ax.set_ylabel("Average time per query (ns)", fontsize=12)
    ax.set_title(r"Query Time vs Locality Pattern (n = 100K, q = 500K, $\alpha$ = 0.3)", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(distribution_labels, fontsize=10)
    ax.legend(title="Implementation", loc="best")
    ax.grid(visible=True, alpha=0.3, axis="y")

    plt.tight_layout()

    # Save as vector graphics
    recreate_directory(OUTPUT_DIR)
    fig.savefig(OUTPUT_DIR / "query_locality.pdf", format="pdf", bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "query_locality.svg", format="svg", bbox_inches="tight")

    plt.close(fig)


if __name__ == "__main__":
    visualize()
    print(f"Visualization saved to {OUTPUT_DIR}")
