import logging
import shutil
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

import yaml

logger = logging.getLogger(__name__)


def load_config(config_path="config/config.yaml"):
    """YAML file padho aur dictionary me convert karo."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file nahi mili: {config_path}")
    with open(path) as f:
        return yaml.safe_load(f)


def run_cleanup(task, dry_run):
    folder = Path(task["path"])
    if not folder.exists():
        raise FileNotFoundError(f"Folder nahi mila: {folder}")

    cutoff = time.time() - task["older_than_days"] * 86400  # din ko seconds me
    count = 0

    for item in folder.iterdir():
        if item.is_file() and item.stat().st_mtime < cutoff:
            if dry_run:
                logger.info(f"[DRY RUN] Delete hoti: {item}")
            else:
                item.unlink()
                logger.info(f"Deleted: {item}")
            count += 1

    return f"{count} files {'milti' if dry_run else 'delete hui'}"


def run_health_check(task, dry_run):
    if dry_run:
        return f"[DRY RUN] {task['url']} ko ping karte"
    try:
        with urlopen(task["url"], timeout=task["timeout_seconds"]) as resp:
            return f"OK, status {resp.status}"
    except URLError as e:
        raise RuntimeError(f"Health check fail: {e}")


def run_backup(task, dry_run):
    src = Path(task["source"])
    dest = Path(task["destination"])
    if not src.exists():
        raise FileNotFoundError(f"Source nahi mila: {src}")

    stamp = time.strftime("%Y%m%d_%H%M%S")
    target = dest / f"backup_{stamp}"

    if dry_run:
        return f"[DRY RUN] {src} -> {target} copy hota"

    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target)
    return f"Backup ban gaya: {target}"


# Task type ko function se jodne wali dictionary
TASK_HANDLERS = {
    "cleanup": run_cleanup,
    "health_check": run_health_check,
    "backup": run_backup,
}


def run_task(task_name, dry_run=False, config_path="config/config.yaml"):
    config = load_config(config_path)
    tasks = config.get("tasks", {})

    if task_name not in tasks:
        raise ValueError(f"Task '{task_name}' config me nahi hai. Available: {list(tasks)}")

    task = tasks[task_name]
    handler = TASK_HANDLERS.get(task["type"])
    if handler is None:
        raise ValueError(f"Unknown task type: {task['type']}")

    logger.info(f"Task shuru: {task_name}")
    result = handler(task, dry_run)
    logger.info(f"Task khatam: {result}")
    return result
