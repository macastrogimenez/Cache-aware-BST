import argparse
import sys

from part1.experimentation.alpha_sensitivity.data_generation import (
    generate as alpha_sensitivity_generate,
)
from part1.experimentation.alpha_sensitivity.execution import execute as alpha_sensitivity_execute
from part1.experimentation.alpha_sensitivity.processing import process as alpha_sensitivity_process
from part1.experimentation.alpha_sensitivity.visualize import (
    visualize as alpha_sensitivity_visualize,
)
from part1.experimentation.query_locality.data_generation import generate as query_locality_generate
from part1.experimentation.query_locality.execution import execute as query_locality_execute
from part1.experimentation.query_locality.processing import process as query_locality_process
from part1.experimentation.query_locality.visualize import visualize as query_locality_visualize
from part2.experimentation.precomputation.data_generation import (
    generate as precomputation_generate,
)
from part2.experimentation.precomputation.execution import (
    execute as precomputation_execute,
)
from part2.experimentation.precomputation.processing import (
    process as precomputation_process,
)
from part2.experimentation.precomputation.visualize import (
    visualize as precomputation_visualize,
)
from part2.experimentation.query_locality.data_generation import (
    generate as rs_query_locality_generate,
)
from part2.experimentation.query_locality.execution import (
    execute as rs_query_locality_execute,
)
from part2.experimentation.query_locality.processing import (
    process as rs_query_locality_process,
)
from part2.experimentation.query_locality.visualize import (
    visualize as rs_query_locality_visualize,
)
from part2.experimentation.query_performance.data_generation import (
    generate as query_performance_generate,
)
from part2.experimentation.query_performance.execution import (
    execute as query_performance_execute,
)
from part2.experimentation.query_performance.processing import (
    process as query_performance_process,
)
from part2.experimentation.query_performance.visualize import (
    visualize as query_performance_visualize,
)


def run_experiment(args, generate_fn, execute_fn, process_fn, visualize_fn):
    """Run experiment steps based on command-line arguments."""
    if args.generate:
        generate_fn()
        sys.exit(0)

    if args.execute:
        execute_fn()
        sys.exit(0)

    if args.process:
        process_fn()
        sys.exit(0)

    if args.visualize:
        visualize_fn()
        sys.exit(0)

    # Run all steps if no specific step is selected
    print("=== Generating data ===")
    generate_fn()
    print("=== Gathering measurements ===")
    execute_fn()
    print("=== Processing measurements ===")
    process_fn()
    print("=== Creating visualizations ===")
    visualize_fn()


def run_predecessor_alpha_sensitivity(args):
    """Run predecessor alpha_sensitivity experiment."""
    print("\n>>> Running predecessor/alpha_sensitivity <<<")
    run_experiment(
        args,
        alpha_sensitivity_generate,
        alpha_sensitivity_execute,
        alpha_sensitivity_process,
        alpha_sensitivity_visualize,
    )


def run_predecessor_query_locality(args):
    """Run predecessor query_locality experiment."""
    print("\n>>> Running predecessor/query_locality <<<")
    run_experiment(
        args,
        query_locality_generate,
        query_locality_execute,
        query_locality_process,
        query_locality_visualize,
    )


def run_rank_select_precomputation(args):
    """Run rank_select precomputation experiment."""
    print("\n>>> Running rank_select/precomputation <<<")
    run_experiment(
        args,
        precomputation_generate,
        precomputation_execute,
        precomputation_process,
        precomputation_visualize,
    )


def run_rank_select_query_performance(args):
    """Run rank_select query_performance experiment."""
    print("\n>>> Running rank_select/query_performance <<<")
    run_experiment(
        args,
        query_performance_generate,
        query_performance_execute,
        query_performance_process,
        query_performance_visualize,
    )


def run_rank_select_query_locality(args):
    """Run rank_select query_locality experiment."""
    print("\n>>> Running rank_select/query_locality <<<")
    run_experiment(
        args,
        rs_query_locality_generate,
        rs_query_locality_execute,
        rs_query_locality_process,
        rs_query_locality_visualize,
    )


