import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from common.files import recreate_directory

DATA_PATH = Path(__file__).parent / "generated" / "processed" / "processed.csv"
OUTPUT_DIR = Path(__file__).parent / "generated" / "plots"


def read_data() -> dict[str, dict[str, list[float]]]:
    """Read processed data and organize by implementation."""
    data: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"alpha": [], "avg": [], "stderr": []}
    )

    with DATA_PATH.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            impl = row["implementation"]
            data[impl]["alpha"].append(float(row["alpha"]))
            data[impl]["avg"].append(float(row["avg time per query (ns)"]))
            data[impl]["stderr"].append(float(row["stderr (ns)"]))

    # Sort by alpha for each implementation
    for impl in data:
        sorted_indices = sorted(
            range(len(data[impl]["alpha"])), key=lambda i: data[impl]["alpha"][i]
        )
        data[impl]["alpha"] = [data[impl]["alpha"][i] for i in sorted_indices]
        data[impl]["avg"] = [data[impl]["avg"][i] for i in sorted_indices]
        data[impl]["stderr"] = [data[impl]["stderr"][i] for i in sorted_indices]

    return dict(data)


def visualize() -> None:
    """Create line plot with error bars for alpha sensitivity analysis."""
    data = read_data()

    # Color and style configuration
    styles = {
        "SortedArray": {"color": "#1f77b4", "marker": "o"},
        "SearchTree": {"color": "#ff7f0e", "marker": "s"},
        "OtherArray": {"color": "#2ca02c", "marker": "^"},
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    for impl, values in data.items():
        style = styles.get(impl, {"color": "gray", "marker": "x"})
        ax.errorbar(
            values["alpha"],
            values["avg"],
            yerr=[s * 1.96 for s in values["stderr"]],  # 95% CI
            label=impl,
            color=style["color"],
            marker=style["marker"],
            markersize=5,
            capsize=3,
            capthick=1,
            linewidth=1.5,
        )

    ax.set_xlabel(r"Balance parameter $\alpha$", fontsize=12)
    ax.set_ylabel("Average time per query (ns)", fontsize=12)
    ax.set_title(r"Query Time vs Balance Parameter $\alpha$ (n = 100K, q = 500K)", fontsize=14)
    ax.legend(title="Implementation", loc="best")
    ax.grid(visible=True, alpha=0.3)

    # Set x-axis ticks to match alpha levels (0.05, 0.1, 0.15, ..., 0.95)
    ax.set_xticks([x / 100 for x in range(5, 95 + 1, 5)])

    plt.tight_layout()

    # Save as vector graphics
    recreate_directory(OUTPUT_DIR)
    fig.savefig(OUTPUT_DIR / "alpha_sensitivity.pdf", format="pdf", bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "alpha_sensitivity.svg", format="svg", bbox_inches="tight")

    plt.close(fig)
