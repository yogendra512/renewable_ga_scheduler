# core/fitness.py — Indian Net Metering & Financial Optimizer
import numpy as np

# --- Reliability Penalties ---
# Blackouts are expensive for Indian warehouses/homes
UNMET_WEIGHT = 20.0  

def fitness(schedule: np.ndarray, demand: np.ndarray, config: dict = None) -> float:
    """
    Evaluates the schedule based on Indian Net Metering (On-Grid) economics.
    
    Schedule columns:
    [0:Solar, 1:Wind, 2:Hydro, 3:Grid (Govt), 4:Battery]
    """
    # 1. Energy Balance
    total_supply = schedule.sum(axis=1)
    diff = total_supply - demand
    unmet = np.sum(np.clip(-diff, 0, None))
    
    # 2. Financial Logic (Rupee-based)
    # Defaulting to average Indian commercial rates if not provided in config
    import_rate = 7.5 if config is None else config.get("import_price", 7.5)
    export_rate = 3.5 if config is None else config.get("export_price", 3.5)
    
    # Calculate Import Cost (Power taken from DISCOM)
    grid_import = schedule[:, 3]
    total_import_cost = np.sum(grid_import * import_rate)
    
    # Calculate Export Credits (Net Metering - Selling back to Govt)
    # Only surplus renewable energy (or battery) that exceeds demand is exported
    surplus_energy = np.clip(diff, 0, None)
    total_export_credit = np.sum(surplus_energy * export_rate)
    
    # 3. Final Fitness Calculation
    # We want to minimize (Import Cost - Export Credit)
    net_bill = total_import_cost - total_export_credit
    
    # We return a negative value because the GA tries to MAXIMIZE fitness.
    # Maximizing -(Penalty + Bill) means minimizing blackouts and minimizing the bill.
    return -(UNMET_WEIGHT * unmet + net_bill)