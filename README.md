# AutoOps CLI

A Python command-line tool that automates the repetitive parts of a DevOps
engineer's day: parsing server/application logs, generating HTML reports,
running scheduled maintenance tasks, and exposing those tasks over a REST
API for remote triggering.

## Why

Every DevOps team accumulates a folder of unmaintained one-off scripts for
checking logs, cleaning up old files, and pinging services. AutoOps CLI
replaces that with a single, config-driven, testable tool.

## Architecture

```
        autoops (CLI entry point)
                 |
     dispatches to subcommand
                 v
        log_parser.py -----> storage.py (SQLite)
                                    |
                +-------------------+-------------------+
                v                                        v
      report_generator.py                     automation_runner.py
      (Jinja2 -> HTML report)                 (config.yaml-driven tasks)
                                                          |
                                                          v
                                              api/main.py (FastAPI)
                                              HTTP triggers + --dry-run
```

## Features

| Command | Description |
|---|---|
| `autoops parse --file <path>` | Parses a log file, classifies lines as ERROR/WARNING/INFO using regex, and stores results in SQLite |
| `autoops report --range daily\|weekly` | Generates an HTML report (summary cards, top recurring errors, recent entries) from stored history |
| `autoops run --task <name> [--dry-run]` | Runs a config-driven automation task (cleanup, health_check, backup). `--dry-run` previews the action without making changes |

Tasks are defined in `config/config.yaml` — adding a new automation task
does not require touching the CLI code.

An optional FastAPI layer (`api/main.py`) exposes the same tasks over HTTP,
protected by an API key header, so tasks can be triggered remotely instead
of only from the terminal.

## Tech Stack

- Python 3 + `argparse` for the CLI
- `re` for log parsing
- SQLite (`sqlite3`) for storage
- `Jinja2` for HTML report templates
- `PyYAML` for config-driven task definitions
- `FastAPI` + `uvicorn` for the optional HTTP layer
- `pytest` for unit tests
- `systemd` timer for scheduled runs

## Installation

```bash
git clone https://github.com/rishita-bisht/autoops-cli.git
cd autoops-cli
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

This installs `autoops` as a real command on your PATH (via `pip install -e .`
and the `[project.scripts]` entry in `pyproject.toml`).

## Usage

```bash
# Parse a log file and save results to the database
autoops parse --file logs/sample.log

# Generate an HTML report
autoops report --range daily

# Preview an automation task without making changes
autoops run --task cleanup --dry-run

# Actually run it
autoops run --task cleanup
```

### Running the API

```bash
uvicorn api.main:app --reload
```

Then visit `http://localhost:8000/docs` for interactive API documentation,
or call endpoints directly:

```bash
curl -X POST "http://localhost:8000/tasks/health_check/run?dry_run=true" \
  -H "X-API-Key: dev-secret-key"
```

### Scheduled runs

`systemd/autoops.service` and `systemd/autoops.timer` run the
`health_check` task automatically on a schedule. See those files for the
unit configuration.

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Sample Report

The `autoops report` command generates an HTML report with summary cards,
a table of the most frequent recurring errors, and a detailed log of
recent entries. See `reports/` after running the command.

## What I'd Improve With More Time

- Replace static ERROR/WARNING/INFO thresholds with simple anomaly
  detection (e.g. flag error rates more than 2 standard deviations above
  the rolling average)
- Add multi-server support — parse logs from remote hosts over SSH into a
  central SQLite (or Postgres) store
- Containerize with Docker for easier deployment
- Replace the plain environment-variable API key with a proper secrets
  manager for production use

## Project Structure

```
autoops-cli/
├── autoops/
│   ├── cli.py               # entry point, argparse commands
│   ├── log_parser.py        # regex-based log classification
│   ├── storage.py           # SQLite persistence layer
│   ├── report_generator.py  # Jinja2 HTML report generation
│   ├── automation_runner.py # config-driven task runner
│   └── templates/
│       └── report.html
├── api/
│   └── main.py               # FastAPI layer
├── config/
│   └── config.yaml           # task definitions
├── systemd/
│   ├── autoops.service
│   └── autoops.timer
├── tests/
│   ├── test_parser.py
│   └── test_automation.py
├── pyproject.toml
└── requirements.txt
```
