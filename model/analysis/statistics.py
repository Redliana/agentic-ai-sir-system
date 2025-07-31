"""model.analysis.statistics.py"""

# Import libraries
import csv
from datetime import datetime
import numpy as np


def get_peak_sir_stats(logs):
    """Get peak values and times for S, I, and R for each run."""
    results = []

    for run_id, run in enumerate(logs):
        s_values = [entry[0] for entry in run]
        i_values = [entry[1] for entry in run]
        r_values = [entry[2] for entry in run]

        peak_num_s = max(s_values)
        peak_num_s_step = s_values.index(peak_num_s)

        peak_num_i = max(i_values)
        peak_num_i_step = i_values.index(peak_num_i)

        peak_num_r = max(r_values)
        peak_num_r_step = r_values.index(peak_num_r)

        results.append({
            "run_id": run_id,
            "num_peak_susceptible": peak_num_s,
            "peak_susceptible_step": peak_num_s_step,
            "num_peak_infected": peak_num_i,
            "peak_infected_step": peak_num_i_step,
            "num_peak_recovered": peak_num_r,
            "peak_recovered_step": peak_num_r_step,
        })

    return results

def save_peak_stats_to_db(stats, db):
    """
    Save peak stats to a database table.

    Args:
        stats (list[dict]): A list of dictionaries containing peak stats.
        db (Database): An instance of the Database class for database interaction.
    """
    try:
        for stat in stats:
            db.load_peak_stat(
                stat["run_id"],
                stat["num_peak_infected"],
                stat["peak_infected_step"],
                stat["num_peak_recovered"],
                stat["peak_recovered_step"],
                stat["num_peak_susceptible"],
                stat["peak_susceptible_step"],
            )
        db.commit()
        print("Peak stats successfully saved to the database.")
    except Exception as e:
        print(f"Error saving peak stats to the database: {e}")