def run_all_predecessor(args):
    """Run all predecessor experiments."""
    run_predecessor_alpha_sensitivity(args)
    run_predecessor_query_locality(args)


def run_all_rank_select(args):
    """Run all rank_select experiments."""
    run_rank_select_precomputation(args)
    run_rank_select_query_performance(args)
    run_rank_select_query_locality(args)


def run_all_experiments(args):
    """Run all experiments for both parts."""
    print("=" * 50)
    print("Running all experiments")
    print("=" * 50)
    run_all_predecessor(args)
    run_all_rank_select(args)
    print("\n" + "=" * 50)
    print("All experiments completed!")
    print("=" * 50)


def main():
    args = parse(sys.argv[1:])

    match args.part:
        case "all":
            run_all_experiments(args)
        case "predecessor":
            match args.experiment:
                case "all":
                    run_all_predecessor(args)
                case "alpha_sensitivity":
                    run_predecessor_alpha_sensitivity(args)
                case "query_locality":
                    run_predecessor_query_locality(args)
        case "rank_select":
            match args.experiment:
                case "all":
                    run_all_rank_select(args)
                case "precomputation":
                    run_rank_select_precomputation(args)
                case "query_performance":
                    run_rank_select_query_performance(args)
                case "query_locality":
                    run_rank_select_query_locality(args)


def parse(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ExperimentRunner",
        description="Runs experiments for evaluating implementations of Predecessor and Rank-Select problems",
        epilog="Created by Urszula Matysiak, Miguel Angel Castro Gimenez and Tomas Vemola ({urma, migca, tvem}@itu.dk) for the Applied Algorithms course at IT University of Copenhagen. Autumn semester of 2025.",
    )

    subparsers = parser.add_subparsers(required=True, title="problem", dest="part")

    # "all" subparser to run all experiments
    all_parser = subparsers.add_parser("all", help="Run all experiments for both parts")
    all_selective = all_parser.add_mutually_exclusive_group()
    all_selective.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Runs only the data generation for all experiments",
    )
    all_selective.add_argument(
        "-e",
        "--execute",
        action="store_true",
        help="Runs only the execution step gathering the timings for all experiments",
    )
    all_selective.add_argument(
        "-p",
        "--process",
        action="store_true",
        help="Runs only the processing step for all experiments",
    )
    all_selective.add_argument(
        "-v",
        "--visualize",
        action="store_true",
        help="Runs only the visualization step for all experiments",
    )

    part1 = subparsers.add_parser("predecessor")
    part1.add_argument(
        "experiment",
        choices=["all", "alpha_sensitivity", "query_locality"],
        type=str,
        help="Experiment to run ('all' runs all predecessor experiments)",
    )
    selective_execution = part1.add_mutually_exclusive_group()
    selective_execution.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Runs only the data generation for the selected experiment",
    )
    selective_execution.add_argument(
        "-e",
        "--execute",
        action="store_true",
        help="Runs only the execution step gathering the timings for the selected experiment",
    )
    selective_execution.add_argument(
        "-p",
        "--process",
        action="store_true",
        help="Runs only the processing step for the selected experiment",
    )
    selective_execution.add_argument(
        "-v",
        "--visualize",
        action="store_true",
        help="Runs only the visualization step for the selected experiment",
    )

    part2 = subparsers.add_parser("rank_select")
    part2.add_argument(
        "experiment",
        choices=["all", "query_performance", "query_locality", "precomputation"],
        type=str,
        help="Experiment to run ('all' runs all rank_select experiments)",
    )
    selective_execution_part2 = part2.add_mutually_exclusive_group()
    selective_execution_part2.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Runs only the data generation for the selected experiment",
    )
    selective_execution_part2.add_argument(
        "-e",
        "--execute",
        action="store_true",
        help="Runs only the execution step gathering the timings for the selected experiment",
    )
    selective_execution_part2.add_argument(
        "-p",
        "--process",
        action="store_true",
        help="Runs only the processing step for the selected experiment",
    )
    selective_execution_part2.add_argument(
        "-v",
        "--visualize",
        action="store_true",
        help="Runs only the visualization step for the selected experiment",
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    main()
