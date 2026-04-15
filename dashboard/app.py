from pathlib import Path
import csv
import json
import sys
from datetime import datetime

# Ensure dashboard can import project modules when launched from the repo root.
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from flask import Flask, render_template
from src.config import LOG_PATH, WHITELIST_PATH

app = Flask(__name__, template_folder="templates", static_folder="static")


def load_log_rows():
    log_path = Path(LOG_PATH)
    if not log_path.exists():
        return []

    rows = []
    with log_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            time_value = row.get("Time") or row.get("time")
            try:
                row["parsed_time"] = datetime.strptime(time_value, "%Y-%m-%d %H:%M:%S") if time_value else None
            except Exception:
                row["parsed_time"] = None
            rows.append(row)

    return rows


def load_whitelist():
    whitelist_path = Path(WHITELIST_PATH)
    if not whitelist_path.exists():
        return []
    try:
        with whitelist_path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def build_summary(rows):
    summary = {
        "total_events": len(rows),
        "trusted": 0,
        "safe": 0,
        "untrusted": 0,
        "blocked": 0,
        "disabled": 0,
        "unique_devices": len({row.get("ID") for row in rows if row.get("ID")} ),
        "reasons": {},
        "last_event": None,
        "average_interval": None,
    }

    for row in rows:
        result = (row.get("Result") or "").upper()
        action = (row.get("Action") or "").upper()
        reason = row.get("Reason") or "Unknown"

        if result == "TRUSTED":
            summary["trusted"] += 1
        elif result == "SAFE":
            summary["safe"] += 1
        elif result == "UNTRUSTED":
            summary["untrusted"] += 1

        if action == "BLOCKED":
            summary["blocked"] += 1
        elif action == "DISABLED":
            summary["disabled"] += 1

        summary["reasons"][reason] = summary["reasons"].get(reason, 0) + 1

    sorted_rows = sorted(
        [r for r in rows if r.get("parsed_time")],
        key=lambda r: r["parsed_time"],
    )
    if sorted_rows:
        summary["last_event"] = sorted_rows[-1]["parsed_time"]
        intervals = []
        for previous, current in zip(sorted_rows, sorted_rows[1:]):
            delta = current["parsed_time"] - previous["parsed_time"]
            intervals.append(delta.total_seconds())
        if intervals:
            summary["average_interval"] = sum(intervals) / len(intervals)

    return summary


@app.route("/")
def dashboard():
    rows = load_log_rows()
    rows = sorted(rows, key=lambda r: r.get("parsed_time") or datetime.min, reverse=True)
    summary = build_summary(rows)
    whitelist = load_whitelist()

    return render_template(
        "index.html",
        rows=rows,
        summary=summary,
        whitelist=whitelist,
    )


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)
