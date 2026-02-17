"""Critical materials analysis metrics for scenario run outputs."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _require_columns(df: pd.DataFrame, required: list[str]) -> bool:
    return not (set(required) - set(df.columns))


def _material_month_view(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse supplier-level logs to one row per material/month."""
    return (
        df.groupby(["run_id", "month", "material"], as_index=False)
        .agg(
            imports=("imports", "first"),
            consumption=("consumption", "first"),
            demand=("demand", "first"),
            effective_supply=("effective_supply", "sum"),
            supply_gap=("supply_gap", "first"),
        )
        .sort_values(["run_id", "month", "material"])
    )


def calculate_supply_concentration_hhi(df: pd.DataFrame) -> float:
    """Average Herfindahl-Hirschman Index (HHI) across material-month groups."""
    if not _require_columns(df, ["run_id", "month", "material", "market_share"]):
        return 0.0

    shares = df[["run_id", "month", "material", "market_share"]].copy()
    shares["market_share"] = pd.to_numeric(shares["market_share"], errors="coerce").fillna(0.0)
    if shares["market_share"].max() > 1.0:
        shares["market_share"] = shares["market_share"] / 100.0

    hhi_by_group = shares.groupby(["run_id", "month", "material"])["market_share"].apply(
        lambda s: float((s**2).sum()) * 10000.0
    )
    return round(float(hhi_by_group.mean()), 2) if len(hhi_by_group) else 0.0


def calculate_import_dependency(df: pd.DataFrame) -> float:
    """Average import dependency ratio = imports / consumption."""
    if not _require_columns(df, ["run_id", "month", "material", "imports", "consumption"]):
        return 0.0

    view = _material_month_view(df)
    consumption = view["consumption"].replace(0, np.nan)
    dependency = (view["imports"] / consumption).replace([np.inf, -np.inf], np.nan)
    return round(float(dependency.fillna(0.0).mean()), 4)


def calculate_processing_bottleneck_score(df: pd.DataFrame) -> float:
    """Average supply bottleneck score = max(demand - supply, 0) / demand."""
    if not _require_columns(
        df, ["run_id", "month", "material", "demand", "effective_supply", "supply_gap"]
    ):
        return 0.0

    view = _material_month_view(df)
    deficit = (view["demand"] - view["effective_supply"]).clip(lower=0.0)
    score = (deficit / view["demand"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    return round(float(score.fillna(0.0).mean()), 4)
