# main.py

from langgraph.graph import StateGraph, END
from agents.control_agent import ControlAgent
from agents.runner_agent import RunnerAgent
from agents.analyzer_agent import AnalyzerAgent

control = ControlAgent()
runner = RunnerAgent()
analyzer = AnalyzerAgent()

# Shared state
class State(dict): pass

def control_prompt_node(state):
    user_input = control.get_user_input()
    state["user_params"] = user_input
    return state, "run_sim"

def run_sim_node(state):
    params = state["user_params"]
    runner.run(params)
    return state, "notify_complete"

def notify_complete_node(state):
    control.notify_sim_complete()
    return state, "get_analysis_question"

def get_analysis_question_node(state):
    # Simulated input for now
    question = input("What would you like to analyze? ")
    state["user_question"] = question
    return state, "analyze"

def analyze_node(state):
    answer = analyzer.analyze(state["user_question"])
    print(f"\nAnalysis Result: {answer}")
    return state, END

# Build the graph
builder = StateGraph(State)
builder.add_node("control_prompt", control_prompt_node)
builder.add_node("run_sim", run_sim_node)
builder.add_node("notify_complete", notify_complete_node)
builder.add_node("get_analysis_question", get_analysis_question_node)
builder.add_node("analyze", analyze_node)

# Transitions
builder.set_entry_point("control_prompt")
builder.add_edge("control_prompt", "run_sim")
builder.add_edge("run_sim", "notify_complete")
builder.add_edge("notify_complete", "get_analysis_question")
builder.add_edge("get_analysis_question", "analyze")
builder.set_finish_point("analyze")

graph = builder.compile()

# Run it
graph.invoke(State())