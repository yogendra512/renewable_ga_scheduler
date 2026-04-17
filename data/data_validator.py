"""
Validate and clean input data before GA processing.
"""
import pandas as pd

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset: Fill NaNs, clamp values, and smooth solar."""
    df = df.copy()

    # Fill missing values using forward fill, then zeros
    df = df.fillna(method="ffill").fillna(0)

    # Ensure Demand is at least 10 to avoid zero-division or unrealistic scenarios
    df["Demand"] = df["Demand"].clip(lower=10)

    # All generation columns must be non-negative
    for col in ["Max Solar", "Max Wind", "Max Hydro"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).clip(lower=0)

    # Smooth solar spikes for more realistic GA convergence
    df["Max Solar"] = df["Max Solar"].rolling(window=3, min_periods=1).mean()

    return df