# ui/input_table.py — Editable per-hour input data table
import numpy as np
import pandas as pd
import streamlit as st


def render_input_table(
    time_slots: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Render the editable per-hour input table and return numpy arrays.

    Resets the table when time_slots changes.

    Args:
        time_slots: Number of hours to simulate

    Returns:
        demand, max_solar, max_wind, max_hydro — each a (T,) float array
    """
    # Reset if time_slots changed
    if (
        "input_df" not in st.session_state
        or st.session_state.get("time_slots") != time_slots
    ):
        st.session_state.input_df = pd.DataFrame({
            "Hour": list(range(1, time_slots + 1)),
            "Demand": np.random.randint(80, 180, time_slots),
            "Max Solar": np.random.randint(20, 100, time_slots),
            "Max Wind": np.random.randint(10, 80, time_slots),
            "Max Hydro": np.random.randint(5, 50, time_slots),
        })
        st.session_state.time_slots = time_slots

    st.subheader("📥 Input Demand & Max Generation")
    edited = st.data_editor(
        st.session_state.input_df,
        num_rows="dynamic",
        key="input_editor",
        use_container_width=True,
    )
    st.session_state.input_df = edited

    # Extract and sanitise
    demand = np.maximum(edited["Demand"].values.astype(float), 0)
    max_solar = np.maximum(edited["Max Solar"].values.astype(float), 0)
    max_wind = np.maximum(edited["Max Wind"].values.astype(float), 0)
    max_hydro = np.maximum(edited["Max Hydro"].values.astype(float), 0)

    return demand, max_solar, max_wind, max_hydro
