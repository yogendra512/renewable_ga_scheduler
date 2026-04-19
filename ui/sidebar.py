# ui/sidebar.py — Sidebar with System Architecture Selector for India
import streamlit as st


def render_sidebar() -> dict:
    """
    Render sidebar controls and return configuration.
    Dynamically adapts to Standard On-Grid, Hybrid, and Off-Grid systems.
    """

    # ===============================
    # 🏗️ SYSTEM ARCHITECTURE (NEW)
    # ===============================
    st.sidebar.header("🏗️ System Architecture")
    system_type = st.sidebar.selectbox(
        "Select System Type",
        ["Hybrid (On-Grid + Battery)", "Standard On-Grid (No Battery)", "Off-Grid (Standalone)"],
        index=0,
        help="Hybrid: Sells excess & has backup. Standard: Bill reduction only. Off-Grid: Remote sites."
    )

    # ===============================
    # 👤 USER MODE SECTION
    # ===============================
    st.sidebar.header("👤 User Settings")
    user_mode = st.sidebar.radio(
        "Select Experience Level",
        ["Basic", "Advanced"],
        help="Basic mode hides complex technical settings."
    )

    # Initialize config
    config = {
        "system_type": system_type,
        "user_mode": user_mode
    }

    # ===============================
    # 🌐 DATA SOURCE SECTION
    # ===============================
    st.sidebar.header("🌐 Data Source")
    data_source = st.sidebar.selectbox(
        "Select Data Source",
        ["Manual", "Live Weather API", "MQTT Sensors", "CSV Upload"]
    )
    config["data_source"] = data_source

    if data_source == "Live Weather API":
        config["latitude"] = st.sidebar.number_input("Latitude", value=25.4)
        config["longitude"] = st.sidebar.number_input("Longitude", value=81.8)
    elif data_source == "CSV Upload":
        config["csv_file"] = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    # ===============================
    # 🇮🇳 INDIAN GRID & NET METERING
    # ===============================
    # Hide these options if the system is "Off-Grid"
    if system_type != "Off-Grid (Standalone)":
        st.sidebar.header("🇮🇳 Indian Grid Settings")
        
        config["net_metering"] = st.sidebar.toggle("Enable Net Metering", value=True)

        col1, col2 = st.sidebar.columns(2)
        with col1:
            config["import_price"] = st.sidebar.number_input("Buy (₹/unit)", value=7.5, step=0.1)
        with col2:
            config["export_price"] = st.sidebar.number_input("Sell (₹/unit)", value=3.5, step=0.1)

        config["grid_available"] = st.sidebar.toggle("Grid Available (No Power Cut)", value=True)
        config["grid_capacity"] = 100 if config["grid_available"] else 0
    else:
        # Defaults for Off-Grid
        config["net_metering"] = False
        config["import_price"] = 0.0
        config["export_price"] = 0.0
        config["grid_capacity"] = 0

    # ===============================
    # 🔌 RESOURCE AVAILABILITY
    # ===============================
    st.sidebar.header("🔌 Available Resources")
    config["include_solar"] = st.sidebar.toggle("Include Solar", value=True)
    config["include_wind"] = st.sidebar.toggle("Include Wind", value=True)
    config["include_hydro"] = st.sidebar.toggle("Include Hydro", value=True)

    # ===============================
    # ⚙️ SIMULATION & BATTERY
    # ===============================
    st.sidebar.header("⚙️ Simulation Inputs")
    time_slots = st.sidebar.number_input("Number of Hours", 3, 48, 12)

    # --- Battery Settings (Hidden for Standard On-Grid) ---
    if system_type != "Standard On-Grid (No Battery)":
        st.sidebar.subheader("🔋 Battery Settings")
        battery_capacity = st.sidebar.number_input("Capacity (units)", 10, 1000, 100, step=10)
        
        if user_mode == "Advanced":
            initial_soc = st.sidebar.number_input("Initial SOC", 0, int(battery_capacity), 50)
            max_charge = st.sidebar.number_input("Max Charge/Hr", 1, 500, 20)
            max_discharge = st.sidebar.number_input("Max Discharge/Hr", 1, 500, 20)
        else:
            initial_soc, max_charge, max_discharge = 50, 20, 20
    else:
        # Defaults for systems with no battery
        battery_capacity, initial_soc, max_charge, max_discharge = 0, 0, 0, 0

    # --- GA Settings ---
    if user_mode == "Advanced":
        st.sidebar.subheader("🧬 GA Settings")
        pop_size = st.sidebar.number_input("Pop Size", 10, 500, 60)
        generations = st.sidebar.number_input("Generations", 10, 1000, 200)
        mutation_rate = st.sidebar.slider("Mutation", 0.0, 0.5, 0.12)
        elitism_frac = st.sidebar.slider("Elitism", 0.0, 0.5, 0.2)
    else:
        pop_size, generations, mutation_rate, elitism_frac = 60, 200, 0.12, 0.2

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