"""
api/main.py
A thin FastAPI layer over automation_runner, log_parser, and
report_generator so tasks can be triggered over HTTP instead of
only from the terminal.

Run with:
    uvicorn api.main:app --reload
"""

import os

from fastapi import FastAPI, Header, HTTPException

from autoops.automation_runner import run_task, load_config
from autoops.report_generator import generate_report
from autoops.storage import init_db, get_level_counts

app = FastAPI(
    title="AutoOps API",
    description="HTTP interface for triggering AutoOps automation tasks",
    version="0.1.0",
)

# Simple auth token check. In a real deployment this would come from
# a secrets manager, not a plain environment variable default.
API_KEY = os.environ.get("AUTOOPS_API_KEY", "dev-secret-key")


def verify_api_key(x_api_key: str = Header(...)):
    """
    FastAPI dependency: every protected route requires this.
    Raises 401 if the key doesn't match.
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
def root():
    """Basic health endpoint, no auth required."""
    return {"status": "ok", "service": "autoops-api"}


@app.get("/tasks")
def list_tasks():
    """Lists all tasks defined in config.yaml."""
    config = load_config()
    return {"tasks": list(config.get("tasks", {}).keys())}


@app.post("/tasks/{task_name}/run")
def trigger_task(task_name: str, dry_run: bool = True, x_api_key: str = Header(...)):
    """
    Runs a task by name. dry_run defaults to True for safety --
    the caller must explicitly pass ?dry_run=false to make real changes.
    """
    verify_api_key(x_api_key)

    try:
        result = run_task(task_name, dry_run=dry_run)
        return {"task": task_name, "dry_run": dry_run, "result": result}
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/report")
def get_report(range: str = "daily", x_api_key: str = Header(...)):
    """Generates an HTML report and returns its file path."""
    verify_api_key(x_api_key)

    init_db()
    path = generate_report(range)
    return {"report_path": path}


@app.get("/stats")
def get_stats(x_api_key: str = Header(...)):
    """Returns all-time ERROR/WARNING/INFO counts from the database."""
    verify_api_key(x_api_key)

    init_db()
    return get_level_counts()
