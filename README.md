# Right-skewed Binary Search Trees

Right-skewed BSTs (where nodes mostly chain off the right child, with few or no left children) can beat balanced BSTs on cache performance for certain workloads, for reasons that come from memory layout, not algorithmic complexity:

Why it helps

Layout matches allocation order. If nodes are allocated with a simple arena/bump allocator and inserted in increasing key order, the right-skewed chain ends up physically contiguous (or close together) in memory. The tree effectively becomes array-like.
Predictable pointer-chasing. Walking the right spine is a single-direction chain of dereferences, like a linked list, rather than branching unpredictably left/right into scattered heap regions. Prefetchers handle single-direction chains far better than the essentially random jumps a balanced tree makes between parent and child nodes.
Fewer cache-line crossings for sequential access. In-order traversal, successor queries, or range scans on a right-skewed tree touch memory much like scanning an array — one cache line after another — instead of repeatedly jumping between distant nodes.

## Report
[Click here](https://github.com/macastrogimenez/Cache-aware-BST/blob/master/Report.pdf)

## Running the project

The environment for running this project is specified in .devcontainer/devcontainer.json.
You can run the project in a devcontainer using VSCode, or by setting up the environment manually on your machine.

First, build to get the `jar` files to execute.

```sh
# Part 1
cd part1/implementation && ./gradlew build

# Part 2
cd part2/implementation && ./gradlew build
```

### Running with Docker

If you have Docker installed, when you open the codebase in VS Code, you get a popup “Reopen in Devcontainer”. That sets up a linux container with the project built.

You should be able to run the experiments as described below, using the CLI interface since it’s an isolated environment.

#### Installing Docker

[link text](https://www.docker.com/products/docker-desktop/)

#### CLI pipelines

```sh
# Activate the python virtual environment if not already activated
uv sync
source .venv/bin/activate

# Run pipelines for all experiments
chmod +x ./run.sh
./run.sh
```

All used for the report are generated in the `{part}/experimentation/{experiment}/generated/{plots}` folder.

To rerun a specific experiment/pipeline step, use the CLI.

```sh
# Run one part of the pipeline for the 'predecessor > query_performance' experiment
python -m cli.main predecessor query_performance # --generate | --execute | --process | --visualize

# Run all experiments in part 1 (predecessor)
python -m cli.main predecessor all

# Get usage help
python -m cli.main --help
```

## Running tests

Run tests with

```sh
# Part 1
cd part1/implementation && ./gradlew test

# Part 2
cd part2/implementation && ./gradlew test
```

Property-based tests are run with 1 000 tries by default. You can specify the amount of runs by passing a value for the `jqwikTries` property.

```sh
# Run 100 000 tries
./gradlew test -PjqwikTries=100000
```

> [!NOTE]
> Part 2 tests with generated data:
> 5 files in the test section are simple edge case tests for small inputs, RankSelectAutomatedTest.java is automated test that uses files generated from python script - both text files and the script are in test_inputs folder.
