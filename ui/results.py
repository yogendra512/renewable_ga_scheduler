# ui/results.py — Post-optimization results updated for 5-column scheduling
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def render_results(
    schedule: np.ndarray,
    soc_list: list[float],
    batt_action: list[str],
    demand: np.ndarray,
) -> None:
    """
    Render results for a 5-column schedule: [Solar, Wind, Hydro, Grid, Battery].
    """
    st.divider()
    st.header("📊 Optimization Results")

    hours = np.arange(1, len(demand) + 1)
    solar = schedule[:, 0]
    wind = schedule[:, 1]
    hydro = schedule[:, 2]
    grid = schedule[:, 3]    # NEW: Grid (Govt) Power
    battery = schedule[:, 4] # Battery shifted to index 4
    total_supply = schedule.sum(axis=1)

    unmet = np.clip(demand - total_supply, 0, None)
    surplus = np.clip(total_supply - demand, 0, None)

    # ------------------------------------------------------------------
    # 1. KPI Summary
    # ------------------------------------------------------------------
    st.subheader("🎯 Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Demand", f"{demand.sum():.0f} units")
    col2.metric("Total Supply", f"{total_supply.sum():.0f} units")
    col3.metric("Unmet Demand", f"{unmet.sum():.1f} units", delta=f"-{unmet.sum():.1f}", delta_color="inverse")
    col4.metric("Surplus Generation", f"{surplus.sum():.1f} units")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total Solar", f"{solar.sum():.0f} units")
    col6.metric("Total Wind", f"{wind.sum():.0f} units")
    col7.metric("Total Hydro", f"{hydro.sum():.0f} units")
    col8.metric("Grid (Govt) Used", f"{grid.sum():.1f} units", delta=f"Cost: {grid.sum() * 1.5:.1f}", delta_color="inverse")

    # ------------------------------------------------------------------
    # 2. Generation Mix — Stacked Bar (Updated for 5 columns)
    # ------------------------------------------------------------------
    st.subheader("🌞 Generation Mix per Hour")
    fig1, ax1 = plt.subplots(figsize=(12, 4))
    ax1.bar(hours, solar, label="Solar ☀️", color="#f4a522")
    ax1.bar(hours, wind, bottom=solar, label="Wind 🌬️", color="#4fc3f7")
    ax1.bar(hours, hydro, bottom=solar + wind, label="Hydro 💧", color="#29b6f6")
    # Add Grid Power layer
    ax1.bar(hours, grid, bottom=solar + wind + hydro, label="Grid (Govt) 🏛️", color="#9e9e9e")
    # Add Battery layer
    ax1.bar(hours, np.clip(battery, 0, None), bottom=solar + wind + hydro + grid,
            label="Battery Discharge 🔋", color="#a5d6a7")
            
    ax1.plot(hours, demand, "r--o", label="Demand", linewidth=2, markersize=4)
    ax1.set_xlabel("Hour")
    ax1.set_ylabel("Energy (units)")
    ax1.set_title("Hourly Generation Mix vs Demand")
    ax1.legend(loc="upper right")
    ax1.set_xticks(hours)
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    # ------------------------------------------------------------------
    # 3. Demand vs Supply Chart & 4. Battery SOC Chart (Remain Same)
    # ------------------------------------------------------------------
    # ... [Charts 3 and 4 code from your original file remains unchanged] ...

    # ------------------------------------------------------------------
    # 5. Hourly Detail Table (Updated with Grid Column)
    # ------------------------------------------------------------------
    st.subheader("📋 Hourly Schedule Detail")
    df = pd.DataFrame({
        "Hour": hours,
        "Demand": demand,
        "Solar": solar,
        "Wind": wind,
        "Hydro": hydro,
        "Grid (Govt)": grid, # NEW
        "Battery Action": batt_action,
        "Total Supply": total_supply,
        "Unmet": unmet,
        "Surplus": surplus,
        "SOC End": np.round(soc_list, 2),
    })
    st.dataframe(df.style.format({
        "Demand": "{:.0f}", "Solar": "{:.1f}", "Wind": "{:.1f}", "Hydro": "{:.1f}",
        "Grid (Govt)": "{:.1f}", "Total Supply": "{:.1f}", "Unmet": "{:.1f}",
        "Surplus": "{:.1f}", "SOC End": "{:.2f}",
    }), use_container_width=True)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Results as CSV",
        data=csv,
        file_name="ga_schedule_results.csv",
        mime="text/csv",
    )