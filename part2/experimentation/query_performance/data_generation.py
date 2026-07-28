"""Data generation for Query Performance experiment (Part 2).

Generates bit vectors and query files for all input sizes.
"""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from common.files import recreate_directory

# Constants
ARBITRARY_SEED_VALUE = 5829471
COUNT_QUERIES = 100_000
INPUT_SIZES = [2**i for i in range(6, 27, 2)]  # 2^6, 2^8, ..., 2^26
BIT_DENSITY = 0.5  # 50% ones


def generate_bit_vector(rng: np.random.Generator, n: int, density: float) -> np.ndarray:
    """Generate a bit vector with approximately `density` fraction of ones."""
    return rng.choice([0, 1], size=n, p=[1 - density, density])


def count_ones(bit_vector: np.ndarray) -> int:
    """Return total count of 1s in the bit vector."""
    return int(np.sum(bit_vector))


def generate_rank_queries(rng: np.random.Generator, n: int, count: int) -> np.ndarray:
    """Generate `count` random indices in range [0, n-1] for rank(i) queries."""
    return rng.integers(0, n, size=count)


def generate_select_queries(rng: np.random.Generator, total_ones: int, count: int) -> np.ndarray:
    """Generate `count` random values in range [1, total_ones] for select(r) queries."""
    return rng.integers(1, total_ones + 1, size=count)


def write_bit_vector_file(path: Path, bit_vector: np.ndarray) -> None:
    """Write bit vector in format: n followed by one bit per line."""
    with path.open("w") as f:
        f.write(f"{len(bit_vector)}\n")
        for bit in bit_vector:
            f.write(f"{bit}\n")


def write_query_file(path: Path, queries: np.ndarray) -> None:
    """Write queries in format: count followed by one query per line."""
    with path.open("w") as f:
        f.write(f"{len(queries)}\n")
        for query in queries:
            f.write(f"{query}\n")


def generate_files_for_size(inputs_dir: Path, n: int) -> None:
    """Generate bit vector and query files for a given input size n."""
    # Use deterministic seed based on n
    rng = np.random.default_rng(seed=ARBITRARY_SEED_VALUE + n)

    # Generate bit vector
    bit_vector = generate_bit_vector(rng, n, BIT_DENSITY)
    total_ones = count_ones(bit_vector)

    # Write bit vector
    write_bit_vector_file(inputs_dir / f"input-n{n}.txt", bit_vector)

    # Generate and write rank queries
    rank_queries = generate_rank_queries(rng, n, COUNT_QUERIES)
    write_query_file(inputs_dir / f"queries-rank-n{n}.txt", rank_queries)

    # Generate and write select queries
    select_queries = generate_select_queries(rng, total_ones, COUNT_QUERIES)
    write_query_file(inputs_dir / f"queries-select-n{n}.txt", select_queries)


def generate() -> None:
    """Main entry point for data generation."""
    inputs_dir = recreate_directory(Path(__file__).parent / "generated" / "inputs")

    print(f"Starting generation of files for {len(INPUT_SIZES)} input sizes.")
    print(f"Input sizes: {INPUT_SIZES}")

    with ProcessPoolExecutor() as ex:
        futures = [ex.submit(generate_files_for_size, inputs_dir, n) for n in INPUT_SIZES]

        for i, future in enumerate(futures):
            future.result()
            n = INPUT_SIZES[i]
            print(f"[{i + 1}/{len(INPUT_SIZES)}] Generated files for n={n}")

    print("Data generation complete.")


if __name__ == "__main__":
    generate()
