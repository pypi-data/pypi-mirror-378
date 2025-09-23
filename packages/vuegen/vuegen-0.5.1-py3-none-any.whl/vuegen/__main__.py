"""Command-line interface for VueGen report generation."""

import sys
from pathlib import Path

from vuegen import report_generator
from vuegen.utils import get_completion_message, get_logger, get_parser


def main():
    # Parse command-line arguments
    parser = get_parser(prog_name="VueGen")
    args = parser.parse_args()

    # Determine the vuegen arguments
    config_path = args.config
    dir_path = args.directory
    report_type = args.report_type

    # Determine the report name for logger suffix
    if config_path:
        report_name = Path(config_path).stem
    elif dir_path:
        report_name = Path(dir_path).name
    else:
        print("Please provide a configuration file or directory path:\n")
        # https://docs.python.org/3/library/argparse.html#printing-help
        parser.print_help()
        sys.exit(1)

    if config_path and dir_path:
        print("Please provide only one of configuration file or directory path:\n")
        parser.print_help()
        sys.exit(1)  # otherwise could resort to either or ?

    # Define logger suffix based on report type and name
    logger_suffix = f"{report_type}_report_{str(report_name)}"

    # Initialize logger
    logger, logfile = get_logger(f"{logger_suffix}")
    logger.info("logfile: %s", logfile)

    # Generate the report
    _, _ = report_generator.get_report(
        report_type=report_type,
        logger=logger,
        config_path=config_path,
        dir_path=dir_path,
        output_dir=args.output_directory,
        streamlit_autorun=args.streamlit_autorun,
        quarto_checks=args.quarto_checks,
        max_depth=args.max_depth,
    )

    # Print completion message
    # ! Could use now report_dir and config_path as information
    print(get_completion_message(report_type, config_path))


if __name__ == "__main__":
    main()
