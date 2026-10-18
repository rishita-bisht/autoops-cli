"""
autoops/cli.py
Entry point for the AutoOps CLI tool.
"""

import argparse
import logging

from autoops.log_parser import parse_log
from autoops.storage import init_db, save_entries, get_level_counts
from autoops.report_generator import generate_report
from autoops.automation_runner import run_task


def handle_parse(args):
    init_db()
    result = parse_log(args.file)
    save_entries(result["entries"], source_file=args.file)

    print(f"[parse] File: {args.file}")
    print(f"[parse] Total lines parsed: {len(result['entries'])}")
    print(f"[parse] ERROR: {result['counts']['ERROR']}")
    print(f"[parse] WARNING: {result['counts']['WARNING']}")
    print(f"[parse] INFO: {result['counts']['INFO']}")
    if result["unmatched"]:
        print(f"[parse] Lines that didn't match expected format: {result['unmatched']}")

    print("[parse] Saved to database.")
    totals = get_level_counts()
    print(f"[parse] All-time totals in database: {totals}")


def handle_report(args):
    init_db()
    output_path = generate_report(args.range)
    print(f"[report] Report generated: {output_path}")


def handle_run(args):
    try:
        result = run_task(args.task, dry_run=args.dry_run)
        print(f"[run] {result}")
    except Exception as e:
        print(f"[run] ERROR: {e}")
        raise SystemExit(1)


def main():
    # Logging setup: tool ke messages terminal pe dikhenge
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

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
    run_cmd.add_argument(
        "--dry-run",
        action="store_true",
        help="Sirf dikhao kya hoga, kuch actually mat karo"
    )
    run_cmd.set_defaults(func=handle_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
