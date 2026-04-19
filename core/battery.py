# core/battery.py — Updated for System Architecture Constraints
import numpy as np


def enforce_battery_constraints(
    schedule: np.ndarray,
    demand: np.ndarray,
    battery_cap: float,
    charge_rate: float,
    discharge_rate: float,
    initial_soc: float,
    config: dict = None  # Added config to check system type
) -> tuple[np.ndarray, list[float], list[str]]:
    """
    Simulate battery behavior based on system architecture.
    Handles 'Standard On-Grid' by disabling battery logic.
    """
    
    # Check if system type allows battery usage
    system_type = config.get("system_type", "Hybrid (On-Grid + Battery)") if config else "Hybrid"
    
    # If standard On-Grid, force battery column to 0 and skip simulation
    if system_type == "Standard On-Grid (No Battery)" or battery_cap <= 0:
        new_schedule = schedule.astype(float).copy()
        new_schedule[:, 4] = 0.0
        return new_schedule, [0.0] * len(demand), ["No Battery"] * len(demand)

    # Proceed with normal battery logic for Hybrid or Off-Grid systems
    soc = float(initial_soc)
    new_schedule = schedule.astype(float).copy()
    soc_list: list[float] = []
    battery_action: list[str] = []

    for t in range(schedule.shape[0]):
        # Priority: 1. Renewables, 2. Grid Power
        renewables = float(new_schedule[t, 0] + new_schedule[t, 1] + new_schedule[t, 2])
        grid_power = float(new_schedule[t, 3])
        
        total_gen = renewables + grid_power
        diff = demand[t] - total_gen

        if diff > 0:
            # Need power -> Discharge battery
            discharge = min(diff, soc, discharge_rate)
            new_schedule[t, 4] = discharge
            soc -= discharge
            battery_action.append(f"+{discharge:.1f} (discharge)" if discharge > 0 else "0")

        elif diff < 0:
            # Excess power -> Charge battery
            charge = min(-diff, battery_cap - soc, charge_rate)
            new_schedule[t, 4] = -charge
            soc += charge
            battery_action.append(f"-{charge:.1f} (charge)" if charge > 0 else "0")

        else:
            new_schedule[t, 4] = 0
            battery_action.append("0")

        soc = max(0.0, min(soc, battery_cap))
        soc_list.append(soc)

    return new_schedule, soc_list, battery_action