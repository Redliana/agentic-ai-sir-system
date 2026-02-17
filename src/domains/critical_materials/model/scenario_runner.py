"""Scenario runner MVP for critical materials workflows."""

from __future__ import annotations

import os
import random
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from domains.critical_materials.ingestion.structured_ingest import load_structured_dataframe


def _prepare_params(params: Dict[str, Any]) -> Dict[str, Any]:
    defaults = {
        "seed": 42,
        "time_horizon_months": 24,
        "demand_growth_rate": 0.08,
        "processing_disruption_pct": 0.15,
        "substitution_factor": 0.10,
        "run_id": 0,
        "output_path": "src/logs/critical_materials_runs.csv",
    }
    merged = defaults.copy()
    merged.update(params or {})
    return merged


def _simulate_month_rows(
    base_df: pd.DataFrame,
    month: int,
    demand_growth_rate: float,
    processing_disruption_pct: float,
    substitution_factor: float,
    run_id: int,
) -> List[Dict[str, Any]]:
    monthly_rows: List[Dict[str, Any]] = []

    # Recovery improves linearly to represent adaptation in supply chains.
    horizon_recovery_factor = max(0.0, 1.0 - ((month - 1) * 0.04))
    month_disruption = max(0.0, processing_disruption_pct * horizon_recovery_factor)

    for material, group in base_df.groupby("material"):
        baseline_demand = float(group["baseline_demand"].mean())
        material_imports = float(group["imports"].mean())
        demand = baseline_demand * ((1.0 + demand_growth_rate) ** month)
        adjusted_demand = demand * max(0.0, 1.0 - substitution_factor)

        supplier_supply = []
        for _, row in group.iterrows():
            capacity_effective = float(row["processing_capacity"]) * (1.0 - month_disruption)
            stochastic_multiplier = max(0.7, min(1.3, random.gauss(1.0, 0.06)))
            unconstrained_supply = float(row["supply_volume"]) * stochastic_multiplier
            effective_supply = max(0.0, min(unconstrained_supply, capacity_effective))
            supplier_supply.append((row, capacity_effective, effective_supply))

        total_supply = sum(item[2] for item in supplier_supply)
        supply_gap = max(0.0, adjusted_demand - total_supply)

        for row, capacity_effective, effective_supply in supplier_supply:
            market_share = (effective_supply / total_supply) if total_supply > 0 else 0.0
            monthly_rows.append(
                {
                    "run_id": run_id,
                    "month": month,
                    "material": material,
                    "supplier": row["supplier"],
                    "country": row["country"],
                    "market_share": round(market_share, 6),
                    "imports": round(material_imports, 4),
                    "consumption": round(adjusted_demand, 4),
                    "processing_capacity": round(capacity_effective, 4),
                    "demand": round(adjusted_demand, 4),
                    "effective_supply": round(effective_supply, 4),
                    "supply_gap": round(supply_gap, 4),
                    "processing_disruption_pct": round(month_disruption, 4),
                    "substitution_factor": round(substitution_factor, 4),
                }
            )

    return monthly_rows


def run_scenario(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a critical-materials scenario and persist monthly run logs."""
    cfg = _prepare_params(params)

    random.seed(int(cfg["seed"]))
    np.random.seed(int(cfg["seed"]))

    base_df = load_structured_dataframe(cfg)
    all_rows: List[Dict[str, Any]] = []

    for month in range(1, int(cfg["time_horizon_months"]) + 1):
        all_rows.extend(
            _simulate_month_rows(
                base_df=base_df,
                month=month,
                demand_growth_rate=float(cfg["demand_growth_rate"]),
                processing_disruption_pct=float(cfg["processing_disruption_pct"]),
                substitution_factor=float(cfg["substitution_factor"]),
                run_id=int(cfg["run_id"]),
            )
        )

    run_df = pd.DataFrame(all_rows)
    output_path = cfg["output_path"]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    run_df.to_csv(output_path, index=False)

    return {
        "status": "completed",
        "rows": int(len(run_df)),
        "materials": sorted(run_df["material"].unique().tolist()),
        "months": int(cfg["time_horizon_months"]),
        "output_path": output_path,
    }
