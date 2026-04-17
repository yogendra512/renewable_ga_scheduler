# ui/input_table.py — Editable per-hour input data table
import numpy as np
import pandas as pd
import streamlit as st

from data.data_fetcher import fetch_data
from data.data_validator import validate_data


def render_input_table(
    time_slots: int,
    config: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Render the editable per-hour input table and return numpy arrays.

    Resets the table when time_slots changes.

    Args:
        time_slots: Number of hours to simulate
        config: Sidebar configuration dict

    Returns:
        demand, max_solar, max_wind, max_hydro — each a (T,) float array
    """

    # ===============================
    # RESET TABLE IF TIME CHANGES
    # ===============================
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

    # ===============================
    # 🌐 FETCH LIVE DATA BUTTON
    # ===============================
    if st.button("⚡ Fetch Live Data"):
        with st.spinner("Fetching data..."):
            try:
                source = config.get("data_source", "Manual")

                if source == "Live Weather API":
                    lat = config.get("latitude", 25.4)
                    lon = config.get("longitude", 81.8)
                    df = fetch_data(lat, lon, time_slots)

                elif source == "CSV Upload":
                    csv_file = config.get("csv_file")
                    if csv_file is None:
                        st.warning("Please upload a CSV file first.")
                        df = None
                    else:
                        df = pd.read_csv(csv_file)

                elif source == "MQTT Sensors":
                    # fallback for now
                    df = fetch_data(25.4, 81.8, time_slots)

                else:
                    # Manual fallback
                    df = fetch_data(25.4, 81.8, time_slots)

                if df is not None:
                    df = validate_data(df)
                    df = df.iloc[:time_slots]

                    # Fix Hour column format
                    df["Hour"] = list(range(1, len(df) + 1))

                    st.session_state.input_df = df
                    st.success(f"✅ Data loaded from {source}")

            except Exception as e:
                st.error(f"Error fetching data: {e}")

    # ===============================
    # EDITABLE TABLE
    # ===============================
    edited = st.data_editor(
        st.session_state.input_df,
        num_rows="dynamic",
        key="input_editor",
        use_container_width=True,
    )
    st.session_state.input_df = edited

    # ===============================
    # EXTRACT ARRAYS (UNCHANGED)
    # ===============================
    demand = np.maximum(edited["Demand"].values.astype(float), 0)
    max_solar = np.maximum(edited["Max Solar"].values.astype(float), 0)
    max_wind = np.maximum(edited["Max Wind"].values.astype(float), 0)
    max_hydro = np.maximum(edited["Max Hydro"].values.astype(float), 0)

    return demand, max_solar, max_wind, max_hydro