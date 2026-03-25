# ui/live_progress.py — Real-time GA progress: bar, fitness chart, live schedule preview
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def render_live_progress(progress: dict, demand: np.ndarray) -> None:
    """
    Update all live UI elements with the latest GA progress snapshot.

    Call this inside the GA generation loop with each yielded progress dict.

    Args:
        progress: dict yielded by ga_run_live()
        demand:   (T,) demand array for chart overlays
    """
    gen = progress["generation"]
    total = progress["total_generations"]
    cost = progress["best_fitness"]
    history = progress["fitness_history"]
    schedule = progress["best_schedule"]
    soc_list = progress["soc_list"]

    # --- Progress bar ---
    pct = gen / total
    st.session_state["_prog_bar"].progress(pct, text=f"Generation {gen} / {total}  |  Best Cost: {cost:.1f}")

    # --- Fitness convergence chart ---
    fig_f, ax_f = plt.subplots(figsize=(10, 2.5))
    ax_f.plot(range(1, len(history) + 1), history, color="#ef5350", linewidth=1.5)
    ax_f.fill_between(range(1, len(history) + 1), history, alpha=0.15, color="#ef5350")
    ax_f.set_xlabel("Generation", fontsize=9)
    ax_f.set_ylabel("Cost (lower = better)", fontsize=9)
    ax_f.set_title("GA Convergence — Fitness Over Generations", fontsize=10)
    ax_f.tick_params(labelsize=8)
    fig_f.tight_layout()
    st.session_state["_fitness_chart"].pyplot(fig_f)
    plt.close(fig_f)

    # --- Animated generation mix bar chart ---
    hours = np.arange(1, len(demand) + 1)
    solar = schedule[:, 0]
    wind  = schedule[:, 1]
    hydro = schedule[:, 2]
    batt  = np.clip(schedule[:, 3], 0, None)

    fig_g, ax_g = plt.subplots(figsize=(10, 3))
    ax_g.bar(hours, solar, label="Solar ☀️",  color="#f4a522")
    ax_g.bar(hours, wind,  bottom=solar,       label="Wind 🌬️",  color="#4fc3f7")
    ax_g.bar(hours, hydro, bottom=solar+wind,  label="Hydro 💧", color="#29b6f6")
    ax_g.bar(hours, batt,  bottom=solar+wind+hydro, label="Battery 🔋", color="#a5d6a7")
    ax_g.plot(hours, demand, "r--o", linewidth=1.5, markersize=3, label="Demand")
    ax_g.set_title(f"Best Schedule (Gen {gen})", fontsize=10)
    ax_g.set_xlabel("Hour", fontsize=9)
    ax_g.set_ylabel("Energy (units)", fontsize=9)
    ax_g.legend(fontsize=8, loc="upper right")
    ax_g.set_xticks(hours)
    ax_g.tick_params(labelsize=8)
    fig_g.tight_layout()
    st.session_state["_gen_chart"].pyplot(fig_g)
    plt.close(fig_g)

    # --- Animated SOC chart ---
    fig_s, ax_s = plt.subplots(figsize=(10, 2))
    ax_s.fill_between(hours, soc_list, alpha=0.3, color="#42a5f5")
    ax_s.plot(hours, soc_list, "b-o", linewidth=1.5, markersize=3)
    ax_s.set_title(f"Battery SOC (Gen {gen})", fontsize=10)
    ax_s.set_xlabel("Hour", fontsize=9)
    ax_s.set_ylabel("SOC (units)", fontsize=9)
    ax_s.set_xticks(hours)
    ax_s.tick_params(labelsize=8)
    fig_s.tight_layout()
    st.session_state["_soc_chart"].pyplot(fig_s)
    plt.close(fig_s)


def init_live_widgets() -> None:
    """
    Create and store Streamlit placeholder widgets in session_state.
    Call once before the GA loop starts.
    """
    st.subheader("🔄 Live Optimization Progress")
    st.session_state["_prog_bar"]     = st.progress(0, text="Starting...")
    st.session_state["_fitness_chart"] = st.empty()
    st.session_state["_gen_chart"]    = st.empty()
    st.session_state["_soc_chart"]    = st.empty()
