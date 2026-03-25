# utils/storage.py — Save & load past GA runs (JSON-based, Streamlit Cloud compatible)
import json
import os
import numpy as np
from datetime import datetime

RUNS_FILE = "ga_runs_history.json"


def _serialize(obj):
    """Convert numpy types to native Python for JSON serialization."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    raise TypeError(f"Not serializable: {type(obj)}")


def save_run(
    run_name: str,
    config: dict,
    demand: np.ndarray,
    schedule: np.ndarray,
    soc_list: list,
    battery_action: list,
    fitness_history: list,
) -> None:
    """Append a completed GA run to the history file."""
    runs = load_all_runs()

    entry = {
        "name": run_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "config": {k: (int(v) if isinstance(v, (np.integer,)) else
                       float(v) if isinstance(v, (np.floating,)) else v)
                   for k, v in config.items()},
        "demand": demand.tolist(),
        "schedule": schedule.tolist(),
        "soc_list": soc_list,
        "battery_action": battery_action,
        "fitness_history": fitness_history,
        "final_cost": fitness_history[-1] if fitness_history else None,
    }

    runs.append(entry)
    with open(RUNS_FILE, "w") as f:
        json.dump(runs, f, default=_serialize)


def load_all_runs() -> list[dict]:
    """Load all saved runs from the history file."""
    if not os.path.exists(RUNS_FILE):
        return []
    try:
        with open(RUNS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def delete_run(index: int) -> None:
    """Delete a run by its index in the history list."""
    runs = load_all_runs()
    if 0 <= index < len(runs):
        runs.pop(index)
        with open(RUNS_FILE, "w") as f:
            json.dump(runs, f)


def clear_all_runs() -> None:
    """Delete all saved runs."""
    if os.path.exists(RUNS_FILE):
        os.remove(RUNS_FILE)


def get_run_names() -> list[str]:
    """Return list of saved run names with timestamps."""
    runs = load_all_runs()
    return [f"{r['name']}  [{r['timestamp']}]" for r in runs]
