# ui/results.py — Professional "Agentic" UI for Indian Net Metering
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

def render_results(
    schedule: np.ndarray,
    soc_list: list[float],
    batt_action: list[str],
    demand: np.ndarray,
) -> None:
    """
    Render professional, interactive results focusing on Indian Net Metering economics.
    Uses Plotly for 2026 agentic insight.
    """
    # 0. Load Configuration and Financials
    config = st.session_state.get("config", {})
    import_rate = config.get("import_price", 7.5)
    export_rate = config.get("export_price", 3.5)
    
    # Process Energy Data
    hours = np.arange(1, len(demand) + 1)
    solar = schedule[:, 0]
    wind = schedule[:, 1]
    hydro = schedule[:, 2]
    grid_import = schedule[:, 3]
    battery = schedule[:, 4]
    total_supply = schedule.sum(axis=1)

    unmet = np.clip(demand - total_supply, 0, None)
    # Surplus calculation for Net Metering export
    surplus_export = np.clip(total_supply - demand, 0, None)

    st.divider()
    st.header("⚡ Indian Grid Command Center")
    st.markdown("Optimization complete. The Genetic Algorithm has calculated the most profitable energy schedule for your warehouse.")

    # 1. 💰 Financial & Agentic Insight Row (KPI Row)
    # This row replaces basic metrics with focused profit/loss calculations.
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    # Financial Calculations
    total_bought = grid_import.sum()
    total_sold = surplus_export.sum()
    
    bill_before_credit = total_bought * import_rate
    net_metering_credit = total_sold * export_rate
    final_bill = bill_before_credit - net_metering_credit

    # Dummy baseline for "savings" calculation (e.g., if warehouse ran 100% on grid)
    baseline_bill = demand.sum() * import_rate
    total_savings = baseline_bill - final_bill

    with kpi_col1:
        st.metric(
            label="Net Payable Amount", 
            value=f"₹{max(0, final_bill):.2f}", 
            delta=f"₹{net_metering_credit:.2f} credits",
            help="Final amount to pay to the electricity board after Net Metering credits."
        )
    with kpi_col2:
        st.metric(
            label="DISCOM Bill (Import Cost)", 
            value=f"₹{bill_before_credit:.2f}", 
            delta=f"{total_bought:.0f} units bought",
            delta_color="inverse",
            help="Cost of power pulled from the govt grid."
        )
    with kpi_col3:
        # AGENTIC INSIGHT: Shows the warehouse owner the real value of the optimizer
        st.metric(
            label="Agentic Savings Insight", 
            value=f"₹{total_savings:.2f}", 
            delta=f"{(total_savings/baseline_bill*100) if baseline_bill>0 else 0:.1f}% vs. No Solar",
            help="Approximate savings achieved by the GA compared to a warehouse with no solar plant."
        )

    # Style the metrics to look professional
    style_metric_cards(
        background_color="#1e2130", 
        border_left_color="#00d4ff", 
        box_shadow=True
    )

    # 2. 🌞 Generation Mix & Net Metering Balance (Interactive)
    # We use Plotly to make the chart interactive and show the energy 'flow'.
    st.subheader("📊 Hourly Energy Flow & Net Metering Balance")
    
    fig = go.Figure()

    # Add Energy Sources (Stacked Bar)
    fig.add_trace(go.Bar(x=hours, y=solar, name="Solar ☀️", marker_color="#f4a522"))
    fig.add_trace(go.Bar(x=hours, y=wind, name="Wind 🌬️", marker_color="#4fc3f7"))
    fig.add_trace(go.Bar(x=hours, y=hydro, name="Hydro 💧", marker_color="#29b6f6"))
    
    # Highlight Export (Net Metering) as negative bars
    fig.add_trace(go.Bar(
        x=hours, 
        y=-surplus_export, 
        name="Sold to Govt ⬆️ (Export)", 
        marker_color="#ef5350",
        hovertemplate="Units Sold: %{y:.1f}<br>Credit: ₹%{text:.2f}",
        text=surplus_export * export_rate
    ))

    # Highlight Import as standard stacked bars
    fig.add_trace(go.Bar(x=hours, y=grid_import, name="Grid (Govt) 🏛️", marker_color="#9e9e9e"))
    
    # Add Battery (Discharge)
    fig.add_trace(go.Bar(x=hours, y=np.clip(battery, 0, None), name="Battery Discharge 🔋", marker_color="#a5d6a7"))

    # Add Demand (Line)
    fig.add_trace(go.Scatter(
        x=hours, y=demand, name="Demand", mode='lines+markers', line=dict(color="#f44336", width=2)
    ))

    fig.update_layout(
        barmode='relative', # Allows stacked bars with positive/negative values
        title="Interactive Generation Mix vs. Warehouse Demand",
        xaxis_title="Hour",
        yaxis_title="Energy Units (kWh)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        hovermode="x unified", # Shows all values for a single hour when hovering
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # 3. 🔋 Battery & SOC Monitor (Optional Chart to keep UI clean)
    st.subheader("🔋 Battery Performance Monitor")
    fig_soc = go.Figure()
    fig_soc.add_trace(go.Scatter(x=hours, y=soc_list, name="SOC (%)", line=dict(color="#00e676", width=3), fill='tozeroy'))
    fig_soc.update_layout(title="Battery State of Charge (SOC) End of Hour", xaxis_title="Hour", yaxis_title="SOC (%)", template="plotly_dark", height=300)
    st.plotly_chart(fig_soc, use_container_width=True)

    # 4. 📋 Hourly Detail Table (Updated with Rupee formatting)
    st.subheader("📋 Hourly Schedule & Billing Detail")
    df = pd.DataFrame({
        "Hour": hours,
        "Demand": demand,
        "Solar": solar,
        "Grid Import": grid_import,
        "Export (Net)": surplus_export,
        "Battery": battery,
        "SOC End": np.round(soc_list, 2),
        "Hourly Bill (₹)": (grid_import * import_rate) - (surplus_export * export_rate)
    })
    
    # Professional formatting for the table
    st.dataframe(df.style.format({
        "Demand": "{:.0f}", "Solar": "{:.1f}", "Grid Import": "{:.1f}", 
        "Export (Net)": "{:.1f}", "Battery": "{:.1f}", "SOC End": "{:.2f}",
        "Hourly Bill (₹)": "{:+.2f}" # Format Rupees with dynamic sign
    }).background_gradient(cmap='RdYlGn', subset=['Hourly Bill (₹)'], vmin=-50, vmax=50), # Add color heat map for profitability
    use_container_width=True)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Professional Indian Grid Report",
        data=csv,
        file_name="indian_grid_optimization.csv",
        mime="text/csv",
    )