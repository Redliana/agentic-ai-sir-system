"""Scenario runner for critical materials supply-chain workflows."""

import csv
import os
import random
from typing import Any, Dict, List


DEFAULT_OUTPUT_PATH = os.path.join("src", "logs", "critical_materials_runs.csv")
COUNTRY_PROFILES = (
    {
        "country": "Country_A",
        "supply_share": 0.48,
        "consumption_share": 0.30,
        "shock_sensitive": True,
    },
    {
        "country": "Country_B",
        "supply_share": 0.34,
        "consumption_share": 0.40,
        "shock_sensitive": False,
    },
    {
        "country": "Country_C",
        "supply_share": 0.18,
        "consumption_share": 0.30,
        "shock_sensitive": False,
    },
)


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _build_month_rows(
    month: int,
    material: str,
    demand: float,
    disruption_pct: float,
    shock_start_month: int,
    substitution_factor: float,
    rng: random.Random,
) -> List[Dict[str, Any]]:
    disruption_applied = month >= shock_start_month
    effective_disruption = disruption_pct if disruption_applied else 0.0

    # Allow substitution to offset part of disruption-induced demand pressure.
    demand_adjustment = 1.0 - (substitution_factor * effective_disruption)
    adjusted_demand = max(demand * demand_adjustment, 0.0)

    supply_by_country = {}
    total_supply = 0.0
    for profile in COUNTRY_PROFILES:
        jitter = rng.uniform(-0.03, 0.03)
        base_supply = adjusted_demand * profile["supply_share"] * (1.0 + jitter)
        if profile["shock_sensitive"]:
            base_supply *= 1.0 - effective_disruption
        supply = max(base_supply, 0.0)
        supply_by_country[profile["country"]] = supply
        total_supply += supply

    rows = []
    for profile in COUNTRY_PROFILES:
        country = profile["country"]
        production = supply_by_country[country]
        processing_capacity = production * (0.97 if profile["shock_sensitive"] else 1.03)
        consumption = adjusted_demand * profile["consumption_share"]
        imports = max(consumption - production, 0.0)
        market_share = (production / total_supply) if total_supply else 0.0

        rows.append(
            {
                "run_id": 0,
                "month": month,
                "material": material,
                "country": country,
                "production": round(production, 4),
                "processing_capacity": round(processing_capacity, 4),
                "demand": round(consumption, 4),
                "consumption": round(consumption, 4),
                "imports": round(imports, 4),
                "market_share": round(market_share, 6),
                "disruption_applied": int(disruption_applied),
            }
        )

    return rows


def run_scenario(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a deterministic monthly critical-materials scenario output."""
    params = params or {}

    seed = _as_int(params.get("seed"), 42)
    months = max(1, _as_int(params.get("time_horizon_months"), 24))
    growth_rate = _as_float(params.get("demand_growth_rate"), 0.08)
    disruption_pct = _clamp(_as_float(params.get("processing_disruption_pct"), 0.15), 0.0, 0.95)
    substitution_factor = _clamp(_as_float(params.get("substitution_factor"), 0.10), 0.0, 1.0)
    base_demand = max(1.0, _as_float(params.get("base_demand_tonnes"), 100000.0))
    material = str(params.get("material") or "graphite")
    output_path = str(params.get("output_path") or DEFAULT_OUTPUT_PATH)

    rng = random.Random(seed)
    shock_start_month = max(1, months // 3)

    rows: List[Dict[str, Any]] = []
    for month in range(months):
        demand = base_demand * ((1.0 + growth_rate) ** month)
        rows.extend(
            _build_month_rows(
                month=month,
                material=material,
                demand=demand,
                disruption_pct=disruption_pct,
                shock_start_month=shock_start_month,
                substitution_factor=substitution_factor,
                rng=rng,
            )
        )

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return {
        "status": "ok",
        "output_path": output_path,
        "rows_written": len(rows),
        "months": months,
        "material": material,
        "shock_start_month": shock_start_month,
    }
