"""Data generation for Precomputation experiment (Part 2).

Generates bit vector files for measuring construction time.
"""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from common.files import recreate_directory

# Constants
ARBITRARY_SEED_VALUE = 5829471
INPUT_SIZES = [2**i for i in range(6, 27, 2)]  # 2^6, 2^8, ..., 2^26
BIT_DENSITY = 0.5  # 50% ones


def generate_bit_vector(rng: np.random.Generator, n: int, density: float) -> np.ndarray:
    """Generate a bit vector with approximately `density` fraction of ones."""
    return rng.choice([0, 1], size=n, p=[1 - density, density])


def write_bit_vector_file(path: Path, bit_vector: np.ndarray) -> None:
    """Write bit vector in format: n followed by one bit per line."""
    with path.open("w") as f:
        f.write(f"{len(bit_vector)}\n")
        for bit in bit_vector:
            f.write(f"{bit}\n")


def generate_files_for_size(inputs_dir: Path, n: int) -> None:
    """Generate bit vector file for a given input size n."""
    # Use deterministic seed based on n
    rng = np.random.default_rng(seed=ARBITRARY_SEED_VALUE + n)

    # Generate and write bit vector
    bit_vector = generate_bit_vector(rng, n, BIT_DENSITY)
    write_bit_vector_file(inputs_dir / f"input-n{n}.txt", bit_vector)


def generate() -> None:
    """Main entry point for data generation."""
    inputs_dir = recreate_directory(Path(__file__).parent / "generated" / "inputs")

    print(f"Generating {len(INPUT_SIZES)} bit vector files...")
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(generate_files_for_size, inputs_dir, n) for n in INPUT_SIZES
        ]
        for i, future in enumerate(futures):
            future.result()
            print(f"  Generated input for n={INPUT_SIZES[i]}")

    print(f"Done. Files written to {inputs_dir}")
