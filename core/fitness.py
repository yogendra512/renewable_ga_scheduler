# core/fitness.py — Priority and Cost-based Fitness Function
import numpy as np

# --- Penalty weights ---
# Unmet demand is the highest priority (blackout prevention)
UNMET_WEIGHT = 5.0   
# Surplus is penalized to prevent wasting renewable energy
SURPLUS_WEIGHT = 0.5 

# --- Source Cost weights ---
# Solar, Wind, and Hydro are 0 (Free/Priority)
# Grid Power has a cost, so we penalize its usage to make it the last resort
GRID_COST_WEIGHT = 1.5 

def fitness(schedule: np.ndarray, demand: np.ndarray) -> float:
    """
    Evaluate schedule quality based on demand fulfillment and cost.
    
    Schedule columns:
    [0: Solar, 1: Wind, 2: Hydro, 3: Grid (Govt), 4: Battery]
    """
    # Calculate total supply across all 5 sources
    total_supply = schedule.sum(axis=1)
    diff = total_supply - demand

    # Calculate energy imbalances
    unmet = np.sum(np.clip(-diff, 0, None))   
    surplus = np.sum(np.clip(diff, 0, None))  
    
    # Calculate "Monetary" cost of using Grid Power (Column index 3)
    grid_usage = np.sum(schedule[:, 3])
    grid_penalty = grid_usage * GRID_COST_WEIGHT

    # Total score (Higher/Less Negative is better)
    # The GA will now try to reduce grid_penalty while keeping unmet at 0
    return -(UNMET_WEIGHT * unmet + SURPLUS_WEIGHT * surplus + grid_penalty)