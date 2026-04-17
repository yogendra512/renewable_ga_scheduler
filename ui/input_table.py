# ui/input_table.py — Updated for 5-column scheduling (Renewables + Grid)
import numpy as np
import pandas as pd
import streamlit as st

from data.data_fetcher import fetch_data
from data.data_validator import validate_data


def render_input_table(
    time_slots: int,
    config: dict,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Render the editable input table and return 5 numpy arrays.
    Now includes Grid (Govt) Power capacity.
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
            "Max Grid": np.full(time_slots, 100), # Default grid capacity
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
                    if csv_file:
                        df = pd.read_csv(csv_file)
                    else:
                        st.warning("Upload a CSV first.")
                        df = None
                else:
                    df = fetch_data(25.4, 81.8, time_slots)

                if df is not None:
                    df = validate_data(df)
                    df = df.iloc[:time_slots]
                    df["Hour"] = list(range(1, len(df) + 1))
                    # Ensure Max Grid exists in fetched data
                    if "Max Grid" not in df.columns:
                        df["Max Grid"] = config.get("grid_capacity", 100)

                    st.session_state.input_df = df
                    st.success(f"✅ Data loaded from {source}")

            except Exception as e:
                st.error(f"Error fetching data: {e}")

    # ===============================
    # EDITABLE TABLE (Column Filtering)
    # ===============================
    cols_to_show = ["Hour", "Demand"]
    if config.get("include_solar", True): cols_to_show.append("Max Solar")
    if config.get("include_wind", True): cols_to_show.append("Max Wind")
    if config.get("include_hydro", True): cols_to_show.append("Max Hydro")
    if config.get("include_grid", True): cols_to_show.append("Max Grid")

    display_df = st.session_state.input_df[cols_to_show]

    edited = st.data_editor(
        display_df,
        num_rows="fixed", # Keep hours consistent
        key="input_editor",
        use_container_width=True,
    )
    
    # Sync edits back
    st.session_state.input_df.update(edited)

    # ===============================
    # EXTRACT 5 ARRAYS & APPLY TOGGLES
    # ===============================
    demand = np.maximum(edited["Demand"].values.astype(float), 0)

    # Resource Arrays with Toggle Logic
    max_solar = np.maximum(edited["Max Solar"].values.astype(float), 0) if config.get("include_solar", True) else np.zeros(len(demand))
    max_wind = np.maximum(edited["Max Wind"].values.astype(float), 0) if config.get("include_wind", True) else np.zeros(len(demand))
    max_hydro = np.maximum(edited["Max Hydro"].values.astype(float), 0) if config.get("include_hydro", True) else np.zeros(len(demand))
    
    # Grid Logic
    if config.get("include_grid", True):
        # Allow user to edit Grid capacity per hour in the table
        max_grid = np.maximum(edited["Max Grid"].values.astype(float), 0)
    else:
        max_grid = np.zeros(len(demand))

    # CRITICAL: Return exactly 5 values to match app.py
    return demand, max_solar, max_wind, max_hydro, max_grid