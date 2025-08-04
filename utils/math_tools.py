# utils/math_tools.py

from collections import defaultdict

def calculate_peak_infection(data: list[dict]) -> str:
    """
    Returns the step with the highest number of infected agents.
    """
    infected_counts = defaultdict(int)

    for row in data:
        if row.get("state") == "I":
            key = (row.get("run_id"), row.get("step"))
            infected_counts[key] += 1

    if not infected_counts:
        return "No infected agents found."

    # Find step with max infections
    peak = max(infected_counts.items(), key=lambda x: x[1])
    run_id, step = peak[0]
    count = peak[1]

    return f"Peak infection occurred at step {step} of run {run_id} with {count} infected agents."
