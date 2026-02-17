"""Structured ingestion utilities for critical materials datasets."""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "material",
    "supplier",
    "country",
    "market_share",
    "processing_capacity",
    "baseline_demand",
    "imports",
    "consumption",
    "supply_volume",
]

NUMERIC_COLUMNS = [
    "market_share",
    "processing_capacity",
    "baseline_demand",
    "imports",
    "consumption",
    "supply_volume",
]


def _default_rows() -> List[Dict[str, Any]]:
    return [
        {
            "material": "lithium",
            "supplier": "AndesExtract",
            "country": "Chile",
            "market_share": 0.34,
            "processing_capacity": 120.0,
            "baseline_demand": 290.0,
            "imports": 180.0,
            "consumption": 290.0,
            "supply_volume": 105.0,
        },
        {
            "material": "lithium",
            "supplier": "AUSHardRock",
            "country": "Australia",
            "market_share": 0.31,
            "processing_capacity": 110.0,
            "baseline_demand": 290.0,
            "imports": 180.0,
            "consumption": 290.0,
            "supply_volume": 95.0,
        },
        {
            "material": "lithium",
            "supplier": "CNRefine",
            "country": "China",
            "market_share": 0.35,
            "processing_capacity": 140.0,
            "baseline_demand": 290.0,
            "imports": 180.0,
            "consumption": 290.0,
            "supply_volume": 110.0,
        },
        {
            "material": "nickel",
            "supplier": "IndoNickel",
            "country": "Indonesia",
            "market_share": 0.52,
            "processing_capacity": 180.0,
            "baseline_demand": 260.0,
            "imports": 140.0,
            "consumption": 260.0,
            "supply_volume": 135.0,
        },
        {
            "material": "nickel",
            "supplier": "PHSmelter",
            "country": "Philippines",
            "market_share": 0.19,
            "processing_capacity": 65.0,
            "baseline_demand": 260.0,
            "imports": 140.0,
            "consumption": 260.0,
            "supply_volume": 50.0,
        },
        {
            "material": "nickel",
            "supplier": "CNRefine",
            "country": "China",
            "market_share": 0.29,
            "processing_capacity": 100.0,
            "baseline_demand": 260.0,
            "imports": 140.0,
            "consumption": 260.0,
            "supply_volume": 75.0,
        },
        {
            "material": "cobalt",
            "supplier": "DRCMine",
            "country": "Democratic Republic of the Congo",
            "market_share": 0.63,
            "processing_capacity": 150.0,
            "baseline_demand": 210.0,
            "imports": 130.0,
            "consumption": 210.0,
            "supply_volume": 120.0,
        },
        {
            "material": "cobalt",
            "supplier": "AUSCobalt",
            "country": "Australia",
            "market_share": 0.14,
            "processing_capacity": 35.0,
            "baseline_demand": 210.0,
            "imports": 130.0,
            "consumption": 210.0,
            "supply_volume": 25.0,
        },
        {
            "material": "cobalt",
            "supplier": "CNRefine",
            "country": "China",
            "market_share": 0.23,
            "processing_capacity": 80.0,
            "baseline_demand": 210.0,
            "imports": 130.0,
            "consumption": 210.0,
            "supply_volume": 45.0,
        },
    ]


def _coerce_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0).clip(lower=0.0)
    return df


def _normalize_market_share(df: pd.DataFrame) -> pd.DataFrame:
    totals = df.groupby("material")["market_share"].transform("sum")
    counts = df.groupby("material")["market_share"].transform("size")
    df["market_share"] = np.where(
        totals <= 0,
        1.0 / counts.replace(0, np.nan),
        df["market_share"] / totals.replace(0, np.nan),
    )
    df["market_share"] = df["market_share"].fillna(0.0)
    return df


def load_structured_dataframe(config: Dict[str, Any] | None = None) -> pd.DataFrame:
    """Load and normalize baseline structured data from file or defaults."""
    cfg = config or {}
    baseline_path = cfg.get("baseline_csv_path")
    if baseline_path and os.path.exists(baseline_path):
        df = pd.read_csv(baseline_path)
        source = "file"
    else:
        df = pd.DataFrame(_default_rows())
        source = "default"

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = 0.0 if col in NUMERIC_COLUMNS else "unknown"

    df = df[REQUIRED_COLUMNS].copy()
    df = _coerce_numeric(df, NUMERIC_COLUMNS)
    df["material"] = df["material"].astype(str).str.strip().str.lower()
    df["supplier"] = df["supplier"].astype(str).str.strip()
    df["country"] = df["country"].astype(str).str.strip()

    # Fill missing operational fields with conservative defaults.
    if np.isclose(df["supply_volume"].sum(), 0.0):
        df["supply_volume"] = df["processing_capacity"] * 0.75
    if np.isclose(df["consumption"].sum(), 0.0):
        df["consumption"] = df["baseline_demand"]
    if np.isclose(df["imports"].sum(), 0.0):
        df["imports"] = df["consumption"] * 0.5

    df = _normalize_market_share(df)
    df.attrs["source"] = source
    return df.reset_index(drop=True)


def ingest_structured_sources(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Normalize and persist structured input data for critical material scenarios."""
    cfg = config or {}
    output_path = cfg.get(
        "normalized_output_path", "src/data/critical_materials/normalized_baseline.csv"
    )

    df = load_structured_dataframe(cfg)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    return {
        "status": "ok",
        "source": df.attrs.get("source", "unknown"),
        "rows": int(len(df)),
        "materials": sorted(df["material"].unique().tolist()),
        "output_path": output_path,
    }
