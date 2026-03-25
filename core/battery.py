# core/battery.py — Battery constraint enforcement
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
    Simulate battery behavior hour-by-hour and adjust the schedule.

    Args:
        schedule:       (T x 4) array [solar, wind, hydro, battery]
        demand:         (T,) demand vector
        battery_cap:    Maximum battery capacity (units)
        charge_rate:    Max charge per hour
        discharge_rate: Max discharge per hour
        initial_soc:    Starting state of charge

    Returns:
        new_schedule:   Adjusted schedule with battery column filled
        soc_list:       SOC at end of each hour
        battery_action: Human-readable action per hour
    """
    soc = float(initial_soc)
    new_schedule = schedule.astype(float).copy()
    soc_list: list[float] = []
    battery_action: list[str] = []

    for t in range(schedule.shape[0]):
        gen = float(new_schedule[t, 0] + new_schedule[t, 1] + new_schedule[t, 2])
        diff = demand[t] - gen

        if diff > 0:
            # Demand exceeds generation — discharge battery
            discharge = min(diff, soc, discharge_rate)
            new_schedule[t, 3] = discharge
            soc -= discharge
            battery_action.append(f"+{discharge:.1f} (discharge)" if discharge > 0 else "0")

        elif diff < 0:
            # Surplus generation — charge battery
            charge = min(-diff, battery_cap - soc, charge_rate)
            new_schedule[t, 3] = -charge
            soc += charge
            battery_action.append(f"-{charge:.1f} (charge)" if charge > 0 else "0")

        else:
            new_schedule[t, 3] = 0
            battery_action.append("0")

        soc = max(0.0, min(soc, battery_cap))
        soc_list.append(soc)

    return new_schedule, soc_list, battery_action
