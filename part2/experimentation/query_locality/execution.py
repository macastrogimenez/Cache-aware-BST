"""Execution for Query Locality experiment (Part 2).

Runs Java experiments for all combinations of implementations, query types,
and access patterns. Collects timing measurements to analyze cache behavior.
"""

import csv
import subprocess
from enum import Enum
from pathlib import Path

from common.files import recreate_directory
from part2.experimentation.query_locality.data_generation import (
    COUNT_QUERIES,
    N,
    QueryPattern,
)

# Constants
TRIALS = 5  # Statistical significance
K_VALUE = 4  # SpaceEfficient parameter (per experiment design)
TIMEOUT_SECONDS = 30  # Increased for large n

# Path to JAR file
JAR_PATH = (
    Path(__file__).parent.parent.parent / "implementation" / "app" / "build" / "libs" / "app.jar"
)


class Implementation(Enum):
    """Implementations to test (Naive excluded due to O(n) complexity)."""

    LOOKUP = "Lookup"
    SPACE_EFFICIENT = "SpaceEfficient"


# Pattern ordering: if pattern X times out, skip all patterns after X
# Ordered from fastest (best cache behavior) to slowest (worst cache behavior)
PATTERN_ORDER = [
    QueryPattern.SEQUENTIAL,
    QueryPattern.STRIDED_64,
    QueryPattern.STRIDED_LARGE,
    QueryPattern.RANDOM,
    QueryPattern.ADVERSARIAL,
]


def get_pattern_index(pattern: QueryPattern) -> int:
    """Return the index of a pattern in the performance order (0 = fastest)."""
    return PATTERN_ORDER.index(pattern)


def run_java(
    input_file: Path,
    query_file: Path,
    implementation: str,
    query_type: str,
    k: int | None = None,
) -> int:
    """Run the Java experiment and return total time in nanoseconds.

    Args:
        input_file: Path to bit vector file.
        query_file: Path to query file.
        implementation: "Lookup" or "SpaceEfficient".
        query_type: "rank" or "select".
        k: Required if implementation is "SpaceEfficient".

    Returns:
        Total time in nanoseconds (for the measured queries, excluding warmup).

    Raises:
        subprocess.TimeoutExpired: If execution exceeds TIMEOUT_SECONDS.
        subprocess.CalledProcessError: If Java process returns non-zero exit code.
    """
    args = [
        "java",
        "-Xmx4g",  # Set maximum heap size to 4GB (system has 7.7GB total)
        "-Xms1g",  # Set initial heap size to 1GB
        "-jar",
        str(JAR_PATH),
        str(input_file),
        str(query_file),
        implementation,
        query_type,
    ]

    if k is not None:
        args.append(str(k))

    result = subprocess.run(
        args,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=True,
        text=True,
        encoding="utf-8",
    )
    return int(result.stdout.strip())


def build_combinations() -> list[tuple]:
    """Build list of (implementation, k, query_type, pattern, trial) tuples.

    Ordered by (impl, k, query_type) then by pattern (fastest first), then trial.
    This ordering enables early termination when a pattern times out.
    """
    combinations = []

    for impl in Implementation:
        for query_type in ["rank", "select"]:
            # Patterns ordered from fastest to slowest
            for pattern in PATTERN_ORDER:
                for trial in range(1, TRIALS + 1):
                    if impl == Implementation.SPACE_EFFICIENT:
                        combinations.append((impl, K_VALUE, query_type, pattern, trial))
                    else:
                        combinations.append((impl, None, query_type, pattern, trial))

    return combinations


