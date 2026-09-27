"""
autoops/cli.py
Entry point for the AutoOps CLI tool.
"""

import argparse


def handle_parse(args):
    print(f"[parse] File parsed: {args.file}")


def handle_report(args):
    print(f"[report] Report generated for range: {args.range}")


def handle_run(args):
    print(f"[run] Task executed: {args.task}")


def main():
    parser = argparse.ArgumentParser(
        prog="autoops",
        description="AutoOps CLI - DevOps automation toolkit"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser("parse", help="Parse a log file")
    parse_cmd.add_argument("--file", required=True, help="Path to the log file")
    parse_cmd.set_defaults(func=handle_parse)

    report_cmd = subparsers.add_parser("report", help="Generate a report")
    report_cmd.add_argument(
        "--range",
        choices=["daily", "weekly"],
        default="daily",
        help="Report time range"
    )
    report_cmd.set_defaults(func=handle_report)

    run_cmd = subparsers.add_parser("run", help="Run an automation task")
    run_cmd.add_argument("--task", required=True, help="Task name to run")
    run_cmd.set_defaults(func=handle_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()


