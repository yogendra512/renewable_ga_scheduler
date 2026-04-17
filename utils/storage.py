# utils/storage.py — Save & load past GA runs (Updated for 5-Column Schedules)
import json
import os
import numpy as np
from datetime import datetime

# Streamlit Cloud tip: Using a relative path works, but ensure write permissions
RUNS_FILE = "ga_runs_history.json"


def _serialize(obj):
    """Convert numpy types to native Python for JSON serialization."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, bool):
        return bool(obj)
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
    """Append a completed GA run to the history file, including Grid data."""
    runs = load_all_runs()

    # Create a clean version of config for JSON
    clean_config = {}
    for k, v in config.items():
        if isinstance(v, (np.ndarray, list)):
            continue # Don't save large arrays inside the config block
        if hasattr(v, 'name'): # Handle file upload objects
            clean_config[k] = str(v.name)
        else:
            try:
                # Use the _serialize logic for single values
                if isinstance(v, (np.integer, np.floating)):
                    clean_config[k] = _serialize(v)
                else:
                    clean_config[k] = v
            except:
                clean_config[k] = str(v)

    entry = {
        "name": run_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "config": clean_config,
        "demand": demand.tolist(),
        "schedule": schedule.tolist(), # This now contains 5 columns!
        "soc_list": soc_list,
        "battery_action": battery_action,
        "fitness_history": fitness_history,
        "final_cost": float(fitness_history[-1]) if fitness_history else 0.0,
    }

    runs.append(entry)
    
    # Ensure directory exists (useful for local development)
    directory = os.path.dirname(RUNS_FILE)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(RUNS_FILE, "w") as f:
        json.dump(runs, f, default=_serialize, indent=2)


def load_all_runs() -> list[dict]:
    """Load all saved runs from the history file."""
    if not os.path.exists(RUNS_FILE):
        return []
    try:
        with open(RUNS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def delete_run(index: int) -> None:
    """Delete a run by its index in the history list."""
    runs = load_all_runs()
    if 0 <= index < len(runs):
        runs.pop(index)
        with open(RUNS_FILE, "w") as f:
            json.dump(runs, f, default=_serialize)


def clear_all_runs() -> None:
    """Delete all saved runs."""
    if os.path.exists(RUNS_FILE):
        os.remove(RUNS_FILE)


def get_run_names() -> list[str]:
    """Return list of saved run names with timestamps."""
    runs = load_all_runs()
    return [f"{r['name']}  [{r['timestamp']}]" for r in runs]