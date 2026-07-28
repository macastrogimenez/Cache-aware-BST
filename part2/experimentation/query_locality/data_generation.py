"""Data generation for Query Locality experiment (Part 2).

Generates a single large bit vector and query files for each (query_type, pattern) combination.
Demonstrates how different query access patterns affect performance due to CPU cache behavior.
"""

from enum import Enum
from pathlib import Path

import numpy as np

from common.files import recreate_directory

# Constants
SEED = 7283651  # For reproducibility
N = 2**24  # 16,777,216 - Large enough to exceed L3 cache
COUNT_QUERIES = 500_000  # Sufficient for stable timing
BIT_DENSITY = 0.5  # 50% ones, consistent with other experiments


class QueryPattern(Enum):
    """Query access patterns for locality testing."""

    SEQUENTIAL = "sequential"
    STRIDED_64 = "strided64"
    STRIDED_LARGE = "strided_large"
    RANDOM = "random"
    ADVERSARIAL = "adversarial"


def generate_bit_vector(rng: np.random.Generator, n: int, density: float) -> np.ndarray:
    """Generate a bit vector with approximately `density` fraction of ones."""
    return rng.choice([0, 1], size=n, p=[1 - density, density])


def count_ones(bit_vector: np.ndarray) -> int:
    """Return total count of 1s in the bit vector."""
    return int(np.sum(bit_vector))


def generate_rank_queries_by_pattern(
    rng: np.random.Generator,
    n: int,
    pattern: QueryPattern,
    count: int,
) -> np.ndarray:
    """Generate rank queries (indices in [0, n-1]) following the specified pattern.

    Args:
        rng: Random number generator for reproducibility.
        n: Size of the bit vector.
        pattern: The query access pattern to generate.
        count: Number of queries to generate.

    Returns:
        Array of query indices.
    """
    match pattern:
        case QueryPattern.SEQUENTIAL:
            # Queries: 0, 1, 2, 3, ... mod n
            return np.arange(count) % n

        case QueryPattern.STRIDED_64:
            # Queries: 0, 64, 128, 192, ... mod n
            return (np.arange(count) * 64) % n

        case QueryPattern.STRIDED_LARGE:
            # Stride = n / 1000 ≈ 16,777 for n = 2^24
            stride = max(1, n // 1000)
            return (np.arange(count) * stride) % n

        case QueryPattern.RANDOM:
            # Uniform random from [0, n-1]
            return rng.integers(0, n, size=count)

        case QueryPattern.ADVERSARIAL:
            # Alternating between left quarter [0, n/4) and right quarter [3n/4, n)
            # This forces cache thrashing by jumping between distant memory regions
            queries = np.empty(count, dtype=np.int64)
            left_end = n // 4
            right_start = 3 * n // 4
            for i in range(count):
                if i % 2 == 0:
                    queries[i] = rng.integers(0, left_end)
                else:
                    queries[i] = rng.integers(right_start, n)
            return queries


def generate_select_queries_by_pattern(
    rng: np.random.Generator,
    total_ones: int,
    pattern: QueryPattern,
    count: int,
) -> np.ndarray:
    """Generate select queries (values in [1, total_ones]) following the specified pattern.

    Args:
        rng: Random number generator for reproducibility.
        total_ones: Total number of 1s in the bit vector.
        pattern: The query access pattern to generate.
        count: Number of queries to generate.

    Returns:
        Array of query values (1-indexed).
    """
    match pattern:
        case QueryPattern.SEQUENTIAL:
            # Sequential r-values: 1, 2, 3, ... mod total_ones + 1
            return (np.arange(count) % total_ones) + 1

        case QueryPattern.STRIDED_64:
            # Strided: 1, 65, 129, ... mod total_ones
            return ((np.arange(count) * 64) % total_ones) + 1

        case QueryPattern.STRIDED_LARGE:
            stride = max(1, total_ones // 1000)
            return ((np.arange(count) * stride) % total_ones) + 1

        case QueryPattern.RANDOM:
            return rng.integers(1, total_ones + 1, size=count)

        case QueryPattern.ADVERSARIAL:
            # Alternating between left and right quarter of valid r-values
            queries = np.empty(count, dtype=np.int64)
            left_end = total_ones // 4
            right_start = 3 * total_ones // 4
            for i in range(count):
                if i % 2 == 0:
                    queries[i] = rng.integers(1, max(2, left_end + 1))
                else:
                    queries[i] = rng.integers(max(1, right_start), total_ones + 1)
            return queries


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


def generate() -> None:
    """Main entry point for data generation.

    Generates:
    - One large bit vector (n = 2^24)
    - 10 query files (5 patterns x 2 query types: rank and select)
    """
    inputs_dir = recreate_directory(Path(__file__).parent / "generated" / "inputs")

    rng = np.random.default_rng(seed=SEED)

    # 1. Generate single bit vector
    print(f"Generating bit vector with n={N:,}...")
    bit_vector = generate_bit_vector(rng, N, BIT_DENSITY)
    total_ones = count_ones(bit_vector)
    print(f"Total ones: {total_ones:,} ({total_ones / N * 100:.1f}%)")

    write_bit_vector_file(inputs_dir / "input.txt", bit_vector)
    print("Written input.txt")

    # 2. Generate query files for each (query_type, pattern) combination
    for pattern in QueryPattern:
        # Rank queries
        rank_queries = generate_rank_queries_by_pattern(rng, N, pattern, COUNT_QUERIES)
        write_query_file(inputs_dir / f"queries-rank-{pattern.value}.txt", rank_queries)
        print(f"Generated rank queries for {pattern.value}")

        # Select queries
        select_queries = generate_select_queries_by_pattern(rng, total_ones, pattern, COUNT_QUERIES)
        write_query_file(inputs_dir / f"queries-select-{pattern.value}.txt", select_queries)
        print(f"Generated select queries for {pattern.value}")

    print("\nData generation complete.")
    print(f"Generated files in: {inputs_dir}")


if __name__ == "__main__":
    generate()
