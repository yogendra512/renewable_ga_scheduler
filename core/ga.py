# core/ga.py — GA runner updated for System Architecture & Indian Net Metering
import numpy as np
from typing import Generator
from core.battery import enforce_battery_constraints
from core.fitness import fitness
from core.operators import init_population, crossover, mutate


def ga_run_live(
    demand: np.ndarray,
    max_solar: np.ndarray,
    max_wind: np.ndarray,
    max_hydro: np.ndarray,
    max_grid: np.ndarray,
    battery_cap: float,
    init_soc: float,
    charge_rate: float,
    discharge_rate: float,
    pop_size: int,
    generations: int,
    mutation_rate: float,
    elitism_frac: float,
    config: dict = None,  
    yield_every: int = 5,
) -> Generator[dict, None, None]:
    """
    GA runner yielding progress updates. 
    Passes config to battery and fitness logic to respect System Architecture.
    """
    T = len(demand)
    population = init_population(pop_size, T, max_solar, max_wind, max_hydro, max_grid)

    best_score = -1e12
    best_adj = None
    best_soc: list[float] = []
    elitism_count = max(1, int(pop_size * elitism_frac))
    fitness_history: list[float] = []

    for gen in range(int(generations)):
        scored = []
        for indiv in population:
            # UPDATED: Now passing config to enforce System Type (Standard/Hybrid/Off-Grid)
            adj, soc_list, _ = enforce_battery_constraints(
                indiv, demand, battery_cap, charge_rate, discharge_rate, init_soc, config=config
            )
            
            # Passing config for Rupee-based fitness
            sc = fitness(adj, demand, config=config)
            
            scored.append((sc, indiv, adj, soc_list))
            if sc > best_score:
                best_score = sc
                best_adj = adj.copy()
                best_soc = soc_list.copy()

        scored.sort(key=lambda x: x[0], reverse=True)
        fitness_history.append(-best_score)

        new_pop = [x[2] for x in scored[:elitism_count]]
        top_half = [x[1] for x in scored[:max(2, pop_size // 2)]]
        
        while len(new_pop) < pop_size:
            p1, p2 = np.random.choice(len(top_half), 2, replace=False)
            child = crossover(top_half[p1], top_half[p2])
            child = mutate(child, max_solar, max_wind, max_hydro, max_grid, mutation_rate)
            new_pop.append(child)
        population = new_pop

        # Yield progress updates to the UI
        if (gen + 1) % yield_every == 0 or gen == int(generations) - 1:
            # Re-run battery logic for best individual to get battery_action strings
            _, _, batt_action = enforce_battery_constraints(
                best_adj, demand, battery_cap, charge_rate, discharge_rate, init_soc, config=config
            )
            yield {
                "generation": gen + 1,
                "total_generations": int(generations),
                "best_fitness": -best_score, 
                "fitness_history": fitness_history.copy(),
                "best_schedule": best_adj.copy(),
                "soc_list": best_soc.copy(),
                "battery_action": batt_action,
                "done": (gen == int(generations) - 1),
            }

def ga_run(
    demand, max_solar, max_wind, max_hydro, max_grid,
    battery_cap, init_soc, charge_rate, discharge_rate,
    pop_size, generations, mutation_rate, elitism_frac,
    config=None, 
):
    """Blocking wrapper for the live runner."""
    result = None
    for result in ga_run_live(
        demand, max_solar, max_wind, max_hydro, max_grid,
        battery_cap, init_soc, charge_rate, discharge_rate,
        pop_size, generations, mutation_rate, elitism_frac,
        config=config
    ):
        pass
    return result["best_schedule"], result["soc_list"], result["battery_action"]