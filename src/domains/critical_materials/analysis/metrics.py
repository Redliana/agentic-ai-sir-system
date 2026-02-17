"""Critical materials analysis metrics."""

import pandas as pd


def _latest_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Use the latest monthly snapshot when temporal data is present."""
    if df.empty:
        return df
    if "month" in df.columns:
        month = pd.to_numeric(df["month"], errors="coerce").max()
        return df[pd.to_numeric(df["month"], errors="coerce") == month]
    if "step" in df.columns:
        step = pd.to_numeric(df["step"], errors="coerce").max()
        return df[pd.to_numeric(df["step"], errors="coerce") == step]
    return df


def _as_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0.0)


def calculate_supply_concentration_hhi(df: pd.DataFrame) -> float:
    """Calculate HHI from market-share data in the latest snapshot."""
    if df.empty:
        return 0.0

    snapshot = _latest_snapshot(df)
    if "market_share" in snapshot.columns:
        shares = _as_numeric(snapshot["market_share"])
        total = float(shares.sum())
        if total > 0:
            shares = shares / total
        return float((shares**2).sum())

    if "production" in snapshot.columns:
        production = _as_numeric(snapshot["production"])
        total = float(production.sum())
        if total <= 0:
            return 0.0
        shares = production / total
        return float((shares**2).sum())

    return 0.0


def calculate_import_dependency(df: pd.DataFrame) -> float:
    """Calculate import dependency as imports / consumption in latest snapshot."""
    if df.empty or {"imports", "consumption"} - set(df.columns):
        return 0.0
    snapshot = _latest_snapshot(df)
    consumption = float(_as_numeric(snapshot["consumption"]).sum())
    imports = float(_as_numeric(snapshot["imports"]).sum())
    return (imports / consumption) if consumption else 0.0


def calculate_processing_bottleneck_score(df: pd.DataFrame) -> float:
    """Calculate processing bottleneck as unmet demand ratio in latest snapshot."""
    if df.empty or {"processing_capacity", "demand"} - set(df.columns):
        return 0.0

    snapshot = _latest_snapshot(df)
    demand = _as_numeric(snapshot["demand"])
    capacity = _as_numeric(snapshot["processing_capacity"])
    total_demand = float(demand.sum())
    if total_demand <= 0:
        return 0.0

    unmet = float((demand - capacity).clip(lower=0).sum())
    return unmet / total_demand
