#!/usr/bin/env bash

set -e

PREFIX="🍰  "
echo "$PREFIX Running $(basename $0)"

echo "$PREFIX Setting up safe git repository to prevent dubious ownership errors"
git config --global --add safe.directory /workspace

echo "$PREFIX Setting up the uv environment"
curl -LsSf https://astral.sh/uv/0.9.17/install.sh | sh
uv venv --python 3.14
. .venv/bin/activate
uv sync

echo "$PREFIX Building implementation of part 1"
cd part1/implementation && ./gradlew build

echo "$PREFIX Building implementation of part 2"
cd ../../ && cd part2/implementation && ./gradlew build

echo "$PREFIX SUCCESS"
exit 0