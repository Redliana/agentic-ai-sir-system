# test.test_analyzer_agent.py

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from agents.analyzer_agent import AnalyzerAgent

if __name__ == "__main__":
    # ✅ Path to your infection logs
    logs_path = "logs/all_agent_logs.csv"

    # ✅ Instantiate the agent
    analyzer = AnalyzerAgent(logs_path)

    # ✅ Try some analysis questions
    test_questions = [
        "How many agents were infected?",
        "What was the peak infection?",
        "What is the standard deviation of peak infected individuals?"
    ]

    for question in test_questions:
        print(f"\n🧠 Question: {question}")
        result = analyzer.analyze(question)
        print("✅ Result:", result)
