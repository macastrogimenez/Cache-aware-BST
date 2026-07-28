import contextlib
import shutil
from pathlib import Path


def recreate_directory(target_path: Path) -> Path:
    # Ignore error if directory does not exist
    with contextlib.suppress(Exception):
        shutil.rmtree(target_path, ignore_errors=True)

    target_path.mkdir(parents=True, exist_ok=True)
    return target_path


def write_file(path: Path, input_ints: set[int], queries: list[int]) -> None:
    with path.open("w") as f:
        f.write(f"{len(input_ints)} {len(queries)}\n")

        joined_inputs = "\n".join(map(str, input_ints))
        f.write(joined_inputs)
        f.write("\n")

        joined_queries = "\n".join(map(str, queries))
        f.write(joined_queries)
