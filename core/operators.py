# core/operators.py — GA operators updated for 5-column scheduling (Solar, Wind, Hydro, Grid, Battery)
import numpy as np


def init_population(
    pop_size: int,
    time_slots: int,
    max_solar: np.ndarray,
    max_wind: np.ndarray,
    max_hydro: np.ndarray,
    max_grid: np.ndarray,  # Added Grid capacity
) -> list[np.ndarray]:
    """
    Create a random initial population of schedules with 5 columns.

    Cols: 0:Solar, 1:Wind, 2:Hydro, 3:Grid (Govt), 4:Battery (Action)
    """
    population = []
    for _ in range(pop_size):
        # Increased to 5 columns
        indiv = np.zeros((time_slots, 5))
        indiv[:, 0] = np.random.randint(0, max_solar + 1)
        indiv[:, 1] = np.random.randint(0, max_wind + 1)
        indiv[:, 2] = np.random.randint(0, max_hydro + 1)
        indiv[:, 3] = np.random.randint(0, max_grid + 1) # Initialize Grid usage
        population.append(indiv)
    return population


def crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    Single-point crossover between two parent schedules (supports 5 columns).
    """
    T = parent1.shape[0]
    cut = np.random.randint(1, T)
    return np.vstack((parent1[:cut], parent2[cut:]))


def mutate(
    individual: np.ndarray,
    max_solar: np.ndarray,
    max_wind: np.ndarray,
    max_hydro: np.ndarray,
    max_grid: np.ndarray,  # Added Grid capacity
    mutation_rate: float,
) -> np.ndarray:
    """
    Apply random mutations including the new Grid column.
    """
    child = individual.copy()
    T = child.shape[0]

    # Create masks for each of the 4 controllable sources
    mask_s = np.random.rand(T) < mutation_rate
    mask_w = np.random.rand(T) < mutation_rate
    mask_h = np.random.rand(T) < mutation_rate
    mask_g = np.random.rand(T) < mutation_rate # Mask for Grid

    if mask_s.any():
        child[mask_s, 0] = np.random.randint(0, max_solar[mask_s] + 1)
    if mask_w.any():
        child[mask_w, 1] = np.random.randint(0, max_wind[mask_w] + 1)
    if mask_h.any():
        child[mask_h, 2] = np.random.randint(0, max_hydro[mask_h] + 1)
    if mask_g.any():
        child[mask_g, 3] = np.random.randint(0, max_grid[mask_g] + 1) # Mutate Grid usage

    return child