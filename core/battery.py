# core/battery.py — Updated for Grid Priority and 5-Column Schedule
import numpy as np


def enforce_battery_constraints(
    schedule: np.ndarray,
    demand: np.ndarray,
    battery_cap: float,
    charge_rate: float,
    discharge_rate: float,
    initial_soc: float,
) -> tuple[np.ndarray, list[float], list[str]]:
    """
    Simulate battery behavior with priority:
    1. Renewables (Solar, Wind, Hydro)
    2. Grid Power (Govt)
    3. Battery (Backup/Storage)

    Args:
        schedule: (T x 5) [solar, wind, hydro, grid, battery]
    """
    soc = float(initial_soc)
    new_schedule = schedule.astype(float).copy()
    soc_list: list[float] = []
    battery_action: list[str] = []

    for t in range(schedule.shape[0]):
        # Calculate available power before using the battery
        # Renewables (Indices 0, 1, 2) + Grid Power (Index 3)
        renewables = float(new_schedule[t, 0] + new_schedule[t, 1] + new_schedule[t, 2])
        grid_power = float(new_schedule[t, 3])
        
        total_gen = renewables + grid_power
        diff = demand[t] - total_gen

        if diff > 0:
            # Demand exceeds combined supply — discharge battery
            discharge = min(diff, soc, discharge_rate)
            new_schedule[t, 4] = discharge # Battery is now at index 4
            soc -= discharge
            battery_action.append(f"+{discharge:.1f} (discharge)" if discharge > 0 else "0")

        elif diff < 0:
            # Surplus exists — use it to charge battery
            # Logic: Charge primarily from free renewable surplus
            charge = min(-diff, battery_cap - soc, charge_rate)
            new_schedule[t, 4] = -charge
            soc += charge
            battery_action.append(f"-{charge:.1f} (charge)" if charge > 0 else "0")

        else:
            new_schedule[t, 4] = 0
            battery_action.append("0")

        # Ensure SOC stays within physical limits
        soc = max(0.0, min(soc, battery_cap))
        soc_list.append(soc)

    return new_schedule, soc_list, battery_action