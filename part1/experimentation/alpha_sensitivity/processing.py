import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from common.execution import Implementation
from common.files import recreate_directory

MEASUREMENTS_PATH = Path(__file__).parent / "generated" / "measurements" / "measurements.csv"


def process() -> None:
    aggregated = read_and_aggregate()
    write_processing_output(aggregated)


@dataclass
class Aggregate:
    alpha: float
    avg_per_query: float
    std_per_query: float
    stderr_per_query: float


type ProcessedData = dict[Implementation, list[Aggregate]]


def read_and_aggregate() -> ProcessedData:
    print("Reading measurements")
    
    chunk_size = 100_000
    aggregates = []
    
    for chunk in pd.read_csv(
        MEASUREMENTS_PATH,
        usecols=["implementation", "time (ns per query)", "alpha"],
        dtype={"implementation": "category", "alpha": "float64"},
        chunksize=chunk_size
    ):
        # Aggregate each chunk
        chunk_grouped = (
            chunk.groupby(["implementation", "alpha"], observed=False)["time (ns per query)"]
            .agg(["sum", "count", lambda x: (x**2).sum()])
            .reset_index()
        )
        chunk_grouped.columns = ["implementation", "alpha", "sum", "count", "sum_sq"]
        aggregates.append(chunk_grouped)
    
    print("Combining chunks...")
    # Combine all chunks
    df = pd.concat(aggregates, ignore_index=True)
    
    # Final aggregation across chunks
    grouped = (
        df.groupby(["implementation", "alpha"], observed=False)
        .agg({"sum": "sum", "count": "sum", "sum_sq": "sum"})
        .reset_index()
    )
    
    # Calculate mean, std, stderr from aggregated statistics
    grouped["mean"] = grouped["sum"] / grouped["count"]
    grouped["std"] = np.sqrt(np.maximum(0, (grouped["sum_sq"] / grouped["count"]) - grouped["mean"]**2))
    grouped["stderr"] = grouped["std"] / np.sqrt(grouped["count"])

    # Build result dictionary
    impl_map = {
        "SortedArray": Implementation.SORTED_ARRAY,
        "SearchTree": Implementation.SEARCH_TREE,
        "OtherArray": Implementation.OTHER_ARRAY,
    }

    result: ProcessedData = {impl: [] for impl in Implementation}

    print("Processing output.")
    for _, row in grouped.iterrows():
        impl = impl_map.get(row["implementation"])
        if impl is None:
            raise ValueError(f"unexpected implementation value: {row['implementation']}")
        result[impl].append(
            Aggregate(
                alpha=round(row["alpha"], 2),
                avg_per_query=row["mean"],
                std_per_query=row["std"],
                stderr_per_query=row["stderr"],
            )
        )

    return result


def write_processing_output(data: ProcessedData) -> None:
    processing_dir = Path(__file__).parent / "generated" / "processed"
    recreate_directory(processing_dir)

    with (processing_dir / "processed.csv").open("w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "implementation",
                "alpha",
                "avg time per query (ns)",
                "std (ns)",
                "stderr (ns)",
            ],
        )
        writer.writeheader()

        for implementation, aggregates in data.items():
            for agg in aggregates:
                writer.writerow(
                    {
                        "implementation": implementation.value,
                        "alpha": agg.alpha,
                        "avg time per query (ns)": agg.avg_per_query,
                        "std (ns)": agg.std_per_query,
                        "stderr (ns)": agg.stderr_per_query,
                    }
                )
