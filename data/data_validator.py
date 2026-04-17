"""
Validate and clean input data before GA processing.
"""

import pandas as pd


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dataset:
    - Fill NaNs
    - Clamp values
    - Smooth solar
    """
    df = df.copy()

    # Fill missing values
    df = df.fillna(method="ffill").fillna(0)

    # Ensure valid ranges
    df["Demand"] = df["Demand"].clip(lower=10)

    for col in ["Max Solar", "Max Wind", "Max Hydro"]:
        df[col] = df[col].clip(lower=0)

    # Smooth solar spikes
    df["Max Solar"] = df["Max Solar"].rolling(
        window=3, min_periods=1
    ).mean()

    return df