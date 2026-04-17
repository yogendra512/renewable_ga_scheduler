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
    """
    Fetch solar radiation and wind speed from Open-Meteo.
    Returns solar (W/m²) and wind (m/s)
    """
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
        # fallback if API fails
        solar = np.random.uniform(0, 800, hours)
        wind = np.random.uniform(0, 15, hours)
        return solar, wind


def _generate_demand(hours: int) -> np.ndarray:
    """
    Generate realistic daily demand pattern.
    """
    demand = []
    for h in range(hours):
        if 0 <= h < 6:
            base = 40
        elif 6 <= h < 10:
            base = 80
        elif 10 <= h < 17:
            base = 60
        elif 17 <= h < 22:
            base = 100
        else:
            base = 50

        demand.append(base + np.random.uniform(-5, 5))

    return np.array(demand)


def _generate_hydro(hours: int) -> np.ndarray:
    """
    Hydro is mostly stable.
    """
    base = 50
    return np.array([base + np.random.uniform(-5, 5) for _ in range(hours)])


def fetch_data(
    latitude: float,
    longitude: float, 
    hours: int = 24,
) -> pd.DataFrame:
    """
    Main function used by UI.

    Returns DataFrame:
    Hour, Demand, Max Solar, Max Wind, Max Hydro
    """
    solar_raw, wind_raw = _fetch_weather(latitude, longitude, hours)

    # Convert to generation units
    max_solar = solar_raw / 10.0
    max_wind = wind_raw * 3.0

    demand = _generate_demand(hours)
    hydro = _generate_hydro(hours)

    df = pd.DataFrame({
        "Hour": list(range(1, hours + 1)),
        "Demand": demand,
        "Max Solar": max_solar,
        "Max Wind": max_wind,
        "Max Hydro": hydro,
    })

    return df