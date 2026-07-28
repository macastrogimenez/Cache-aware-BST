from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from common.data_generation import (
    QueryDistribution,
    generate_int_set,
    generate_queries,
)
from common.files import recreate_directory, write_file

ARBITRARY_SEED_VALUE = 2983562
TRIALS = 5
COUNT_QUERIES = 500_000
INPUT_SIZE = 100_000


def generate() -> None:
    path = Path(__file__).parent / "generated" / "inputs"
    target_dir = recreate_directory(path)

    tasks = []
    for distribution in QueryDistribution:
        for trial_idx in range(TRIALS):
            filepath = target_dir / f"input-{distribution.value}-{trial_idx + 1}.txt"
            trial_seed = ARBITRARY_SEED_VALUE + trial_idx

            tasks.append((filepath, trial_seed, distribution))

    print(f"Starting generation of {len(tasks)} files.")

    with ProcessPoolExecutor() as ex:
        futures = [
            ex.submit(generate_file, filepath, trial_seed, distribution)
            for filepath, trial_seed, distribution in tasks
        ]

        for i, future in enumerate(futures):
            future.result()
            print(f"{i}/{len(tasks)} files generated.")


def generate_file(filepath: Path, trial_seed: int, query_distribution: QueryDistribution) -> None:
    rng = np.random.default_rng(seed=trial_seed)

    input_ints = generate_int_set(rng, INPUT_SIZE)
    queries = generate_queries(
        rng,
        count_queries=COUNT_QUERIES,
        distribution=query_distribution,
        reference_data=input_ints,
    )

    write_file(path=filepath, input_ints=input_ints, queries=queries)
