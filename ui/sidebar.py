# ui/sidebar.py — Sidebar inputs and configuration
import streamlit as st


def render_sidebar() -> dict:
    """
    Render sidebar controls and return all configuration as a dict.
    Includes User Type toggle (Basic/Advanced) and Resource Availability.
    """

    # ===============================
    # 👤 USER MODE SECTION
    # ===============================
    st.sidebar.header("👤 User Settings")
    user_mode = st.sidebar.radio(
        "Select Experience Level",
        ["Basic", "Advanced"],
        help="Basic mode hides complex technical settings for a simpler experience."
    )

    # ===============================
    # 🌐 DATA SOURCE SECTION
    # ===============================
    st.sidebar.header("🌐 Data Source")

    data_source = st.sidebar.selectbox(
        "Select Data Source",
        ["Manual", "Live Weather API", "MQTT Sensors", "CSV Upload"],
        key="data_source_select"
    )

    config = {
        "data_source": data_source,
        "user_mode": user_mode
    }

    if data_source == "Live Weather API":
        config["latitude"] = st.sidebar.number_input(
            "Latitude", value=25.4, key="latitude_input"
        )
        config["longitude"] = st.sidebar.number_input(
            "Longitude", value=81.8, key="longitude_input"
        )
    elif data_source == "CSV Upload":
        config["csv_file"] = st.sidebar.file_uploader(
            "Upload CSV", type=["csv"], key="csv_uploader"
        )

    # ===============================
    # 🔌 RESOURCE AVAILABILITY (NEW)
    # ===============================
    st.sidebar.header("🔌 Available Resources")
    st.sidebar.caption("Toggle which resources are available at your location.")
    config["include_solar"] = st.sidebar.toggle("Include Solar", value=True, key="inc_solar")
    config["include_wind"] = st.sidebar.toggle("Include Wind", value=True, key="inc_wind")
    config["include_hydro"] = st.sidebar.toggle("Include Hydro", value=True, key="inc_hydro")

    # ===============================
    # ⚙️ SIMULATION INPUTS
    # ===============================
    st.sidebar.header("⚙️ Simulation Inputs")

    time_slots = st.sidebar.number_input(
        "Number of Hours (Time Slots)",
        min_value=3, max_value=48, value=12,
        key="time_slots_input",
        help="How many hours ahead should the GA optimize?"
    )

    # --- Battery Settings ---
    st.sidebar.subheader("🔋 Battery Settings")
    battery_capacity = st.sidebar.number_input(
        "Capacity (units)", min_value=10, max_value=1000, value=100, step=10,
        key="battery_capacity"
    )

    # Advanced battery settings hidden in Basic mode
    if user_mode == "Advanced":
        initial_soc = st.sidebar.number_input(
            "Initial SOC (units)", min_value=0, max_value=int(battery_capacity), value=50,
            key="initial_soc"
        )
        max_charge = st.sidebar.number_input(
            "Max Charge/Hour", min_value=1, max_value=500, value=20,
            key="max_charge"
        )
        max_discharge = st.sidebar.number_input(
            "Max Discharge/Hour", min_value=1, max_value=500, value=20,
            key="max_discharge"
        )
    else:
        # Defaults for Basic mode
        initial_soc = 50
        max_charge = 20
        max_discharge = 20

    # --- GA Settings (Hidden in Basic Mode) ---
    if user_mode == "Advanced":
        st.sidebar.subheader("🧬 Genetic Algorithm Settings")
        pop_size = st.sidebar.number_input(
            "Population Size", min_value=10, max_value=500, value=60, key="pop_size"
        )
        generations = st.sidebar.number_input(
            "Generations", min_value=10, max_value=1000, value=200, key="generations"
        )
        mutation_rate = st.sidebar.slider(
            "Mutation Rate", min_value=0.0, max_value=0.5, value=0.12, key="mutation_rate"
        )
        elitism_frac = st.sidebar.slider(
            "Elitism Fraction", min_value=0.0, max_value=0.5, value=0.2, key="elitism_frac"
        )
    else:
        # Defaults for Basic mode
        pop_size = 60
        generations = 200
        mutation_rate = 0.12
        elitism_frac = 0.2

    # ===============================
    # FINAL CONFIG UPDATE
    # ===============================
    config.update({
        "time_slots": int(time_slots),
        "battery_capacity": float(battery_capacity),
        "initial_soc": float(initial_soc),
        "max_charge": float(max_charge),
        "max_discharge": float(max_discharge),
        "pop_size": int(pop_size),
        "generations": int(generations),
        "mutation_rate": float(mutation_rate),
        "elitism_frac": float(elitism_frac),
    })

    return config