def execute() -> None:
    """Main entry point for execution phase.

    Runs all combinations and writes measurements to CSV.
    Implements smart timeout handling: if a pattern times out,
    all slower patterns for the same (impl, k, query_type) are skipped.
    """
    inputs_dir = Path(__file__).parent / "generated" / "inputs"
    measurements_dir = Path(__file__).parent / "generated" / "measurements"

    input_file = inputs_dir / "input.txt"

    # Verify JAR exists
    if not JAR_PATH.exists():
        raise RuntimeError(
            f"JAR file not found at {JAR_PATH}. "
            "Please build the Java project first with: cd part2/implementation && ./gradlew build"
        )

    # Verify input file exists
    if not input_file.exists():
        raise RuntimeError(
            "Input file not found. Please run data generation first: "
            "python -m cli.main rank_select query_locality -g"
        )

    # Verify query files exist
    for pattern in QueryPattern:
        for query_type in ["rank", "select"]:
            query_file = inputs_dir / f"queries-{query_type}-{pattern.value}.txt"
            if not query_file.exists():
                raise RuntimeError(
                    f"Query file not found: {query_file}. Please run data generation first."
                )

    print(f"Input file: {input_file}")
    print(f"Input size: n = {N:,}")

    # Build combinations
    combinations = build_combinations()
    total_runs = len(combinations)
    print(f"Total runs to execute: {total_runs}")

    # Create measurements directory
    recreate_directory(measurements_dir)

    # Track timeouts: key = (impl, k, query_type), value = pattern index that timed out
    # If timed_out_at[key] = 2, skip all patterns with index >= 2
    timed_out_at: dict[tuple, int] = {}

    # Track failures and skipped runs for summary
    failures = []
    skipped = []

    fieldnames = [
        "implementation",
        "k",
        "query_type",
        "pattern",
        "trial",
        "total_time_ns",
        "query_count",
    ]

    with (measurements_dir / "measurements.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, (impl, k, query_type, pattern, trial) in enumerate(combinations, 1):
            config_key = (impl.value, k, query_type)
            pattern_idx = get_pattern_index(pattern)
            impl_label = f"{impl.value}" + (f"-k{k}" if k else "")
            progress = f"[{i}/{total_runs}]"

            # Check if this pattern should be skipped due to earlier timeout
            if config_key in timed_out_at and pattern_idx >= timed_out_at[config_key]:
                msg = (
                    f"SKIPPED (slower than timed-out pattern): "
                    f"{impl_label}, {query_type}, {pattern.value}, trial {trial}"
                )
                print(f"{progress} {msg}")
                skipped.append(msg)
                continue

            query_file = inputs_dir / f"queries-{query_type}-{pattern.value}.txt"

            try:
                total_time_ns = run_java(input_file, query_file, impl.value, query_type, k)

                writer.writerow(
                    {
                        "implementation": impl.value,
                        "k": k if k else "",
                        "query_type": query_type,
                        "pattern": pattern.value,
                        "trial": trial,
                        "total_time_ns": total_time_ns,
                        "query_count": COUNT_QUERIES,
                    }
                )

                # Flush after each write to ensure data is saved
                f.flush()

                # Format time for readability
                time_ms = total_time_ns / 1_000_000
                print(
                    f"{progress} {impl_label}, {query_type}, {pattern.value}, "
                    f"trial {trial}: {total_time_ns:,} ns ({time_ms:.2f} ms)"
                )

            except subprocess.TimeoutExpired:
                msg = f"TIMEOUT: {impl_label}, {query_type}, {pattern.value}, trial {trial}"
                print(f"{progress} {msg}")
                failures.append(msg)

                # Mark this pattern index as timed out - skip this and all slower patterns
                if config_key not in timed_out_at:
                    timed_out_at[config_key] = pattern_idx
                    print(
                        f"  → Will skip {pattern.value} and slower patterns "
                        f"for {impl_label}/{query_type}"
                    )

            except subprocess.CalledProcessError as e:
                msg = f"ERROR: {impl_label}, {query_type}, {pattern.value}, trial {trial}"
                print(f"{progress} {msg}")
                if e.stderr:
                    print(f"  stderr: {e.stderr}")
                failures.append(msg)

            except MemoryError:
                msg = f"MEMORY: {impl_label}, {query_type}, {pattern.value}, trial {trial}"
                print(f"{progress} {msg}")
                failures.append(msg)
                # Also skip slower patterns on memory errors
                if config_key not in timed_out_at:
                    timed_out_at[config_key] = pattern_idx
                    print(
                        f"  → Will skip {pattern.value} and slower patterns "
                        f"for {impl_label}/{query_type}"
                    )

    # Summary
    print("\n" + "=" * 60)
    print(f"Execution complete. Total runs attempted: {total_runs}")
    completed = total_runs - len(skipped) - len(failures)
    print(f"Completed: {completed}")
    if skipped:
        print(f"Skipped: {len(skipped)}")
    if failures:
        print(f"Failures: {len(failures)}")
        for failure in failures:
            print(f"  - {failure}")
    if timed_out_at:
        print(f"Configurations that timed out: {list(timed_out_at.keys())}")
    if not failures and not skipped:
        print("All runs completed successfully.")

    print(f"\nMeasurements saved to: {measurements_dir / 'measurements.csv'}")


if __name__ == "__main__":
    execute()
