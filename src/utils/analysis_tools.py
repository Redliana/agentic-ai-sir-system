"""Compatibility wrapper for SIR analysis metrics.

The canonical implementation now lives at ``domains.sir.analysis.metrics``.
"""

from domains.sir.analysis.metrics import (
    calculate_agents_never_recovered,
    calculate_average_total_infected,
    calculate_final_state_distribution,
    calculate_infection_decline_rate,
    calculate_infection_decrease_after_step,
    calculate_peak_infection,
    calculate_peak_infection_std,
    calculate_recovery_rate_post_peak,
    calculate_reinfection_count,
    calculate_time_to_half_infected,
    plot_state_dynamics,
)

__all__ = [
    "calculate_average_total_infected",
    "calculate_peak_infection",
    "calculate_peak_infection_std",
    "plot_state_dynamics",
    "calculate_infection_decline_rate",
    "calculate_time_to_half_infected",
    "calculate_recovery_rate_post_peak",
    "calculate_reinfection_count",
    "calculate_agents_never_recovered",
    "calculate_final_state_distribution",
    "calculate_infection_decrease_after_step",
]

