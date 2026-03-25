# core/fitness.py — Fitness / objective function for GA
import numpy as np

# Penalty weights
UNMET_WEIGHT = 2.0    # Unmet demand is heavily penalised (blackout cost)
SURPLUS_WEIGHT = 0.5  # Surplus generation is lightly penalised (wasted energy)


def fitness(schedule: np.ndarray, demand: np.ndarray) -> float:
    """
    Evaluate the quality of an energy schedule.

    Higher (less negative) score = better schedule.

    Args:
        schedule: (T x 4) array [solar, wind, hydro, battery]
        demand:   (T,) demand vector

    Returns:
        Scalar fitness score (always <= 0; 0 means perfect balance)
    """
    total_supply = schedule.sum(axis=1)
    diff = total_supply - demand

    unmet = np.sum(np.clip(-diff, 0, None))    # hours where supply < demand
    surplus = np.sum(np.clip(diff, 0, None))   # hours where supply > demand

    return -(UNMET_WEIGHT * unmet + SURPLUS_WEIGHT * surplus)
