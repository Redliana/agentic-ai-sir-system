# test.test_analysis_tools.py

import pandas as pd
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from utils.analysis_tools import (
    calculate_average_total_infected, 
    calculate_peak_infection, 
    calculate_peak_infection_std,
    calculate_time_to_half_infected,
    calculate_recovery_rate_post_peak,
    calculate_reinfection_count,
    calculate_agents_never_recovered,
    calculate_final_state_distribution,
    plot_state_dynamics,
    calculate_infection_decline_rate
    )


# Load your simulation CSV
test_csv_path = "logs/all_agent_logs.csv"
df = pd.read_csv(test_csv_path)

# Run tests
print("📊 Data shape:", df.shape)

# Test 1: Average total infected
avg_total_infected = calculate_average_total_infected(df)
print("✅ Average Total Infected:", avg_total_infected)

# Test 2: Peak infection values
peak_infected, peak_step = calculate_peak_infection(df)
print("✅ Peak Infection:", peak_infected)
print("✅ Step of Peak Infection:", peak_step)

# Test 3: Std deviation of peak infections
std_result = calculate_peak_infection_std(df)
print("✅ Std Dev of Peak Infection:", std_result)

# Test 4 is a a plot - no testing required
plot_state_dynamics(df)

# Test 5: When outbreak is over
decline_result = calculate_infection_decline_rate(df)
print("✅ Infection Decline Rate:", decline_result)

# Test 6: Time to half infected
time_to_half = calculate_time_to_half_infected(df)
print("✅ Time to Half Infected:", time_to_half)

# Test 7: Recovery rate over time
recovery_rates= calculate_recovery_rate_post_peak(df)
print("✅ Recovery Rate Post Infection Peak:", recovery_rates)

# Test 8: Reinfected agent count
reinfected = calculate_reinfection_count(df)
print("✅ Avg Reinfected Agents:", reinfected)

# Test 9: Agents that never recovered
never_recovered = calculate_agents_never_recovered(df)
print("✅ Agents Never Recovered:", never_recovered)

# Test 10: Final state distribution
final_states = calculate_final_state_distribution(df)
print("✅ Final State Distribution:", final_states)