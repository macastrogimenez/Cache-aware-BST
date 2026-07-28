# Construct absolute path relative to this script's location
import subprocess
from enum import Enum
from pathlib import Path

JAR_PATH_PREDECESSOR = (
    Path(__file__).parent.parent / "part1" / "implementation" / "app" / "build" / "libs" / "app.jar"
)


class Implementation(Enum):
    SORTED_ARRAY = "SortedArray"
    OTHER_ARRAY = "OtherArray"
    SEARCH_TREE = "SearchTree"


def run_java(jar: Path, arg: str) -> subprocess.CompletedProcess:
    if not Path.exists(jar):
        raise RuntimeError(
            f"File not found at path: {jar.absolute()}. Have you run ./gradlew build to create the jar file?"
        )

    return subprocess.run(
        [  # noqa: S607
            "java",
            "-Xmx8g",  # Set maximum heap size to 8GB
            "-Xms2g",  # Set initial heap size to 2GB
            "-jar",
            str(jar),
            arg,
        ],  
        capture_output=True,
        timeout=15,
        check=True,
        text=True,
        encoding="utf-8",
    )


def get_input_files(inputs_dir: Path) -> list[Path]:
    if not Path.exists(inputs_dir):
        raise RuntimeError("'generated' folder does not exist. Have you run data generation?")

    input_files = list(Path.glob(inputs_dir, "input-*.txt"))

    if len(input_files) == 0:
        raise RuntimeError("No files in the 'generated' directory. Have you run data generation?")

    return input_files
