from enum import Enum

import numpy as np


class QueryDistribution(Enum):
    """Query distribution types to test different access patterns."""

    # Uniformly distributed over the range of values in the data set
    UNIFORM_IN_RANGE = "in_range"

    # Sequential traversal over elements in the data set
    # generation differs by how many elements each query answer
    # advances in the data structure
    HIGH_LOCALITY = "high_locality"
    MEDIUM_LOCALITY = "medium_locality"
    LOW_LOCALITY = "low_locality"

    # Alternating queries between left and right quarter of the data set
    ADVERSARIAL_LOCALITY = "adversarial_locality"


def generate_int_set(rng: np.random.Generator, size: int) -> set[int]:
    """
    Generate a uniformly distributed set of unique random integers.

    :param rng: Random number generator
    :param size: Number of integers to generate
    :param integer_bits: Bit width of integers (determines range)
    :return: Set of unique signed integers in range [-2^31, 2^31)
    """
    oversample_factor = 1.05  # Generate 5% extra to account for collisions

    # Generates batches of integers (duplicates allowed),
    # then deduplicates by assigning them to a set
    # repeats until we have the desired amount of integers.
    # This approach is much faster than generation with using replace=False parameter
    result = set()
    while len(result) < size:
        needed = size - len(result)
        # Generate needed samples (plus some extra for collisions)
        batch_size = int(needed * oversample_factor) + 1
        batch = rng.integers(-(2**31), 2**31, size=batch_size, dtype=np.int32)
        # Shift to signed range [-2^31, 2^31)
        result.update(batch)

    # Return exactly 'size' elements
    return set(list(result)[:size])


def generate_queries(
    rng: np.random.Generator,
    count_queries: int,
    distribution: QueryDistribution,
    reference_data: set[int],
):
    sorted_data = sorted(reference_data)
    count_data = len(reference_data)

    def generate_locality_queries(step_min: int, step_max: int) -> list[int]:
        i = 0
        queries = []

        for _ in range(count_queries):
            # Jump by between `step_min` to `step_max` elements forward
            # Wrap around to the beginning if i > count_data
            i = (i + rng.integers(step_min, step_max)) % count_data

            # Small perturbation to not land directly on top of an element
            queries.append(sorted_data[i] + rng.integers(-10, 10 + 1))

        return queries

    match distribution:
        case QueryDistribution.UNIFORM_IN_RANGE:
            # Step size ~33% of data set
            return list(
                rng.integers(low=sorted_data[0], high=sorted_data[-1] + 1, size=count_queries)
            )
        case QueryDistribution.HIGH_LOCALITY:
            # Step size ~0.01% of data set
            return generate_locality_queries(step_min=1, step_max=max(100, count_data // 10_000))
        case QueryDistribution.MEDIUM_LOCALITY:
            # Step size ~1% of data set
            return generate_locality_queries(
                step_min=count_data // 1_000, step_max=count_data // 100
            )
        case QueryDistribution.LOW_LOCALITY:
            # Step size ~10% of data set
            return generate_locality_queries(step_min=count_data // 100, step_max=count_data // 10)
        case QueryDistribution.ADVERSARIAL_LOCALITY:
            # Step size ~50% of data set

            left_quarter = sorted_data[: len(sorted_data) // 4]
            right_quarter = sorted_data[3 * len(sorted_data) // 4 :]

            half = count_queries // 2
            left_queries = rng.choice(left_quarter, size=half)
            right_queries = rng.choice(right_quarter, size=count_queries - half)

            # Interleave: left, right, left, right, ...
            queries = np.empty(count_queries, dtype=left_queries.dtype)
            queries[0::2] = left_queries
            queries[1::2] = right_queries

            return queries.tolist()

        case _:
            raise NotImplementedError(
                f"Generation for query distribution {distribution.value} not implemented."
            )
