"""Critical materials analysis metric stubs."""

from typing import Dict

import pandas as pd


def calculate_supply_concentration_hhi(df: pd.DataFrame) -> float:
    """Placeholder for Herfindahl-Hirschman concentration index."""
    if "market_share" not in df.columns:
        return 0.0
    return float((df["market_share"] ** 2).sum())


def calculate_import_dependency(df: pd.DataFrame) -> Dict[str, float]:
    """Placeholder import dependency metric."""
    if {"imports", "consumption"} - set(df.columns):
        return {"import_dependency": 0.0}
    consumption = float(df["consumption"].sum())
    imports = float(df["imports"].sum())
    return {"import_dependency": (imports / consumption) if consumption else 0.0}


def calculate_processing_bottleneck_score(df: pd.DataFrame) -> Dict[str, float]:
    """Placeholder bottleneck score metric."""
    if {"processing_capacity", "demand"} - set(df.columns):
        return {"bottleneck_score": 0.0}
    deficit = (df["demand"] - df["processing_capacity"]).clip(lower=0).sum()
    total_demand = df["demand"].sum()
    return {"bottleneck_score": float(deficit / total_demand) if total_demand else 0.0}

