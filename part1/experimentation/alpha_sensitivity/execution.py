import csv
import subprocess
from pathlib import Path

from common.execution import (
    JAR_PATH_PREDECESSOR,
    Implementation,
    get_input_files,
    run_java,
)
from common.files import recreate_directory

ALPHAS = [x / 100 for x in range(5, 95 + 1, 5)]  # [0.05, 0.1, ..., 0.95]


def execute():
    inputs_dir = Path(__file__).parent / "generated" / "inputs"
    input_files = get_input_files(inputs_dir)

    measurements_dir = Path(__file__).parent / "generated" / "measurements"
    recreate_directory(measurements_dir)

    with (measurements_dir / "measurements.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=["implementation", "alpha", "time (ns per query)"])
        writer.writeheader()

        combinations = [
            (implementation.value, file, alpha)
            for implementation in Implementation
            for file in input_files
            for alpha in ALPHAS
        ]

        remaining_runs = len(combinations)
        print(f"Executing {remaining_runs} runs.")

        for implementation, file, alpha in combinations:
            assert Path(file).exists(), f"Expected input file {file} to exist"
            assert 0 < alpha < 1, f"Alpha must be between 0 and 1, got {alpha}"

            try:
                result = run_java(jar=JAR_PATH_PREDECESSOR, arg=f"{file} {implementation} {alpha}").stdout
            except subprocess.CalledProcessError as e:
                print(e.stdout)
                print(e.stderr)
                print(e.output)
                print(e.returncode)

            writer.writerows(
                {"implementation": implementation, "alpha": alpha, "time (ns per query)": time}
                for time in result.split("\n")
                if time  # skip empty lines from trailing newline
            )

            remaining_runs -= 1
            print(f"Remaining runs to execute: {remaining_runs}")
