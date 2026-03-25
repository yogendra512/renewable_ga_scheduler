# ui/results.py — Post-optimization results: metrics, charts, and tables
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
    Render all result panels after GA optimization completes.

    Sections:
        1. Summary KPI metrics
        2. Generation mix stacked bar chart
        3. Demand vs Total Supply line chart
        4. Battery SOC over time
        5. Detailed hourly results table

    Args:
        schedule:     (T x 4) best schedule [solar, wind, hydro, battery]
        soc_list:     State-of-charge at end of each hour
        batt_action:  Human-readable battery action per hour
        demand:       (T,) hourly demand
    """
    st.divider()
    st.header("📊 Optimization Results")

    hours = np.arange(1, len(demand) + 1)
    solar = schedule[:, 0]
    wind = schedule[:, 1]
    hydro = schedule[:, 2]
    battery = schedule[:, 3]
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
    col8.metric("Net Battery", f"{battery.sum():.1f} units")

    # ------------------------------------------------------------------
    # 2. Generation Mix — Stacked Bar
    # ------------------------------------------------------------------
    st.subheader("🌞 Generation Mix per Hour")
    fig1, ax1 = plt.subplots(figsize=(12, 4))
    ax1.bar(hours, solar, label="Solar ☀️", color="#f4a522")
    ax1.bar(hours, wind, bottom=solar, label="Wind 🌬️", color="#4fc3f7")
    ax1.bar(hours, hydro, bottom=solar + wind, label="Hydro 💧", color="#29b6f6")
    ax1.bar(hours, np.clip(battery, 0, None), bottom=solar + wind + hydro,
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
    # 3. Demand vs Supply
    # ------------------------------------------------------------------
    st.subheader("⚖️ Demand vs Total Supply")
    fig2, ax2 = plt.subplots(figsize=(12, 3))
    ax2.fill_between(hours, demand, total_supply,
                     where=(total_supply >= demand), alpha=0.3,
                     color="green", label="Surplus")
    ax2.fill_between(hours, demand, total_supply,
                     where=(total_supply < demand), alpha=0.3,
                     color="red", label="Unmet Demand")
    ax2.plot(hours, demand, "r-o", label="Demand", linewidth=2, markersize=4)
    ax2.plot(hours, total_supply, "g-s", label="Total Supply", linewidth=2, markersize=4)
    ax2.set_xlabel("Hour")
    ax2.set_ylabel("Energy (units)")
    ax2.set_title("Demand vs Total Supply Balance")
    ax2.legend()
    ax2.set_xticks(hours)
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # ------------------------------------------------------------------
    # 4. Battery SOC
    # ------------------------------------------------------------------
    st.subheader("🔋 Battery State of Charge (SOC)")
    fig3, ax3 = plt.subplots(figsize=(12, 3))
    ax3.fill_between(hours, soc_list, alpha=0.3, color="#42a5f5")
    ax3.plot(hours, soc_list, "b-o", linewidth=2, markersize=4)
    ax3.set_xlabel("Hour")
    ax3.set_ylabel("SOC (units)")
    ax3.set_title("Battery State of Charge Over Time")
    ax3.set_xticks(hours)
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    # ------------------------------------------------------------------
    # 5. Hourly Detail Table
    # ------------------------------------------------------------------
    st.subheader("📋 Hourly Schedule Detail")
    df = pd.DataFrame({
        "Hour": hours,
        "Demand": demand,
        "Solar": solar,
        "Wind": wind,
        "Hydro": hydro,
        "Battery Action": batt_action,
        "Total Supply": total_supply,
        "Unmet": unmet,
        "Surplus": surplus,
        "SOC End": np.round(soc_list, 2),
    })
    st.dataframe(df.style.format({
        "Demand": "{:.0f}",
        "Solar": "{:.1f}",
        "Wind": "{:.1f}",
        "Hydro": "{:.1f}",
        "Total Supply": "{:.1f}",
        "Unmet": "{:.1f}",
        "Surplus": "{:.1f}",
        "SOC End": "{:.2f}",
    }), use_container_width=True)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Results as CSV",
        data=csv,
        file_name="ga_schedule_results.csv",
        mime="text/csv",
    )
