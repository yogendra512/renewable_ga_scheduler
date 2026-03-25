# ui/sidebar.py — Sidebar inputs and configuration
import streamlit as st


def render_sidebar() -> dict:
    """
    Render sidebar controls and return all configuration as a dict.

    Returns:
        config: {
            time_slots, battery_capacity, initial_soc,
            max_charge, max_discharge,
            pop_size, generations, mutation_rate, elitism_frac
        }
    """
    st.sidebar.header("⚙️ Simulation Inputs")

    # --- Time ---
    time_slots = st.sidebar.number_input(
        "Number of Hours (Time Slots)", min_value=3, max_value=48, value=12
    )

    # --- Battery ---
    st.sidebar.subheader("🔋 Battery Settings")
    battery_capacity = st.sidebar.number_input(
        "Capacity (units)", min_value=10, max_value=1000, value=100, step=10
    )
    initial_soc = st.sidebar.number_input(
        "Initial SOC (units)", min_value=0, max_value=battery_capacity, value=50, step=1
    )
    max_charge = st.sidebar.number_input(
        "Max Charge/Hour", min_value=1, max_value=500, value=20, step=1
    )
    max_discharge = st.sidebar.number_input(
        "Max Discharge/Hour", min_value=1, max_value=500, value=20, step=1
    )

    # --- GA ---
    st.sidebar.subheader("🧬 Genetic Algorithm Settings")
    pop_size = st.sidebar.number_input(
        "Population Size", min_value=10, max_value=500, value=60, step=10
    )
    generations = st.sidebar.number_input(
        "Generations", min_value=10, max_value=1000, value=200, step=10
    )
    mutation_rate = st.sidebar.slider(
        "Mutation Rate", min_value=0.0, max_value=0.5, value=0.12, step=0.01
    )
    elitism_frac = st.sidebar.slider(
        "Elitism Fraction", min_value=0.0, max_value=0.5, value=0.2, step=0.05
    )

    return {
        "time_slots": int(time_slots),
        "battery_capacity": float(battery_capacity),
        "initial_soc": float(initial_soc),
        "max_charge": float(max_charge),
        "max_discharge": float(max_discharge),
        "pop_size": int(pop_size),
        "generations": int(generations),
        "mutation_rate": float(mutation_rate),
        "elitism_frac": float(elitism_frac),
    }
