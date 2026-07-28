"""Execution for Query Performance experiment (Part 2).

Runs Java experiments for all combinations and collects timing measurements.
"""

import csv
import subprocess
from enum import Enum
from pathlib import Path

from common.files import recreate_directory
from part2.experimentation.query_performance.data_generation import COUNT_QUERIES, INPUT_SIZES

# Constants
TRIALS = 5
K_VALUES = [1, 4, 16]  # SpaceEfficient parameter choices
TIMEOUT_SECONDS = 15  # Timeout per run

# Path to JAR file
JAR_PATH = (
    Path(__file__).parent.parent.parent / "implementation" / "app" / "build" / "libs" / "app.jar"
)


class Implementation(Enum):
    NAIVE = "Naive"
    LOOKUP = "Lookup"
    SPACE_EFFICIENT = "SpaceEfficient"


def get_available_sizes(inputs_dir: Path) -> list[int]:
    """Get list of input sizes from available input files."""
    sizes = []
    for n in INPUT_SIZES:
        input_file = inputs_dir / f"input-n{n}.txt"
        if input_file.exists():
            sizes.append(n)
    return sorted(sizes)


def run_java(
    input_file: Path,
    query_file: Path,
    implementation: str,
    query_type: str,
    k: int | None = None,
) -> int:
    """Run the Java experiment and return total time in nanoseconds."""
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


def build_combinations(input_sizes: list[int]) -> list[tuple]:
    """Build list of all (implementation, k, n, query_type, trial) combinations.

    Organized by (impl, k, query_type) then by increasing n, then by trial.
    This allows early termination when timeouts occur.
    """
    combinations = []
    for impl in Implementation:
        for query_type in ["rank", "select"]:
            if impl == Implementation.SPACE_EFFICIENT:
                for k in K_VALUES:
                    for n in input_sizes:
                        for trial in range(1, TRIALS + 1):
                            combinations.append((impl, k, n, query_type, trial))
            else:
                for n in input_sizes:
                    for trial in range(1, TRIALS + 1):
                        combinations.append((impl, None, n, query_type, trial))
    return combinations


def execute() -> None:
    """Main entry point for execution phase."""
    inputs_dir = Path(__file__).parent / "generated" / "inputs"
    measurements_dir = Path(__file__).parent / "generated" / "measurements"

    # Verify JAR exists
    if not JAR_PATH.exists():
        raise RuntimeError(
            f"JAR file not found at {JAR_PATH}. "
            "Please build the Java project first with: cd part2/implementation && ./gradlew build"
        )

    # Get available input sizes
    available_sizes = get_available_sizes(inputs_dir)
    if not available_sizes:
        raise RuntimeError(
            "No input files found. Please run data generation first: "
            "python -m cli.main rank_select query_performance -g"
        )

    print(f"Found input files for sizes: {available_sizes}")

    # Build combinations
    combinations = build_combinations(available_sizes)
    total_runs = len(combinations)
    print(f"Total combinations to execute: {total_runs}")

    # Create measurements directory
    recreate_directory(measurements_dir)

    # Track failures and skipped runs
    failures = []
    skipped = []

    # Track which (impl, k, query_type) combinations have timed out
    # Key: (impl_value, k, query_type), Value: True if timed out
    timed_out_configs = {}

    with (measurements_dir / "measurements.csv").open("w", newline="") as f:
        fieldnames = [
            "implementation",
            "k",
            "n",
            "query_type",
            "trial",
            "total_time_ns",
            "query_count",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, (impl, k, n, query_type, trial) in enumerate(combinations, 1):
            input_file = inputs_dir / f"input-n{n}.txt"
            query_file = inputs_dir / f"queries-{query_type}-n{n}.txt"

            impl_label = f"{impl.value}" + (f"-k{k}" if k else "")
            progress = f"[{i}/{total_runs}]"
            config_key = (impl.value, k, query_type)

            # Skip if this configuration has already timed out
            if timed_out_configs.get(config_key, False):
                msg = (
                    f"SKIPPED (previous timeout): {impl_label}, n={n}, {query_type}, trial {trial}"
                )
                print(f"{progress} {msg}")
                skipped.append(msg)
                continue

            try:
                total_time_ns = run_java(input_file, query_file, impl.value, query_type, k)

                writer.writerow(
                    {
                        "implementation": impl.value,
                        "k": k if k else "",
                        "n": n,
                        "query_type": query_type,
                        "trial": trial,
                        "total_time_ns": total_time_ns,
                        "query_count": COUNT_QUERIES,
                    }
                )

                # Flush after each write to ensure data is saved
                f.flush()

                print(
                    f"{progress} {impl_label}, n={n}, {query_type}, trial {trial}: {total_time_ns} ns"
                )

            except subprocess.TimeoutExpired:
                msg = f"TIMEOUT: {impl_label}, n={n}, {query_type}, trial {trial}"
                print(f"{progress} {msg}")
                failures.append(msg)
                # Mark this configuration as timed out to skip larger sizes
                timed_out_configs[config_key] = True
                print(f"  → Skipping larger sizes for {impl_label}, {query_type}")

            except subprocess.CalledProcessError as e:
                msg = f"ERROR: {impl_label}, n={n}, {query_type}, trial {trial} - {e.stderr}"
                print(f"{progress} {msg}")
                failures.append(msg)

            except MemoryError:
                msg = f"MEMORY: {impl_label}, n={n}, {query_type}, trial {trial}"
                print(f"{progress} {msg}")
                failures.append(msg)
                # Also skip larger sizes on memory errors
                timed_out_configs[config_key] = True
                print(f"  → Skipping larger sizes for {impl_label}, {query_type}")

    # Summary
    print("\n" + "=" * 50)
    print(f"Execution complete. Total runs attempted: {total_runs}")
    completed = total_runs - len(skipped) - len(failures)
    print(f"Completed: {completed}")
    if skipped:
        print(f"Skipped: {len(skipped)}")
    if failures:
        print(f"Failures: {len(failures)}")
        for failure in failures:
            print(f"  - {failure}")
    if not failures and not skipped:
        print("All runs completed successfully.")


if __name__ == "__main__":
    execute()
