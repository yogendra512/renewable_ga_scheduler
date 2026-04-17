# app.py — Dynamic Renewable GA Scheduler (Final 5-Column Version)
import streamlit as st
import numpy as np
import os

st.set_page_config(
    page_title="Renewable GA Scheduler",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import UI and Core modules
from ui.sidebar import render_sidebar
from ui.input_table import render_input_table
from ui.results import render_results
from ui.live_progress import init_live_widgets, render_live_progress
from ui.compare import render_compare_page
from core.ga import ga_run_live
from utils.storage import save_run

def main():
    st.title("⚡ Renewable Energy Scheduling — GA Optimizer")
    st.markdown(
        "Configure inputs in the sidebar, edit hourly data, then run the optimizer. "
        "Results update **live** as the GA evolves."
    )

    # 1. Render Sidebar and sync to session state
    config = render_sidebar()
    st.session_state.config = config

    # 2. Setup Navigation Tabs
    tab_run, tab_compare = st.tabs(["🚀 Run Optimizer", "🆚 Compare Runs"])

    # ------------------------------------------------------------------
    # TAB 1: Run Optimizer
    # ------------------------------------------------------------------
    with tab_run:
        # Extract 5 arrays from the input table
        demand, max_solar, max_wind, max_hydro, max_grid = render_input_table(
            config["time_slots"], config
        )

        col_btn, col_name = st.columns([2, 3])
        with col_btn:
            run_btn = st.button("🚀 Run GA Optimization", use_container_width=True, type="primary")
        with col_name:
            run_name = st.text_input("Save as (run name):", value="Run 1", label_visibility="collapsed")

        if run_btn:
            init_live_widgets()
            last_progress = None

            try:
                # Execute GA with 5-column priority logic
                for progress in ga_run_live(
                    demand=demand,
                    max_solar=max_solar,
                    max_wind=max_wind,
                    max_hydro=max_hydro,
                    max_grid=max_grid,
                    battery_cap=config["battery_capacity"],
                    init_soc=config["initial_soc"],
                    charge_rate=config["max_charge"],
                    discharge_rate=config["max_discharge"],
                    pop_size=config["pop_size"],
                    generations=config["generations"],
                    mutation_rate=config["mutation_rate"],
                    elitism_frac=config["elitism_frac"],
                    yield_every=max(1, config["generations"] // 40),
                ):
                    render_live_progress(progress, demand)
                    last_progress = progress

                st.success("✅ GA Optimization Completed!")

                # 3. Save the Run (We will update storage.py next to handle this)
                save_run(
                    run_name=run_name,
                    config=config,
                    demand=demand,
                    schedule=last_progress["best_schedule"],
                    soc_list=last_progress["soc_list"],
                    battery_action=last_progress["battery_action"],
                    fitness_history=last_progress["fitness_history"],
                )
                st.caption(f"💾 Run saved as **{run_name}** — view it in the Compare Runs tab.")

                # 4. Render Final Results
                render_results(
                    last_progress["best_schedule"],
                    last_progress["soc_list"],
                    last_progress["battery_action"],
                    demand,
                )

            except Exception as e:
                st.error(f"❌ Error during GA run: {e}")
                raise e

    # ------------------------------------------------------------------
    # TAB 2: Compare Runs
    # ------------------------------------------------------------------
    with tab_compare:
        render_compare_page()

if __name__ == "__main__":
    main()