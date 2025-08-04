# test.test_analysis_tools.py

import pandas as pd
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from utils.analysis_tools import calculate_average_total_infected, calculate_peak_infection, calculate_peak_infection_std

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