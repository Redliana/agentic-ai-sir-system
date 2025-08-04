# main_graph.py

# Import libraries
import sys

from langgraph.graph import StateGraph
from agents.ui_agent import UIAgent

from agents.model_agent import ModelAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.reporter_agent import ReporterAgent

# Initialize agents
interface = UIAgent()
runner = ModelAgent()
analyzer = AnalyzerAgent(logs_path="logs/all_agent_logs.csv")
reporter = ReporterAgent()

# Graph State
class State(dict): pass

def user_input_node(state: State):
    state["user_input"] = interface.get_user_input()
    state["user_intent"] = interface.classify_intent(state["user_input"])
    return state

def run_model_node(state: State):
    runner.run()
    print("[UI Agent]: Model completed.")
    return state

def ask_analysis_question_node(state: State):
    state["user_question"] = interface.ask_analysis_question()
    return state

def analyze_node(state: State):
    question = state["user_question"]
    result = analyzer.analyze(question)
    state["analysis_result"] = result
    return state

def report_node(state: State):
    question = state["user_question"]
    result = state["analysis_result"]
    response = reporter.report(question, result)
    print(f"[Report Agent]: {response}")
    return state

def fallback_node(state: State):
    print("\n[UI Agent]: Sorry, I didn't understand that. Try asking to 'run' a model or 'analyze' results.")
    return state

def route_by_intent(state: State) -> str:
    return state["user_intent"]

def exit_node(state: State):
    print("👋 Exiting the program. Goodbye!")
    sys.exit(0)

# Build LangGraph
graph_builder = StateGraph(State)

graph_builder.add_node("user_input", user_input_node)
graph_builder.add_node("run_model", run_model_node)
graph_builder.add_node("ask_analysis_question", ask_analysis_question_node)
graph_builder.add_node("analyze", analyze_node)
graph_builder.add_node("report", report_node)
graph_builder.add_node("fallback", fallback_node)
graph_builder.add_node("exit", exit_node)

# Entry
graph_builder.set_entry_point("user_input")


# Conditional routing using intent classifier
graph_builder.add_conditional_edges(
    "user_input",
    route_by_intent,
    {
        "run": "run_model",
        "analyze": "ask_analysis_question",
        "exit": "exit",
        "unknown": "fallback"
    }
)

# Define transitions
graph_builder.add_edge("run_model", "user_input")
graph_builder.add_edge("ask_analysis_question", "analyze")
graph_builder.add_edge("analyze", "report")
graph_builder.set_finish_point("report")

graph_builder.set_entry_point("user_input")

graph = graph_builder.compile()

if __name__ == "__main__":
    graph.invoke(State())

