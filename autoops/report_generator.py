"""
autoops/report_generator.py
Builds an HTML report from stored log data using a Jinja2 template.
"""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from autoops.storage import get_level_counts, get_top_error_messages, get_all_entries

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT_DIR = "reports"


def generate_report(range_label):
    """
    Pulls data from the database, renders it into the HTML template,
    and writes the result to a file in OUTPUT_DIR.
    Returns the path of the generated report.
    """
    counts = get_level_counts()
    top_errors = get_top_error_messages(limit=5)
    entries = get_all_entries()

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report.html")

    html = template.render(
        range=range_label,
        counts=counts,
        top_errors=top_errors,
        entries=entries,
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"report_{range_label}_{timestamp}.html")

    with open(output_path, "w") as f:
        f.write(html)

    return output_path
