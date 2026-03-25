# core/operators.py — GA operators: initialisation, crossover, mutation
import numpy as np


def init_population(
    pop_size: int,
    time_slots: int,
    max_solar: np.ndarray,
    max_wind: np.ndarray,
    max_hydro: np.ndarray,
) -> list[np.ndarray]:
    """
    Create a random initial population of schedules.

    Each individual is a (T x 4) array:
        col 0 = solar generation
        col 1 = wind generation
        col 2 = hydro generation
        col 3 = battery action (filled later by battery enforcement)

    Args:
        pop_size:   Number of individuals
        time_slots: Number of hours (T)
        max_solar:  (T,) per-hour solar capacity
        max_wind:   (T,) per-hour wind capacity
        max_hydro:  (T,) per-hour hydro capacity

    Returns:
        List of (T x 4) numpy arrays
    """
    population = []
    for _ in range(pop_size):
        indiv = np.zeros((time_slots, 4))
        indiv[:, 0] = np.random.randint(0, max_solar + 1)
        indiv[:, 1] = np.random.randint(0, max_wind + 1)
        indiv[:, 2] = np.random.randint(0, max_hydro + 1)
        population.append(indiv)
    return population


def crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    Single-point crossover between two parent schedules.

    Args:
        parent1: (T x 4) array
        parent2: (T x 4) array

    Returns:
        child: (T x 4) array combining rows from both parents
    """
    T = parent1.shape[0]
    cut = np.random.randint(1, T)
    return np.vstack((parent1[:cut], parent2[cut:]))


def mutate(
    individual: np.ndarray,
    max_solar: np.ndarray,
    max_wind: np.ndarray,
    max_hydro: np.ndarray,
    mutation_rate: float,
) -> np.ndarray:
    """
    Apply random mutations to an individual schedule.

    For each hour, each source independently has a `mutation_rate` chance
    of being replaced with a new random value within its allowed range.

    Args:
        individual:    (T x 4) array
        max_solar:     (T,) per-hour solar capacity
        max_wind:      (T,) per-hour wind capacity
        max_hydro:     (T,) per-hour hydro capacity
        mutation_rate: Probability of mutating each gene

    Returns:
        Mutated copy of the individual
    """
    child = individual.copy()
    T = child.shape[0]

    mask_s = np.random.rand(T) < mutation_rate
    mask_w = np.random.rand(T) < mutation_rate
    mask_h = np.random.rand(T) < mutation_rate

    if mask_s.any():
        child[mask_s, 0] = np.random.randint(0, max_solar[mask_s] + 1)
    if mask_w.any():
        child[mask_w, 1] = np.random.randint(0, max_wind[mask_w] + 1)
    if mask_h.any():
        child[mask_h, 2] = np.random.randint(0, max_hydro[mask_h] + 1)

    return child
