# ui/compare.py — Side-by-side comparison of multiple saved GA runs
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utils.storage import load_all_runs, delete_run, clear_all_runs


def render_compare_page() -> None:
    """Render the Compare Runs tab: convergence overlay, KPI table, and schedule comparison."""
    st.header("🆚 Compare GA Runs")

    runs = load_all_runs()
    if not runs:
        st.info("No saved runs yet. Run the optimizer and save a run first.")
        return

    # Run selector
    run_labels = [f"{r['name']}  [{r['timestamp']}]" for r in runs]
    selected = st.multiselect(
        "Select runs to compare (2 or more recommended):",
        options=run_labels,
        default=run_labels[:min(3, len(run_labels))],
    )
    if not selected:
        st.warning("Select at least one run to display.")
        return

    chosen = [runs[run_labels.index(s)] for s in selected]

    # ------------------------------------------------------------------
    # 1. Convergence overlay
    # ------------------------------------------------------------------
    st.subheader("📉 Fitness Convergence")
    fig_c, ax_c = plt.subplots(figsize=(11, 3.5))
    colors = plt.cm.tab10.colors
    for i, run in enumerate(chosen):
        h = run["fitness_history"]
        ax_c.plot(range(1, len(h) + 1), h, label=run["name"],
                  color=colors[i % 10], linewidth=1.8)
    ax_c.set_xlabel("Generation")
    ax_c.set_ylabel("Cost (lower = better)")
    ax_c.set_title("Convergence Comparison")
    ax_c.legend()
    fig_c.tight_layout()
    st.pyplot(fig_c)
    plt.close(fig_c)

    # ------------------------------------------------------------------
    # 2. KPI summary table
    # ------------------------------------------------------------------
    st.subheader("📊 Key Metrics Comparison")
    rows = []
    for run in chosen:
        demand   = np.array(run["demand"])
        schedule = np.array(run["schedule"])
        total_supply = schedule.sum(axis=1)
        unmet   = float(np.clip(demand - total_supply, 0, None).sum())
        surplus = float(np.clip(total_supply - demand, 0, None).sum())
        rows.append({
            "Run": run["name"],
            "Timestamp": run["timestamp"],
            "Generations": run["config"].get("generations", "—"),
            "Pop Size": run["config"].get("pop_size", "—"),
            "Mutation Rate": run["config"].get("mutation_rate", "—"),
            "Final Cost": round(run["final_cost"], 2) if run["final_cost"] else "—",
            "Unmet Demand": round(unmet, 1),
            "Surplus": round(surplus, 1),
            "Total Solar": round(float(schedule[:, 0].sum()), 1),
            "Total Wind": round(float(schedule[:, 1].sum()), 1),
            "Total Hydro": round(float(schedule[:, 2].sum()), 1),
        })
    df_kpi = pd.DataFrame(rows).set_index("Run")
    st.dataframe(df_kpi, use_container_width=True)

    # ------------------------------------------------------------------
    # 3. Generation mix comparison (one chart per run)
    # ------------------------------------------------------------------
    st.subheader("🌞 Generation Mix Comparison")
    n = len(chosen)
    fig_m, axes = plt.subplots(1, n, figsize=(6 * n, 4), sharey=True)
    if n == 1:
        axes = [axes]

    for ax, run in zip(axes, chosen):
        demand   = np.array(run["demand"])
        schedule = np.array(run["schedule"])
        hours    = np.arange(1, len(demand) + 1)
        solar, wind, hydro = schedule[:, 0], schedule[:, 1], schedule[:, 2]
        batt = np.clip(schedule[:, 3], 0, None)
        ax.bar(hours, solar, color="#f4a522", label="Solar")
        ax.bar(hours, wind,  bottom=solar,              color="#4fc3f7", label="Wind")
        ax.bar(hours, hydro, bottom=solar+wind,         color="#29b6f6", label="Hydro")
        ax.bar(hours, batt,  bottom=solar+wind+hydro,   color="#a5d6a7", label="Battery")
        ax.plot(hours, demand, "r--o", linewidth=1.5, markersize=3, label="Demand")
        ax.set_title(run["name"], fontsize=9)
        ax.set_xlabel("Hour", fontsize=8)
        ax.tick_params(labelsize=7)
        if ax is axes[0]:
            ax.set_ylabel("Energy (units)", fontsize=8)
            ax.legend(fontsize=7, loc="upper right")

    fig_m.tight_layout()
    st.pyplot(fig_m)
    plt.close(fig_m)

    # ------------------------------------------------------------------
    # 4. SOC comparison
    # ------------------------------------------------------------------
    st.subheader("🔋 Battery SOC Comparison")
    fig_soc, ax_soc = plt.subplots(figsize=(11, 3))
    for i, run in enumerate(chosen):
        soc = run["soc_list"]
        hours = np.arange(1, len(soc) + 1)
        ax_soc.plot(hours, soc, label=run["name"], color=colors[i % 10], linewidth=1.8, marker="o", markersize=3)
    ax_soc.set_xlabel("Hour")
    ax_soc.set_ylabel("SOC (units)")
    ax_soc.set_title("Battery SOC Over Time")
    ax_soc.legend()
    fig_soc.tight_layout()
    st.pyplot(fig_soc)
    plt.close(fig_soc)

    # ------------------------------------------------------------------
    # 5. Manage saved runs
    # ------------------------------------------------------------------
    st.subheader("🗂️ Manage Saved Runs")
    col1, col2 = st.columns([3, 1])
    with col1:
        del_label = st.selectbox("Select run to delete:", run_labels)
    with col2:
        st.write("")
        st.write("")
        if st.button("🗑️ Delete Run"):
            delete_run(run_labels.index(del_label))
            st.success(f"Deleted: {del_label}")
            st.rerun()

    if st.button("⚠️ Clear ALL Saved Runs", type="secondary"):
        clear_all_runs()
        st.success("All runs cleared.")
        st.rerun()
