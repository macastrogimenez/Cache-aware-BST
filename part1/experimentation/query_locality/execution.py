import csv
import subprocess
from pathlib import Path

from common.data_generation import QueryDistribution
from common.execution import (
    JAR_PATH_PREDECESSOR,
    Implementation,
    get_input_files,
    run_java,
)
from common.files import recreate_directory

ALPHA = 0.3


def execute():
    inputs_dir = Path(__file__).parent / "generated" / "inputs"
    input_files = get_input_files(inputs_dir)

    measurements_dir = Path(__file__).parent / "generated" / "measurements"
    recreate_directory(measurements_dir)

    with (measurements_dir / "measurements.csv").open("w") as f:
        writer = csv.DictWriter(
            f, fieldnames=["implementation", "alpha", "query distribution", "time (ns per query)"]
        )
        writer.writeheader()

        combinations = [
            (implementation.value, file)
            for implementation in Implementation
            for file in input_files
        ]

        remaining_runs = len(combinations)
        print(f"Executing {remaining_runs} runs.")

        for implementation, file in combinations:
            assert Path(file).exists(), f"Expected input file {file} to exist"

            distribution = file.name.split("-")[1]
            assert distribution in [d.value for d in QueryDistribution]

            try:
                result = run_java(jar=JAR_PATH_PREDECESSOR, arg=f"{file} {implementation} {ALPHA}").stdout
            except subprocess.CalledProcessError as e:
                print(e.stdout)
                print(e.stderr)
                print(e.output)
                print(e.returncode)

            writer.writerows(
                {
                    "implementation": implementation,
                    "alpha": ALPHA,
                    "time (ns per query)": time,
                    "query distribution": distribution,
                }
                for time in result.split("\n")
                if time  # skip empty lines from trailing newline
            )

            remaining_runs -= 1
            print(f"Remaining runs to execute: {remaining_runs}")
