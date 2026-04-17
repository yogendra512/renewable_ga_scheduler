"""
Fetch renewable energy data using Open-Meteo API (free, no API key).
Falls back to synthetic data if API fails.
"""

from typing import Tuple
import requests
import pandas as pd
import numpy as np

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def _fetch_weather(latitude: float, longitude: float, hours: int) -> Tuple[np.ndarray, np.ndarray]:
    """Fetch solar radiation and wind speed from Open-Meteo."""
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "shortwave_radiation,wind_speed_10m",
            "forecast_days": 2,
        }
        res = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()["hourly"]

        solar = np.array(data["shortwave_radiation"][:hours])
        wind = np.array(data["wind_speed_10m"][:hours])
        return solar, wind
    except Exception:
        # Fallback if API fails
        solar = np.random.uniform(0, 800, hours)
        wind = np.random.uniform(0, 15, hours)
        return solar, wind

def _generate_demand(hours: int) -> np.ndarray:
    """Generate realistic daily demand pattern using modulo for multi-day support."""
    demand = []
    for h in range(hours):
        hour_of_day = h % 24  # Modulo fix for simulations > 24h
        if 0 <= hour_of_day < 6:
            base = 40
        elif 6 <= hour_of_day < 10:
            base = 80
        elif 10 <= hour_of_day < 17:
            base = 60
        elif 17 <= hour_of_day < 22:
            base = 100
        else:
            base = 50
        demand.append(base + np.random.uniform(-5, 5))
    return np.array(demand)

def fetch_data(latitude: float, longitude: float, hours: int = 24, is_live: bool = False) -> pd.DataFrame:
    """Main function to return a cleaned DataFrame for the UI."""
    solar_raw, wind_raw = _fetch_weather(latitude, longitude, hours)

    # Convert to generation units and apply clipping/rounding
    max_solar = np.clip(solar_raw / 10.0, 0, None).round(1)
    max_wind = np.clip(wind_raw * 3.0, 0, None).round(1)

    demand = _generate_demand(hours).round(1)
    # Hydro is stable: base 50 units with slight variance
    hydro = (np.full(hours, 50.0) + np.random.uniform(-2, 2, hours)).round(1)

    df = pd.DataFrame({
        "Hour": list(range(1, hours + 1)),
        "Demand": demand,
        "Max Solar": max_solar,
        "Max Wind": max_wind,
        "Max Hydro": hydro,
    })
    return df