import os
import random

OUT_DIR = "test_inputs"
os.makedirs(OUT_DIR, exist_ok=True)


# ------------------------------------------------------------
# Power-of-two lengths
# ------------------------------------------------------------
def generate_power_of_two_lengths(min_exp=6, max_exp=14):
    return [2**e for e in range(min_exp, max_exp + 1)]


# ------------------------------------------------------------
# Random bitvector of length n
# ------------------------------------------------------------
def generate_random_bitvector(n):
    return "".join(random.choice("01") for _ in range(n))


# ------------------------------------------------------------
# Structured edge-case vectors
# ------------------------------------------------------------
def generate_structured_vectors(n):
    vectors = []

    # All zeros
    vectors.append(("all_zero", "0" * n))

    # All ones
    vectors.append(("all_one", "1" * n))

    # Alternating
    vectors.append(("alternating", "".join("01"[i % 2] for i in range(n))))

    # Prefix-heavy: first 75% ones, last 25% zeros
    prefix_len = int(n * 0.75)
    vectors.append(("prefix_heavy", "1" * prefix_len + "0" * (n - prefix_len)))

    # Suffix-heavy: first 25% zeros, last 75% ones
    suffix_len = int(n * 0.25)
    vectors.append(("suffix_heavy", "0" * suffix_len + "1" * (n - suffix_len)))

    # Block pattern: quarter zeros, quarter ones, quarter zeros, quarter ones
    quarter = n // 4
    pattern = "0" * quarter + "1" * quarter + "0" * quarter + "1" * (n - 3 * quarter)
    vectors.append(("block_pattern", pattern))

    return vectors


# ------------------------------------------------------------
# Generate queries
# ------------------------------------------------------------
def generate_queries(bits, num_rank=20, num_select=20):
    n = len(bits)

    # Rank queries (any index 0..n-1)
    rank_queries = [f"rank {random.randint(0, n - 1)}" for _ in range(num_rank)]

    # Select queries (only valid r)
    ones_count = bits.count("1")
    select_queries = []
    for _ in range(num_select):
        if ones_count == 0:
            select_queries.append("select 1")  # will return -1
        else:
            r = random.randint(1, ones_count)
            select_queries.append(f"select {r}")

    return rank_queries, select_queries


# ------------------------------------------------------------
# Write one test file
# ------------------------------------------------------------
def write_test_file(name, bits, rank_queries, select_queries):
    path = os.path.join(OUT_DIR, f"{name}.txt")
    with open(path, "w") as f:
        f.write(f"{len(bits)}\n")
        f.write(bits + "\n")
        f.write(f"{len(rank_queries)}\n")
        f.write("\n".join(rank_queries) + "\n")
        f.write(f"{len(select_queries)}\n")
        f.write("\n".join(select_queries) + "\n")
    print("Generated:", path)


# ------------------------------------------------------------
# Generate random test cases
# ------------------------------------------------------------
def generate_random_cases(count=50):
    lengths = generate_power_of_two_lengths(6, 14)  # 64..16384
    for i in range(count):
        n = random.choice(lengths)
        bits = generate_random_bitvector(n)
        rank_q, select_q = generate_queries(bits)
        write_test_file(f"random_{i:03d}", bits, rank_q, select_q)


# ------------------------------------------------------------
# Generate structured test cases
# ------------------------------------------------------------
def generate_structured_cases():
    lengths = generate_power_of_two_lengths(6, 12)  # smaller lengths for structured
    for n in lengths:
        for name, bits in generate_structured_vectors(n):
            rank_q, select_q = generate_queries(bits)
            write_test_file(f"{name}_{n}", bits, rank_q, select_q)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    # Random tests
    generate_random_cases(100)

    # Structured tests
    generate_structured_cases()


if __name__ == "__main__":
    main()
